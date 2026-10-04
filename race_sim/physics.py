import numpy as np
from race_math import smooth_blend
from racer import Racer, RacerProfile

# Constants
RACE_DISTANCE = 1200.0
LAUNCH_END_P = 0.10      # ~120m
STRETCH_START_P = 0.80   # ~960m
# Integration step size
DP = 0.001

class RacePhysics:
    def __init__(self, racers):
        self.racers = racers
        self.p_steps = np.arange(0, 1.0 + DP, DP)

    def generate_velocity_curve(self, racer):
        """
        Generates the velocity array for the racer over the distance domain `self.p_steps`.
        Returns v(p) and the remaining stamina.
        """
        v_p = np.zeros_like(self.p_steps)
        stamina_p = np.zeros_like(self.p_steps)

        current_stamina = racer.max_stamina

        # We also need acceleration to compute stamina, but since v is defined via functions,
        # we can compute a raw target v(p) first, and then apply stamina bounds if we want.
        # However, to avoid a zero-wall, remaining stamina will gracefully decay the ability
        # to apply tactical or stretch contributions.

        # Launch parameters (similar for all)
        launch_start_v = racer.base_speed * 0.2  # Start slow at the gun

        for i, p in enumerate(self.p_steps):

            # 1. Base sustainable speed + tactical
            tactical = racer.get_tactical_contribution(p)
            target_v = racer.base_speed + tactical

            # 2. Universal Launch Mechanic
            # Smoothly transition from starting speed to the target speed around LAUNCH_END_P
            # We allow slight variations by using racer.power or similar, but for now we keep it unified
            launch_factor = smooth_blend(p, 0.0, LAUNCH_END_P)
            # v after launch
            v_current = launch_start_v * (1 - launch_factor) + target_v * launch_factor

            # 3. Last Stretch Mechanic
            # At STRETCH_START_P, tactical identity fades and it becomes a test of Speed, Power, Stamina
            stretch_blend = smooth_blend(p, STRETCH_START_P - 0.02, STRETCH_START_P + 0.03)

            # Stretch effort is bounded by remaining stamina and modulated by power
            # Smoothly cap stamina effect (if stamina < 10, effort drops)
            stamina_factor = smooth_blend(current_stamina, 0, racer.max_stamina * 0.2)
            stretch_effort = (racer.power * 0.1 + racer.base_speed * 0.05) * stamina_factor

            stretch_v = racer.base_speed + stretch_effort

            v_final = v_current * (1 - stretch_blend) + stretch_v * stretch_blend

            # Record velocity
            v_p[i] = v_final
            stamina_p[i] = current_stamina

            # 4. Integrate Stamina cost
            # Time delta for this distance step
            dx = DP * RACE_DISTANCE
            dt = dx / v_final if v_final > 0 else 0

            # Base running cost proportional to time/distance
            base_cost_rate = 0.5

            # Cost for operating above base speed
            overspeed = max(0, v_final - racer.base_speed)
            overspeed_cost_rate = overspeed ** 1.5 * 0.1

            # We'll compute dv/dt for acceleration cost
            accel_cost_rate = 0.0
            if i > 0:
                dt_prev = dx / v_p[i-1] if v_p[i-1] > 0 else 0.01
                dv = (v_final - v_p[i-1])
                accel = dv / dt if dt > 0 else 0
                if accel > 0:
                    accel_cost_rate = (accel ** 1.2) * 0.2

            total_cost_rate = base_cost_rate + overspeed_cost_rate + accel_cost_rate
            cost = total_cost_rate * dt

            current_stamina -= cost

        return v_p, stamina_p

    def integrate_trajectories(self, v_p_dict):
        """
        Integrates v(p) to find t(p), then inverts to find p(t) for animation.
        Returns a time grid and positions at those times.
        """
        t_p_dict = {}
        max_t = 0

        for racer_id, v_p in v_p_dict.items():
            t_p = np.zeros_like(self.p_steps)
            for i in range(1, len(self.p_steps)):
                dx = DP * RACE_DISTANCE
                # Trapezoidal rule for better dt estimation
                v_avg = (v_p[i] + v_p[i-1]) / 2.0
                dt = dx / v_avg if v_avg > 0 else 0
                t_p[i] = t_p[i-1] + dt

            t_p_dict[racer_id] = t_p
            if t_p[-1] > max_t:
                max_t = t_p[-1]

        # Create a common time grid
        dt_anim = 0.1 # 10 FPS
        t_anim = np.arange(0, max_t + dt_anim, dt_anim)

        p_anim_dict = {}
        for racer_id, t_p in t_p_dict.items():
            # Invert t(p) -> p(t) using interpolation
            p_anim = np.interp(t_anim, t_p, self.p_steps)
            p_anim_dict[racer_id] = p_anim

        return t_anim, p_anim_dict
