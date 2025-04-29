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
        self.num_food = num_food
        self.food_seed = food_seed
        self.fixed_food_positions = self.generate_fixed_food()
        self.food_positions = list(self.fixed_food_positions)
        self.food_touch_time = {}
        self.carnivore_division_probab = 0.1
        self.carnivore_last_meal_time = {}
        self.carnivore_starvation_time = 150

        # New for individual food regeneration
        self.food_respawn_timer = {}  # {pos: frame_when_eaten}
        self.food_respawn_delay = 200  # frames to wait before respawning eaten food

        # Dynamic food event system
        self.food_event = "normal"  # can be "normal", "drought", "abundance"
        self.food_event_timer = 0
        self.food_event_duration = 0
        self.base_food_respawn_delay = 200
        self.base_num_food = num_food

    def generate_fixed_food(self):
        rng = np.random.default_rng(self.food_seed)
        return [tuple(pos) for pos in rng.integers(0, self.size, (self.num_food, 2))]

    def spawn_food(self):
        return list(self.fixed_food_positions)

    def add_organisms(self, organisms):
        self.organisms = organisms
        for org in organisms:
            if hasattr(org, "cannibalism") and org.cannibalism:
                self.carnivore_last_meal_time[org] = 0

    def trigger_food_event(self):
        # Randomly trigger a food event with a small probability
        if self.food_event_timer == 0 and random.random() < 0.01:
            event = random.choices(
                ["drought", "abundance", "normal"],
                weights=[0.2, 0.15, 0.65]
            )[0]
            if event == "drought":
                self.food_event = "drought"
                self.food_event_duration = random.randint(200, 400)
                self.food_respawn_delay = int(self.base_food_respawn_delay * 2.5)
                self.num_food = max(5, int(self.base_num_food * 0.4))
            elif event == "abundance":
                self.food_event = "abundance"
                self.food_event_duration = random.randint(150, 300)
                self.food_respawn_delay = int(self.base_food_respawn_delay * 0.5)
                self.num_food = int(self.base_num_food * 1.5)
            else:
                self.food_event = "normal"
                self.food_event_duration = random.randint(300, 600)
                self.food_respawn_delay = self.base_food_respawn_delay
                self.num_food = self.base_num_food
            self.food_event_timer = self.food_event_duration
            print(f"Food event triggered: {self.food_event} for {self.food_event_duration} frames.")

        # Decrement event timer and reset if event ends
        if self.food_event_timer > 0:
            self.food_event_timer -= 1
            if self.food_event_timer == 0:
                # Reset to normal
                self.food_event = "normal"
                self.food_respawn_delay = self.base_food_respawn_delay
                self.num_food = self.base_num_food
                print("Food event ended, returning to normal.")

    def update(self, frame, herbivore_scatter, carnivore_scatter, food_scatter):
        self.trigger_food_event()

        new_organisms = []
        to_remove = []

        for org in self.organisms:
            org.move(self.food_positions, self.organisms)
            pos = (org.x, org.y)

            # Death by age
            if org.is_dead():
                to_remove.append(org)
                continue

            # Herbivore logic
            if not org.cannibalism:
                if pos in self.food_positions:
                    self.food_positions.remove(pos)
                    self.food_respawn_timer[pos] = frame  # Mark for delayed respawn
                    self.food_touch_time[org] = frame

                if org in self.food_touch_time and frame - self.food_touch_time[org] >= 5:
                    new_organisms.append(org.division())
                    del self.food_touch_time[org]

            # Carnivore logic
            else:
                fed = False
                for target in self.organisms:
                    if not target.cannibalism and (target.x, target.y) == pos and target not in to_remove:
                        to_remove.append(target)
                        fed = True
                        self.carnivore_last_meal_time[org] = frame
                        org.rest_timer = 10
                        if random.random() < self.carnivore_division_probab:
                            new_organisms.append(org.division())
                        break

                if org in self.carnivore_last_meal_time and frame - self.carnivore_last_meal_time[org] >= self.carnivore_starvation_time:
                    to_remove.append(org)

        # Cleanup removed organisms
        for org in to_remove:
            if org in self.organisms:
                self.organisms.remove(org)
            self.food_touch_time.pop(org, None)
            self.carnivore_last_meal_time.pop(org, None)

        # Add new organisms
        self.organisms.extend(new_organisms)
        for new_org in new_organisms:
            if hasattr(new_org, "cannibalism") and new_org.cannibalism:
                self.carnivore_last_meal_time[new_org] = frame

        # Individual food respawn
        to_respawn = [pos for pos, eaten_frame in self.food_respawn_timer.items()
                      if frame - eaten_frame >= self.food_respawn_delay]
        for pos in to_respawn:
            if pos not in self.food_positions:
                self.food_positions.append(pos)
            del self.food_respawn_timer[pos]

        # If food is too low, respawn at random positions to maintain event-driven num_food
        while len(self.food_positions) < self.num_food:
            # Random position, avoid overlap
            tries = 0
            while True:
                new_pos = (random.randint(0, self.size-1), random.randint(0, self.size-1))
                if new_pos not in self.food_positions:
                    self.food_positions.append(new_pos)
                    break
                tries += 1
                if tries > 10 * self.size:
                    break  # Avoid infinite loop

        # Update plot positions
        herb_x, herb_y = zip(*[(o.x, o.y) for o in self.organisms if not o.cannibalism]) if any(
            not o.cannibalism for o in self.organisms) else ([], [])
        carn_x, carn_y = zip(*[(o.x, o.y) for o in self.organisms if o.cannibalism]) if any(
            o.cannibalism for o in self.organisms) else ([], [])
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

        herbivore_scatter = ax.scatter([], [], c='blue', s=20, marker='o', label="Herbivores")
        carnivore_scatter = ax.scatter([], [], c='red', s=30, marker='s', label="Carnivores")
        food_scatter = ax.scatter([], [], c='green', s=30, marker='x', label="Food")

        ax.legend(loc="upper right")

        ani = animation.FuncAnimation(fig, self.update, interval=100,
                                      fargs=(herbivore_scatter, carnivore_scatter, food_scatter), blit=True)
        plt.show()
