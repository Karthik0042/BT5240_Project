import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from organism import Organism

class Grid:
    def __init__(self, size, num_organisms, num_food, food_seed=42):
        self.size = size
        self.organisms = []
        self.time_steps = 0
        self.last_food_spawn_time = 0
        self.food_timer = 200
        self.num_food = num_food
        self.food_seed = food_seed
        self.fixed_food_positions = self.generate_fixed_food()  # Fixed positions
        self.food_positions = list(self.fixed_food_positions)
        self.organism_timers = {}
        self.food_touch_time = {}
        self.carnivore_division_probab = 0.4
        self.carnivore_last_meal_time = {}
        self.carnivore_starvation_time = 100  # frames before a carnivore dies from starvation

    def generate_fixed_food(self):
        rng = np.random.default_rng(self.food_seed)
        return [tuple(pos) for pos in rng.integers(0, self.size, (self.num_food, 2))]

    def spawn_food(self):
        return list(self.fixed_food_positions)


    def add_organisms(self, organisms):
        self.organisms = organisms
        for org in organisms:
            self.organism_timers[org] = 0
            if org.canbalism:
                self.carnivore_last_meal_time[org] = 0

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

                if org in self.food_touch_time and frame - self.food_touch_time[org] >= 5:
                    new_organisms.append(org.division())
                    del self.food_touch_time[org]

                if frame - self.organism_timers[org] >= 100:
                    to_remove.append(org)

            else:
                fed = False
                for target in self.organisms:
                    if not target.canbalism and (target.x, target.y) == pos and target not in to_remove:
                        to_remove.append(target)
                        fed = True
                        self.carnivore_last_meal_time[org] = frame
                        if random.random() < self.carnivore_division_probab:
                            new_organisms.append(org.division())
                        break

                # Starvation check
                if org in self.carnivore_last_meal_time:
                    if frame - self.carnivore_last_meal_time[org] >= self.carnivore_starvation_time:
                        to_remove.append(org)

        for org in to_remove:
            if org in self.organisms:
                self.organisms.remove(org)
            self.organism_timers.pop(org, None)
            self.food_touch_time.pop(org, None)
            self.carnivore_last_meal_time.pop(org, None)

        self.organisms.extend(new_organisms)
        for new_org in new_organisms:
            if new_org.canbalism:
                self.carnivore_last_meal_time[new_org] = frame
            self.organism_timers[new_org] = frame

        if frame - self.last_food_spawn_time >= self.food_timer and len(self.food_positions) == 0:
            self.food_positions = self.spawn_food()
            self.last_food_spawn_time = frame

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
