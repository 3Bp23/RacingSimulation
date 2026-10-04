import numpy as np
import random
import copy
from racer import Racer, RacerProfile
from physics import RacePhysics

# Desired finishes
FINISH_CLOSE = "close"
FINISH_NORMAL = "normal"
FINISH_DOMINANT = "dominant"

class OutcomePlanner:
    def __init__(self, racers, desired_winner_id, desired_finish=FINISH_NORMAL):
        """
        racers: List of Racer instances with base parameters already set.
        desired_winner_id: The ID of the racer we want to win.
        desired_finish: String representing how close the race should be.
        """
        self.base_racers = racers
        self.winner_id = desired_winner_id
        self.desired_finish = desired_finish

    def generate_random_racer_variant(self, racer):
        """
        Creates a slightly mutated copy of a racer, keeping them within their
        elasticity envelope.
        """
        new_racer = copy.deepcopy(racer)

        # Base stats variance (tight bounds)
        new_racer.base_speed = racer.base_speed * np.random.uniform(0.98, 1.02)
        new_racer.power = racer.power * np.random.uniform(0.90, 1.10)
        new_racer.max_stamina = racer.max_stamina * np.random.uniform(0.95, 1.05)
        new_racer.stamina = new_racer.max_stamina

        # Tactical curve variance
        new_racer.profile_params['amplitude'] = racer.profile_params.get('amplitude', 1.0) * np.random.uniform(0.8, 1.2)

        # Shift timings slightly
        shift = np.random.uniform(-0.02, 0.02)
        new_racer.profile_params['start'] = max(0.0, racer.profile_params.get('start', 0.2) + shift)
        new_racer.profile_params['peak'] = min(0.9, max(0.1, racer.profile_params.get('peak', 0.5) + shift))
        new_racer.profile_params['end'] = min(0.95, racer.profile_params.get('end', 0.8) + shift)

        return new_racer

    def evaluate_race(self, racers_list):
        """
        Simulates a race with the given racers, returns loss and simulated data.
        """
        phys = RacePhysics(racers_list)

        v_dict = {}
        s_dict = {}

        for r in racers_list:
            v_p, s_p = phys.generate_velocity_curve(r)
            v_dict[r.racer_id] = v_p
            s_dict[r.racer_id] = s_p

        t_anim, p_anim = phys.integrate_trajectories(v_dict)

        # Determine finish times
        finish_times = {}
        for r in racers_list:
            # Time to reach p=1.0. We check the index where p >= 1.0
            p_array = p_anim[r.racer_id]
            idx = np.searchsorted(p_array, 1.0)
            if idx < len(t_anim):
                finish_times[r.racer_id] = t_anim[idx]
            else:
                finish_times[r.racer_id] = t_anim[-1] # fallback

        # Sort by finish time
        sorted_results = sorted(finish_times.items(), key=lambda x: x[1])
        actual_winner_id = sorted_results[0][0]

        # Calculate loss
        loss = 0.0

        # 1. Winner constraint
        if actual_winner_id != self.winner_id:
            loss += 1000.0  # Heavy penalty for wrong winner
            # Add gap from actual winner to desired winner as gradient
            loss += (finish_times[self.winner_id] - sorted_results[0][1]) * 10.0

        # 2. Finish gap constraint
        gap_to_second = sorted_results[1][1] - sorted_results[0][1]

        target_gap = 0.5 # Normal
        if self.desired_finish == FINISH_CLOSE:
            target_gap = 0.1
        elif self.desired_finish == FINISH_DOMINANT:
            target_gap = 2.0

        loss += abs(gap_to_second - target_gap) * 50.0

        # 3. Overtaking and Dynamic spread
        # We want changing race order.
        order_changes = 0
        spreads = []
        for i in range(0, len(t_anim), len(t_anim)//10): # Sample 10 points
            pos_at_t = [p_anim[r.racer_id][i] for r in racers_list]
            spreads.append(np.std(pos_at_t))

        # Penalize zero spread or too much spread
        mean_spread = np.mean(spreads)
        loss += abs(mean_spread - 0.05) * 100.0

        # 4. Stamina health
        for r in racers_list:
            final_stamina = s_dict[r.racer_id][-1]
            if final_stamina < 0:
                loss += abs(final_stamina) * 100.0 # Heavy penalty for negative stamina

        return loss, finish_times, t_anim, p_anim, v_dict, s_dict

    def optimize(self, iterations=50):
        """
        Simple evolutionary/random search to find a valid race configuration.
        """
        best_loss = float('inf')
        best_racers = None
        best_data = None

        for _ in range(iterations):
            candidate_racers = [self.generate_random_racer_variant(r) for r in self.base_racers]

            # Optionally, slightly boost the desired winner to guide search
            for r in candidate_racers:
                if r.racer_id == self.winner_id:
                    r.base_speed *= 1.01
                    r.max_stamina *= 1.02
                    r.stamina = r.max_stamina

            loss, finish_times, t_anim, p_anim, v_dict, s_dict = self.evaluate_race(candidate_racers)

            if loss < best_loss:
                best_loss = loss
                best_racers = candidate_racers
                best_data = {
                    'finish_times': finish_times,
                    't_anim': t_anim,
                    'p_anim': p_anim,
                    'v_dict': v_dict,
                    's_dict': s_dict
                }

        return best_racers, best_data
