import numpy as np
import matplotlib.pyplot as plt
from grid import Grid
from organism import Organism

fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlim(0, 20)
ax.set_ylim(0, 20)
ax.set_title("Simulation")

grid_size = 20
time_steps = None
num_organisms = 10
reproduction_time = 75  # Adjusted reproduction time

def run_simulation():
    g = Grid(grid_size, time_steps, reproduction_time)
    organisms = [
        Organism(
            np.random.randint(0, grid_size),
            np.random.randint(0, grid_size),
            grid_size,
            speed=0.3 + np.random.normal(0, 0.1),  # Initial speed around 0.3
            food_gene=0.3 + np.random.uniform(0, 0.1)  # food detection
        ) for _ in range(num_organisms)
    ]
    g.add_organisms(organisms)
    population_data, avg_speed_history, avg_food_gene_history, food_count_history, food_interactions = g.animate(fig, ax)
    return {
        'population': population_data,
        'avg_speed_history': avg_speed_history,
        'avg_food_gene_history': avg_food_gene_history,
        'food_count_history': food_count_history,
        'food_interactions': food_interactions
    }

# Run the simulation
results = run_simulation()

# Plot the graphs
g = Grid(grid_size, time_steps, reproduction_time)
g.plot_graphs(
    results['population'],
    results['avg_speed_history'],
    results['avg_food_gene_history'],
    results['food_count_history'],
    results['food_interactions']
)
