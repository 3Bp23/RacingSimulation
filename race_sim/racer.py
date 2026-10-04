import numpy as np
from race_math import bump_profile, smooth_blend

class RacerProfile:
    FRONT_RUNNER = "front_runner"
    PACER = "pacer"
    LATE_SURGER = "late_surger"

class Racer:
    def __init__(self, racer_id, profile_type, speed, power, stamina, profile_params):
        """
        racer_id: int/string identifier
        profile_type: RacerProfile string
        speed: sustainable baseline speed (m/s)
        power: ability to accelerate / respond (scalar)
        stamina: total energy resource (scalar)
        profile_params: dict containing elasticity envelope parameters (amplitude, start, peak, end)
        """
        self.racer_id = racer_id
        self.profile_type = profile_type

        self.base_speed = speed
        self.power = power
        self.max_stamina = stamina
        self.stamina = stamina

        self.profile_params = profile_params

    def get_tactical_contribution(self, p):
        """
        Returns the tactical speed contribution at progress p (0 to 1).
        """
        params = self.profile_params
        amplitude = params.get('amplitude', 0.5)

        if self.profile_type == RacerProfile.FRONT_RUNNER:
            # Rise early, peak early (e.g. Early Race), fade gradually
            start = params.get('start', 0.05)
            peak = params.get('peak', 0.20)
            end = params.get('end', 0.60)
            return amplitude * bump_profile(p, start, peak, end)

        elif self.profile_type == RacerProfile.PACER:
            # Delayed rise, mid-race peak, converge before stretch
            start = params.get('start', 0.20)
            peak = params.get('peak', 0.50)
            end = params.get('end', 0.80)
            return amplitude * bump_profile(p, start, peak, end)

        elif self.profile_type == RacerProfile.LATE_SURGER:
            # Hold, setup later, strong late rise (Late Race), converge at Stretch
            start = params.get('start', 0.40)
            peak = params.get('peak', 0.70)
            end = params.get('end', 0.85)
            return amplitude * bump_profile(p, start, peak, end)

        return 0.0
