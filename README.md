# 1200m Race Simulation

A physics-based, continuous mathematical race simulation designed for storytelling and dramatic natural races.

## Deliverables Include
1. **Mathematical Foundation (`race_math.py`)**: Uses $C^1$ and $C^2$ continuous basis functions (Perlin's `smootherstep`, asymmetric Gaussian) to ensure velocities and transitions are visually and mechanically smooth.
2. **Physics Module (`physics.py`)**: Operates in the distance domain $p = x/1200$. Calculates continuous velocity profiles combining the universal Launch, parameter-driven Tactical profiles, and Stamina-bound Last Stretch mechanics. Performs numerical integration to invert distance vs time into $x(t)$.
3. **Outcome Planner (`planner.py`)**: Resolves the "Predetermined Outcome" constraint using a random-search optimizer. It slightly mutates base racers and evaluates candidate races against an objective loss function that penalizes wrong winners, incorrect gap distances, field stagnancy, and zero-stamina exhaustion, without resorting to rubber-banding.
4. **Diagnostics & Visualization (`diagnostics.py`, `visualization.py`)**: Outputs comprehensive Matplotlib charts for analysis and a simple 2D side-scrolling playback using Pygame.
5. **Monte Carlo Validation (`monte_carlo.py`)**: Evaluates batches of races against desired storylines.

## Tuning Parameters
- `LAUNCH_END_P`, `STRETCH_START_P` (in `physics.py`): Control global phase triggers.
- `Racer` initializations: The core Speed, Power, Stamina baselines set the pack behavior, while `amplitude`, `start`, `peak`, and `end` map the tactical elasticity envelope.
- `OutcomePlanner` loss function (in `planner.py`): Weights for winner mismatch, finish gaps, and spread dynamically adjust the acceptable "dramatic flavor" of generated races.

## Weaknesses & Next Steps
- **Stamina Modeling**: Currently, stamina affects the final Stretch capability and imposes loss penalties during optimization. True non-linear exhaustion (where a runner heavily fades mid-race due to 0 stamina) requires further testing to ensure the velocity function remains $C^1$ continuous as they enter a "walking" state.
- **Planner Efficiency**: The evolutionary search uses simple deep copies and random mutations. Moving to a more sophisticated gradient-free optimizer (like CMA-ES) could speed up generation drastically.
- **Monte Carlo Metrics**: Need to extend the batch loop to capture dynamic stats (like exact counts of lead changes).
