# grid.py

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class Grid:
    def __init__(self, size, time_steps):
        self.size = size
        self.time_steps = time_steps  # Number of animation frames
        self.organisms = []  # List of organisms

    def add_organisms(self, organisms):
        """Add a list of organisms to the grid."""
        self.organisms = organisms

    def update(self, frame, scatter):
        """Move organisms and update scatter plot."""
        # Move organisms
        for org in self.organisms:
            org.move()

        # Update scatter plot positions
        x_vals = [org.x for org in self.organisms]
        y_vals = [org.y for org in self.organisms]
        scatter.set_offsets(np.c_[x_vals, y_vals])  # Efficient update using set_offsets

        return scatter,  # Blit requires a tuple

    def animate(self, fig, ax):
        """Run animation."""
        # Draw grid
        ax.set_xticks(np.arange(0, self.size, 1), minor=True)
        ax.set_yticks(np.arange(0, self.size, 1), minor=True)
        ax.grid(which="minor", color="gray", linestyle="-", linewidth=0.1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(0, self.size)
        ax.set_ylim(0, self.size)

        # Create scatter plot for organisms
        scatter = ax.scatter([], [], c='red', s=20)  # s=20 for size of dots

        # Create animation
        ani = animation.FuncAnimation(fig, self.update, frames=self.time_steps, interval=100, fargs=(scatter,),
                                      blit=True)

        plt.show()
