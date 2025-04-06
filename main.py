import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline, BSpline
from grid import Grid
from organism import Organism

# Initialize plot
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_title("20x20 Grid Animation")

# Create Grid
grid_size = 20  # Change to 1000 for a large grid
time_steps = 200  # Number of frames in animation
g = Grid(grid_size, time_steps)

# Create and add organisms
num_organisms = 5  # Adjust number of organisms
organisms = [Organism(np.random.randint(0, grid_size), np.random.randint(0, grid_size), grid_size) for _ in range(num_organisms)]
g.add_organisms(organisms)

# Run animation
population_data = g.animate(fig, ax)

# Time values
time = np.arange(len(population_data))

# B-Spline Smoothing
xnew = np.linspace(time.min(), time.max(), 15)  # More points for smoothness
spl = make_interp_spline(time, population_data, k=3)  # type: BSpline
smooth_population = spl(xnew)

# Plotting
plt.figure()
plt.plot(time, population_data, label='Original Data')
plt.plot(xnew, smooth_population, label='B-Spline Smoothed', color='red')
plt.xlabel("Time Step")
plt.ylabel("Number of Organisms")
plt.title("Organism Population Over Time")
plt.legend()
plt.show()
