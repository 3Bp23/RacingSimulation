import numpy as np
import time
from racer import Racer, RacerProfile
from planner import OutcomePlanner, FINISH_CLOSE, FINISH_NORMAL, FINISH_DOMINANT

def generate_base_field(num_racers=10):
    """
    Generates a mixed field of 10 racers.
    """
    profiles = [RacerProfile.FRONT_RUNNER, RacerProfile.PACER, RacerProfile.LATE_SURGER]
    racers = []

    for i in range(1, num_racers + 1):
        ptype = profiles[i % len(profiles)]

        # Base population variance
        speed = 10.0 + np.random.uniform(-0.1, 0.1)
        power = 5.0 + np.random.uniform(-0.5, 0.5)
        stamina = 150.0 + np.random.uniform(-10.0, 10.0)

        # Profile variance
        amp = np.random.uniform(0.8, 1.2)

        if ptype == RacerProfile.FRONT_RUNNER:
            params = {'amplitude': amp, 'start': 0.05, 'peak': 0.20, 'end': 0.60}
        elif ptype == RacerProfile.PACER:
            params = {'amplitude': amp, 'start': 0.20, 'peak': 0.50, 'end': 0.80}
        else:
            params = {'amplitude': amp, 'start': 0.40, 'peak': 0.70, 'end': 0.85}

        r = Racer(i, ptype, speed, power, stamina, params)
        racers.append(r)

    return racers

def run_monte_carlo(num_races=100):
    stats = {
        'winner_counts': {},
        'profile_wins': {RacerProfile.FRONT_RUNNER: 0, RacerProfile.PACER: 0, RacerProfile.LATE_SURGER: 0},
        'avg_gaps': [],
        'negative_stamina_count': 0
    }

    finishes = [FINISH_NORMAL, FINISH_CLOSE, FINISH_DOMINANT]

    start_time = time.time()
    for i in range(num_races):
        racers = generate_base_field(10)
        desired_winner = np.random.choice([r.racer_id for r in racers])
        desired_finish = np.random.choice(finishes, p=[0.7, 0.2, 0.1])

        planner = OutcomePlanner(racers, desired_winner, desired_finish)
        # 20 iterations per race for performance during MC
        best_racers, data = planner.optimize(iterations=20)

        ft = data['finish_times']
        sorted_ft = sorted(ft.items(), key=lambda x: x[1])
        actual_winner = sorted_ft[0][0]

        stats['winner_counts'][actual_winner] = stats['winner_counts'].get(actual_winner, 0) + 1
        winner_profile = next(r.profile_type for r in best_racers if r.racer_id == actual_winner)
        stats['profile_wins'][winner_profile] += 1

        gap = sorted_ft[1][1] - sorted_ft[0][1]
        stats['avg_gaps'].append(gap)

        # Check stamina health
        for r in best_racers:
            if data['s_dict'][r.racer_id][-1] < 0:
                stats['negative_stamina_count'] += 1

        if (i+1) % 10 == 0:
            print(f"Completed {i+1}/{num_races} races...")

    total_time = time.time() - start_time
    print("\n--- Monte Carlo Results ---")
    print(f"Total time for {num_races} races: {total_time:.2f}s")
    print(f"Average finish gap (1st to 2nd): {np.mean(stats['avg_gaps']):.3f}s")
    print("Wins by profile:")
    for k, v in stats['profile_wins'].items():
        print(f"  {k}: {v} ({v/num_races*100:.1f}%)")
    print(f"Total negative stamina occurrences across all racers/races: {stats['negative_stamina_count']}")

if __name__ == "__main__":
    run_monte_carlo(100)
