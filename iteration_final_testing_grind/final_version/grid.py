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

        self.food_respawn_timer = {}
        self.food_respawn_delay = 200

        self.food_event = "normal"
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

        if self.food_event_timer > 0:
            self.food_event_timer -= 1
            if self.food_event_timer == 0:
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

            if org.is_dead():
                to_remove.append(org)
                continue

            if not org.cannibalism:
                if pos in self.food_positions:
                    self.food_positions.remove(pos)
                    self.food_respawn_timer[pos] = frame
                    self.food_touch_time[org] = frame

                if org in self.food_touch_time and frame - self.food_touch_time[org] >= 5:
                    new_organisms.append(org.division())
                    del self.food_touch_time[org]

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

        for org in to_remove:
            if org in self.organisms:
                self.organisms.remove(org)
            self.food_touch_time.pop(org, None)
            self.carnivore_last_meal_time.pop(org, None)

        self.organisms.extend(new_organisms)
        for new_org in new_organisms:
            if hasattr(new_org, "cannibalism") and new_org.cannibalism:
                self.carnivore_last_meal_time[new_org] = frame

        to_respawn = [pos for pos, eaten_frame in self.food_respawn_timer.items()
                      if frame - eaten_frame >= self.food_respawn_delay]
        for pos in to_respawn:
            if pos not in self.food_positions:
                self.food_positions.append(pos)
            del self.food_respawn_timer[pos]

        while len(self.food_positions) < self.num_food:
            tries = 0
            while True:
                new_pos = (random.randint(0, self.size-1), random.randint(0, self.size-1))
                if new_pos not in self.food_positions:
                    self.food_positions.append(new_pos)
                    break
                tries += 1
                if tries > 10 * self.size:
                    break

        if herbivore_scatter is not None and carnivore_scatter is not None and food_scatter is not None:
            herb_x, herb_y = zip(*[(o.x, o.y) for o in self.organisms if not o.cannibalism]) if any(
                not o.cannibalism for o in self.organisms) else ([], [])
            carn_x, carn_y = zip(*[(o.x, o.y) for o in self.organisms if o.cannibalism]) if any(
                o.cannibalism for o in self.organisms) else ([], [])
            food_x, food_y = zip(*self.food_positions) if self.food_positions else ([], [])

            herbivore_scatter.set_offsets(np.c_[herb_x, herb_y])
            carnivore_scatter.set_offsets(np.c_[carn_x, carn_y])
            food_scatter.set_offsets(np.c_[food_x, food_y])

            return herbivore_scatter, carnivore_scatter, food_scatter

    def get_stats(self, frame):
        herbivores = [o for o in self.organisms if not o.cannibalism]
        carnivores = [o for o in self.organisms if o.cannibalism]
        stats = {
            'frame': frame,
            'herbivores': len(herbivores),
            'carnivores': len(carnivores),
        }
        for trait in ['speed', 'lifespan', 'food_gene', 'energy_efficiency']:
            if herbivores:
                stats[f'mean_{trait}_herb'] = np.mean([getattr(o, trait, np.nan) for o in herbivores])
            else:
                stats[f'mean_{trait}_herb'] = np.nan
            if carnivores:
                stats[f'mean_{trait}_carni'] = np.mean([getattr(o, trait, np.nan) for o in carnivores])
            else:
                stats[f'mean_{trait}_carni'] = np.nan
        return stats

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

    def animate_population(self, total_frames):
        fig, ax = plt.subplots(figsize=(8,4))
        ax.set_xlim(0, total_frames)
        ax.set_ylim(0, max(self.num_food, 20))
        ax.set_xlabel('Frame')
        ax.set_ylabel('Population')
        ax.set_title('Population Dynamics')
        line_herb, = ax.plot([], [], lw=2, color='blue', label='Herbivores')
        line_carni, = ax.plot([], [], lw=2, color='red', label='Carnivores')
        ax.legend()

        frames = []
        herb_counts = []
        carni_counts = []

        def update(frame):
            self.update(frame, None, None, None)
            stats = self.get_stats(frame)
            frames.append(frame)
            herb_counts.append(stats['herbivores'])
            carni_counts.append(stats['carnivores'])
            line_herb.set_data(frames, herb_counts)
            line_carni.set_data(frames, carni_counts)
            ax.set_xlim(0, max(100, frame+10))
            ax.set_ylim(0, max(10, max(herb_counts + carni_counts) + 5))
            return line_herb, line_carni

        ani = animation.FuncAnimation(
            fig, update, frames=total_frames, blit=True, interval=100, repeat=False
        )
        plt.show()
