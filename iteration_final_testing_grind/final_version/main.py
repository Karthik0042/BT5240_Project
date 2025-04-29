import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from grid import Grid
from organism import Organism


# Parameters
grid_size = 50
num_herbivores = 5
num_carnivores = 0
num_food = 100
total_frames = 2000

organisms = [
    Organism(np.random.randint(0, grid_size), np.random.randint(0, grid_size), grid_size, cannibalism=False)
    for _ in range(num_herbivores)
]
organisms += [
    Organism(np.random.randint(0, grid_size), np.random.randint(0, grid_size), grid_size, cannibalism=True)
    for _ in range(num_carnivores)
]

g = Grid(grid_size, num_organisms=num_herbivores + num_carnivores, num_food=num_food)
g.add_organisms(organisms)

fig, (ax_grid, ax_pop) = plt.subplots(1, 2, figsize=(14, 6))

# Grid subplot
ax_grid.set_title("Grid Simulation: Herbivores (Blue), Carnivores (Red)")
ax_grid.set_xticks([])
ax_grid.set_yticks([])
ax_grid.set_xlim(0, grid_size)
ax_grid.set_ylim(0, grid_size)
herbivore_scatter = ax_grid.scatter([], [], c='blue', s=20, marker='o', label="Herbivores")
carnivore_scatter = ax_grid.scatter([], [], c='red', s=30, marker='s', label="Carnivores")
food_scatter = ax_grid.scatter([], [], c='green', s=30, marker='x', label="Food")
ax_grid.legend(loc="upper right")

# Population subplot
ax_pop.set_xlabel('Frame')
ax_pop.set_ylabel('Population')
ax_pop.set_title('Population Dynamics')
line_herb, = ax_pop.plot([], [], lw=2, color='blue', label='Herbivores')
line_carni, = ax_pop.plot([], [], lw=2, color='red', label='Carnivores',linestyle= ':' )
ax_pop.legend()

herb_counts = np.full(total_frames, np.nan)
carni_counts = np.full(total_frames, np.nan)

def update(frame):
    g.update(frame, herbivore_scatter, carnivore_scatter, food_scatter)
    stats = g.get_stats(frame)
    herb_counts[frame] = stats['herbivores']
    carni_counts[frame] = stats['carnivores']

    x = np.arange(frame + 1)
    line_herb.set_data(x, herb_counts[:frame + 1])
    line_carni.set_data(x, carni_counts[:frame + 1])

    # X axis: always show full history up to current frame
    ax_pop.set_xlim(0, frame + 1)
    # Y axis: autoscale to max so far, with a small buffer
    y_max = max(10, np.nanmax(herb_counts[:frame + 1]), np.nanmax(carni_counts[:frame + 1]))
    ax_pop.set_ylim(0, y_max + 5)

    return herbivore_scatter, carnivore_scatter, food_scatter, line_herb, line_carni

ani = animation.FuncAnimation(
    fig, update, frames=total_frames, blit=False, interval=100, repeat=False
)

plt.tight_layout()
plt.show()
