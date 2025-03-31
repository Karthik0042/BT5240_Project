# main.py

import numpy as np
import matplotlib.pyplot as plt
from grid import Grid
from organism import Organism

# Initialize plot
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_title("10x10 Grid Animation") # Change title to "20x20 Grid Animation"

# Create Grid
grid_size = 20  # Change to 1000 for a large grid
time_steps = 50  # Number of frames in animation
g = Grid(grid_size, time_steps)

# Create and add organisms
num_organisms = 1  # Adjust number of organisms
organisms = [Organism(np.random.randint(0, grid_size), np.random.randint(0, grid_size), grid_size) for _ in range(num_organisms)]
g.add_organisms(organisms)

# Run animation
g.animate(fig, ax)

