import numpy as np
import matplotlib.pyplot as plt
from grid import Grid
from organism import Organism

# Parameters
grid_size = 50
num_herbivores = 15  # Increased from 10
num_carnivores = 2
num_food = 200  # Increased from 150

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

# Setup plot with six subplots
fig = plt.figure(figsize=(15, 10))
grid_ax = fig.add_subplot(231)
memory_fear_ax = fig.add_subplot(232)
herbivore_memory_fear_lifespan_ax = fig.add_subplot(233)
herbivore_trait_ax = fig.add_subplot(234)
carnivore_trait_ax = fig.add_subplot(235)
food_gene_ax = fig.add_subplot(236)
grid_ax.set_title("Grid Simulation: Herbivores (Red), Carnivores (Blue)")
fig.tight_layout(pad=3.0)

# Animate
g.animate(fig, grid_ax, memory_fear_ax, herbivore_memory_fear_lifespan_ax, herbivore_trait_ax, carnivore_trait_ax, food_gene_ax)
