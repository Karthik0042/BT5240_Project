import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from organism import Organism

class Grid:
    def __init__(self, size, num_organisms, num_food):
        self.size = size
        self.organisms = []
        self.time_steps = 0
        self.last_food_spawn_time = 0
        self.food_timer = 200
        self.num_food = num_food
        self.food_positions = self.spawn_food()
        self.organism_timers = {}
        self.food_touch_time = {}

    def spawn_food(self):
        return [tuple(pos) for pos in np.random.randint(0, self.size, (self.num_food, 2))]

    def add_organisms(self, organisms):
        self.organisms = organisms
        for org in organisms:
            self.organism_timers[org] = 0

    def update(self, frame, herbivore_scatter, carnivore_scatter, food_scatter):
        new_organisms = []
        to_remove = []

        for org in self.organisms:
            org.move(self.food_positions, self.organisms)
            pos = (org.x, org.y)

            if org not in self.organism_timers:
                self.organism_timers[org] = frame

            if not org.canbalism:
                if pos in self.food_positions:
                    self.food_positions.remove(pos)
                    self.organism_timers[org] = frame
                    self.food_touch_time[org] = frame

                if org in self.food_touch_time and frame - self.food_touch_time[org] >= 50:
                    new_organisms.append(org.division())
                    del self.food_touch_time[org]

                if frame - self.organism_timers[org] >= 100:
                    to_remove.append(org)
            else:
                # Carnivore logic: Check for herbivore at the same position
                for target in self.organisms:
                    if not target.canbalism and (target.x, target.y) == pos and target not in to_remove:
                        to_remove.append(target)  # Remove herbivore
                        new_organisms.append(org.division())  # Carnivore divides upon consuming herbivore
                        break  # Carnivore eats only one herbivore per frame

        # Remove organisms that should be removed
        for org in to_remove:
            if org in self.organisms:
                self.organisms.remove(org)
            self.organism_timers.pop(org, None)
            self.food_touch_time.pop(org, None)

        # Add new organisms (carnivore divisions)
        self.organisms.extend(new_organisms)

        # Food respawn logic
        if frame - self.last_food_spawn_time >= self.food_timer and len(self.food_positions) == 0:
            self.food_positions = self.spawn_food()
            self.last_food_spawn_time = frame

        # Update scatter data
        herb_x, herb_y = zip(*[(o.x, o.y) for o in self.organisms if not o.canbalism]) if any(
            not o.canbalism for o in self.organisms) else ([], [])
        carn_x, carn_y = zip(*[(o.x, o.y) for o in self.organisms if o.canbalism]) if any(
            o.canbalism for o in self.organisms) else ([], [])
        food_x, food_y = zip(*self.food_positions) if self.food_positions else ([], [])

        herbivore_scatter.set_offsets(np.c_[herb_x, herb_y])
        carnivore_scatter.set_offsets(np.c_[carn_x, carn_y])
        food_scatter.set_offsets(np.c_[food_x, food_y])

        return herbivore_scatter, carnivore_scatter, food_scatter

    def animate(self, fig, ax):
        ax.set_xticks(np.arange(0, self.size, 1), minor=True)
        ax.set_yticks(np.arange(0, self.size, 1), minor=True)
        ax.grid(which="minor", color="gray", linestyle="-", linewidth=0.1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(0, self.size)
        ax.set_ylim(0, self.size)

        herbivore_scatter = ax.scatter([], [], c='red', s=20, marker='s', label="Herbivores")
        carnivore_scatter = ax.scatter([], [], c='blue', s=30, marker='o', label="Carnivores")
        food_scatter = ax.scatter([], [], c='green', s=30, marker='x', label="Food")

        ax.legend(loc="upper right")

        ani = animation.FuncAnimation(fig, self.update, interval=100,
                                      fargs=(herbivore_scatter, carnivore_scatter, food_scatter), blit=True)
        plt.show()
