import matplotlib.pyplot as plt
import numpy as np
import os

class RaceDiagnostics:
    def __init__(self, racers, phys, data, out_dir="diagnostics"):
        self.racers = racers
        self.phys = phys
        self.data = data
        self.out_dir = out_dir
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

    def _plot_phases(self, ax):
        # Mark phases as vertical lines
        phases = [0.10, 0.30, 0.60, 0.80, 1.0]
        labels = ['Launch', 'Early', 'Middle', 'Late', 'Finish']
        for p, label in zip(phases, labels):
            ax.axvline(x=p, color='gray', linestyle='--', alpha=0.5)
            ax.text(p, ax.get_ylim()[1], label, rotation=90, verticalalignment='top', alpha=0.5)

    def plot_speed_vs_distance(self):
        fig, ax = plt.subplots(figsize=(10, 6))
        for r in self.racers:
            v_p = self.data['v_dict'][r.racer_id]
            ax.plot(self.phys.p_steps, v_p, label=f"Racer {r.racer_id} ({r.profile_type})")

        ax.set_title("Speed vs Distance")
        ax.set_xlabel("Progress (p)")
        ax.set_ylabel("Velocity (m/s)")
        self._plot_phases(ax)
        ax.legend()
        plt.savefig(os.path.join(self.out_dir, "speed_vs_dist.png"))
        plt.close()

    def plot_tactical_contribution(self):
        fig, ax = plt.subplots(figsize=(10, 6))
        for r in self.racers:
            tactical = [r.get_tactical_contribution(p) for p in self.phys.p_steps]
            ax.plot(self.phys.p_steps, tactical, label=f"Racer {r.racer_id}")

        ax.set_title("Tactical Contribution vs Distance")
        ax.set_xlabel("Progress (p)")
        ax.set_ylabel("Velocity Delta (m/s)")
        self._plot_phases(ax)
        ax.legend()
        plt.savefig(os.path.join(self.out_dir, "tactical_vs_dist.png"))
        plt.close()

    def plot_stamina_vs_distance(self):
        fig, ax = plt.subplots(figsize=(10, 6))
        for r in self.racers:
            s_p = self.data['s_dict'][r.racer_id]
            ax.plot(self.phys.p_steps, s_p, label=f"Racer {r.racer_id}")

        ax.set_title("Stamina vs Distance")
        ax.set_xlabel("Progress (p)")
        ax.set_ylabel("Remaining Stamina")
        self._plot_phases(ax)
        ax.legend()
        plt.savefig(os.path.join(self.out_dir, "stamina_vs_dist.png"))
        plt.close()

    def plot_position_relative_to_mean(self):
        fig, ax = plt.subplots(figsize=(10, 6))
        t_anim = self.data['t_anim']
        p_anim = self.data['p_anim']

        # Calculate mean progress at each timestep
        mean_p = np.mean([p_anim[r.racer_id] for r in self.racers], axis=0)

        for r in self.racers:
            rel_p = p_anim[r.racer_id] - mean_p
            ax.plot(t_anim, rel_p, label=f"Racer {r.racer_id}")

        ax.set_title("Relative Position (from Mean) over Time")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Delta Progress")
        ax.legend()
        plt.savefig(os.path.join(self.out_dir, "relative_pos.png"))
        plt.close()

    def generate_all(self):
        self.plot_speed_vs_distance()
        self.plot_tactical_contribution()
        self.plot_stamina_vs_distance()
        self.plot_position_relative_to_mean()
