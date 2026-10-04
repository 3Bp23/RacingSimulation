import pygame
import sys
import numpy as np

class RaceVisualizer:
    def __init__(self, racers, data, width=1200, height=600):
        self.racers = racers
        self.t_anim = data['t_anim']
        self.p_anim = data['p_anim']

        self.width = width
        self.height = height
        self.fps = 60 # playback fps, decoupled from integration dt

        # Map profile types to colors
        self.colors = {
            'front_runner': (255, 100, 100),
            'pacer': (100, 255, 100),
            'late_surger': (100, 100, 255)
        }

    def play(self):
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("1200m Race Sim")
        clock = pygame.time.Clock()

        font = pygame.font.SysFont(None, 24)

        # Find total time
        max_t = self.t_anim[-1]
        t_current = 0.0
        dt = 0.1 # Real-time simulation speed multiplier can be applied here

        running = True
        while running and t_current <= max_t + 2.0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((30, 30, 30))

            # Draw finish line
            finish_x = self.width * 0.9
            pygame.draw.line(screen, (255, 255, 255), (finish_x, 0), (finish_x, self.height), 2)

            # Interpolate positions
            for i, r in enumerate(self.racers):
                # interp to get progress at current time
                p = np.interp(t_current, self.t_anim, self.p_anim[r.racer_id])
                x = 50 + p * (finish_x - 50)
                y = 50 + i * 40

                color = self.colors.get(r.profile_type, (200, 200, 200))
                pygame.draw.circle(screen, color, (int(x), int(y)), 10)

                label = font.render(str(r.racer_id), True, (255, 255, 255))
                screen.blit(label, (int(x) - 5, int(y) - 8))

            time_label = font.render(f"Time: {t_current:.1f}s", True, (255, 255, 255))
            screen.blit(time_label, (10, 10))

            pygame.display.flip()

            t_current += dt
            clock.tick(self.fps)

        pygame.quit()
