import numpy as np
import matplotlib.pyplot as plt
from grid import Grid
from organism import Organism

# Parameters
grid_size = 50
num_herbivores = 5
num_carnivores = 0
num_food = 100

# Create organisms
organisms = [
    Organism(np.random.randint(0, grid_size), np.random.randint(0, grid_size), grid_size, cannibalism=False)
    for _ in range(num_herbivores)
]
organisms += [
    Organism(np.random.randint(0, grid_size), np.random.randint(0, grid_size), grid_size, cannibalism=True)
    for _ in range(num_carnivores)
]

# Initialize grid
g = Grid(grid_size, num_organisms=num_herbivores + num_carnivores, num_food=num_food)
g.add_organisms(organisms)

# Setup plot
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_title("Grid Simulation: Herbivores (Red), Carnivores (Blue)")

# Animate
g.animate(fig, ax)

