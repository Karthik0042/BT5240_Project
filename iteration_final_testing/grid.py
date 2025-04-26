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
        self.num_food = num_food
        self.food_seed = food_seed
        self.food_positions = self.spawn_initial_food()
        self.initial_food_positions = set(self.food_positions)  # Store fixed food locations
        self.food_touch_time = {}
        self.carnivore_division_probab = 0.125
        self.carnivore_last_meal_time = {}
        self.carnivore_starvation_time = 395

        self.food_respawn_timer = {}
        self.food_respawn_delay = 80

        self.trait_history = {
            'herbivore_food_gene': [],
            'herbivore_speed': [],
            'herbivore_lifespan': [],
            'herbivore_energy_efficiency': [],
            'herbivore_memory': [],
            'herbivore_fear': [],
            'carnivore_food_gene': [],
            'carnivore_speed': [],
            'carnivore_lifespan': [],
            'carnivore_energy_efficiency': []
        }
        self.memory_fear_history = []

    def spawn_initial_food(self):
        rng = np.random.default_rng(self.food_seed)
        food_positions = []
        positions = set()
        while len(food_positions) < self.num_food:
            x, y = rng.integers(0, self.size, 2)
            pos = (x, y)
            if pos not in positions:
                food_positions.append(pos)
                positions.add(pos)
        return food_positions

    def spawn_dynamic_food(self, frame):
        # Only respawn food at initial positions after delay
        to_respawn = [pos for pos, eaten_frame in self.food_respawn_timer.items()
                      if frame - eaten_frame >= self.food_respawn_delay]
        for pos in to_respawn:
            if pos not in self.food_positions and pos in self.initial_food_positions:
                self.food_positions.append(pos)
            del self.food_respawn_timer[pos]

    def add_organisms(self, organisms):
        self.organisms = organisms
        for org in organisms:
            if org.cannibalism:
                self.carnivore_last_meal_time[org] = 0

    def update(self, frame, herbivore_scatter, carnivore_scatter, food_scatter,
               memory_fear_scatter, herbivore_trait_lines, carnivore_trait_lines,
               food_gene_lines, herbivore_memory_fear_lifespan_lines):
        new_organisms = []
        to_remove = []

        self.spawn_dynamic_food(frame)

        for org in self.organisms:
            movement_cost = 1.0  # Fixed movement cost, no fertility map
            org.move(self.food_positions, self.organisms, movement_cost)
            pos = (org.x, org.y)

            if org.is_dead():
                to_remove.append(org)
                continue

            if not org.cannibalism:
                if pos in self.food_positions:
                    self.food_positions.remove(pos)
                    self.food_respawn_timer[pos] = frame
                    self.food_touch_time[org] = frame
                    org.last_food_location = pos
                    org.memory_timer = 0

                if org in self.food_touch_time and frame - self.food_touch_time[org] >= 3:
                    new_organisms.append(org.division())
                    del self.food_touch_time[org]

            else:
                fed = False
                for target in self.organisms:
                    if not target.cannibalism and (target.x, target.y) == pos and target not in to_remove:
                        to_remove.append(target)
                        fed = True
                        self.carnivore_last_meal_time[org] = frame
                        if random.random() < self.carnivore_division_probab:
                            new_organisms.append(org.division())
                        for herbivore in self.organisms:
                            if not herbivore.cannibalism and herbivore != target:
                                if herbivore.witness_cannibalization(org, (target.x, target.y)):
                                    herbivore.communicate_carnivore(self.organisms, org)
                        break

                if org in self.carnivore_last_meal_time and frame - self.carnivore_last_meal_time[org] >= self.carnivore_starvation_time:
                    to_remove.append(org)

        # Detect carnivore collisions
        carnivore_positions = {}
        for org in self.organisms:
            if org.cannibalism and not org.is_dead():
                pos = (org.x, org.y)
                if pos in carnivore_positions:
                    carnivore_positions[pos].append(org)
                else:
                    carnivore_positions[pos] = [org]

        collisions = 0
        for pos, orgs in carnivore_positions.items():
            if len(orgs) > 1:  # Collision detected
                collisions += len(orgs)
                for org in orgs:
                    org.lifespan = max(50, org.lifespan - 150)

        for org in to_remove:
            if org in self.organisms:
                self.organisms.remove(org)
            self.food_touch_time.pop(org, None)
            self.carnivore_last_meal_time.pop(org, None)

        self.organisms.extend(new_organisms)
        for new_org in new_organisms:
            if new_org.cannibalism:
                self.carnivore_last_meal_time[new_org] = frame

        herb_positions = [(o.x, o.y) for o in self.organisms if not o.cannibalism]
        carn_positions = [(o.x, o.y) for o in self.organisms if o.cannibalism]
        herb_x, herb_y = zip(*herb_positions) if herb_positions else ([], [])
        carn_x, carn_y = zip(*carn_positions) if carn_positions else ([], [])
        food_x, food_y = zip(*self.food_positions) if self.food_positions else ([], [])

        herbivore_scatter.set_offsets(np.c_[herb_x, herb_y])
        carnivore_scatter.set_offsets(np.c_[carn_x, carn_y])
        food_scatter.set_offsets(np.c_[food_x, food_y])

        herbivores = [o for o in self.organisms if not o.cannibalism]
        carnivores = [o for o in self.organisms if o.cannibalism]

        self.trait_history['herbivore_food_gene'].append(np.mean([o.food_gene for o in herbivores]) if herbivores else 0)
        self.trait_history['herbivore_speed'].append(np.mean([o.speed for o in herbivores]) if herbivores else 0)
        self.trait_history['herbivore_lifespan'].append(np.mean([o.lifespan for o in herbivores]) if herbivores else 0)
        self.trait_history['herbivore_energy_efficiency'].append(np.mean([o.energy_efficiency for o in herbivores]) if herbivores else 0)
        self.trait_history['herbivore_memory'].append(np.mean([o.memory for o in herbivores]) if herbivores else 0)
        self.trait_history['herbivore_fear'].append(np.mean([o.fear for o in herbivores]) if herbivores else 0)
        self.trait_history['carnivore_food_gene'].append(np.mean([o.food_gene for o in carnivores]) if carnivores else 0)
        self.trait_history['carnivore_speed'].append(np.mean([o.speed for o in carnivores]) if carnivores else 0)
        self.trait_history['carnivore_lifespan'].append(np.mean([o.lifespan for o in carnivores]) if carnivores else 0)
        self.trait_history['carnivore_energy_efficiency'].append(np.mean([o.energy_efficiency for o in carnivores]) if carnivores else 0)

        # Log population, collisions, lifespans, and memory
        if frame % 100 == 0:
            print(f"Frame {frame}: Herbivores={len(herbivores)}, Carnivores={len(carnivores)}, "
                  f"Collisions={collisions}, Avg Memory={self.trait_history['herbivore_memory'][-1]:.3f}, "
                  f"Avg Fear={self.trait_history['herbivore_fear'][-1]:.3f}, "
                  f"Avg Herbivore Lifespan={self.trait_history['herbivore_lifespan'][-1]:.1f}, "
                  f"Avg Carnivore Lifespan={self.trait_history['carnivore_lifespan'][-1]:.1f}")

        memory = self.trait_history['herbivore_memory'][-1]
        fear = self.trait_history['herbivore_fear'][-1]
        self.memory_fear_history.append((memory, fear))
        memory_values, fear_values = zip(*self.memory_fear_history) if self.memory_fear_history else ([], [])
        memory_fear_scatter.set_offsets(np.c_[memory_values, fear_values])

        herbivore_traits = ['herbivore_speed', 'herbivore_energy_efficiency', 'herbivore_lifespan']
        for i, key in enumerate(herbivore_traits[:2]):
            herbivore_trait_lines[i].set_data(range(len(self.trait_history[key])), self.trait_history[key])
        herbivore_trait_lines[2].set_data(range(len(self.trait_history['herbivore_lifespan'])), self.trait_history['herbivore_lifespan'])

        carnivore_traits = ['carnivore_speed', 'carnivore_energy_efficiency', 'carnivore_lifespan']
        for i, key in enumerate(carnivore_traits[:2]):
            carnivore_trait_lines[i].set_data(range(len(self.trait_history[key])), self.trait_history[key])
        carnivore_trait_lines[2].set_data(range(len(self.trait_history['carnivore_lifespan'])), self.trait_history['carnivore_lifespan'])

        food_gene_keys = ['herbivore_food_gene', 'carnivore_food_gene']
        for i, key in enumerate(food_gene_keys):
            food_gene_lines[i].set_data(range(len(self.trait_history[key])), self.trait_history[key])

        memory_fear_lifespan_traits = ['herbivore_memory', 'herbivore_fear', 'herbivore_lifespan']
        for i, key in enumerate(memory_fear_lifespan_traits[:2]):
            herbivore_memory_fear_lifespan_lines[i].set_data(range(len(self.trait_history[key])), self.trait_history[key])
        herbivore_memory_fear_lifespan_lines[2].set_data(range(len(self.trait_history['herbivore_lifespan'])), self.trait_history['herbivore_lifespan'])

        return [herbivore_scatter, carnivore_scatter, food_scatter, memory_fear_scatter] + herbivore_trait_lines + carnivore_trait_lines + food_gene_lines + herbivore_memory_fear_lifespan_lines

    def animate(self, fig, grid_ax, memory_fear_ax, herbivore_memory_fear_lifespan_ax, herbivore_trait_ax, carnivore_trait_ax, food_gene_ax):
        grid_ax.set_xticks(np.arange(0, self.size, 1), minor=True)
        grid_ax.set_yticks(np.arange(0, self.size, 1), minor=True)
        grid_ax.grid(which="minor", color="gray", linestyle="-", linewidth=0.1)
        grid_ax.set_xticks([])
        grid_ax.set_yticks([])
        grid_ax.set_xlim(0, self.size)
        grid_ax.set_ylim(0, self.size)

        herbivore_scatter = grid_ax.scatter([], [], c='blue', s=20, marker='s', label="Herbivores")
        carnivore_scatter = grid_ax.scatter([], [], c='red', s=30, marker='o', label="Carnivores")
        food_scatter = grid_ax.scatter([], [], c='green', s=30, marker='x', label="Food")
        grid_ax.legend(loc="upper right")
        grid_ax.set_title("Grid Simulation: Herbivores (Blue), Carnivores (Red)")

        memory_fear_scatter = memory_fear_ax.scatter([], [], c='purple', s=50, alpha=0.5)
        memory_fear_ax.set_xlim(0, 1)
        memory_fear_ax.set_ylim(0, 1)
        memory_fear_ax.set_xlabel('Herbivore Memory')
        memory_fear_ax.set_ylabel('Herbivore Fear', fontsize=10, labelpad=2)
        memory_fear_ax.set_title('Memory vs. Fear (All Time Steps)')
        memory_fear_ax.grid(True)

        herbivore_memory_fear_lifespan_lines = []
        memory_fear_lifespan_traits = ['herbivore_memory', 'herbivore_fear']
        for key in memory_fear_lifespan_traits:
            line, = herbivore_memory_fear_lifespan_ax.plot([], [], label=key.replace('_', ' ').title())
            herbivore_memory_fear_lifespan_lines.append(line)
        herbivore_memory_fear_lifespan_ax.set_xlim(0, 1000)
        herbivore_memory_fear_lifespan_ax.set_ylim(0, 1)
        herbivore_memory_fear_lifespan_ax.set_xlabel('Time Steps')
        herbivore_memory_fear_lifespan_ax.set_ylabel('Memory / Fear', fontsize=10, labelpad=2)
        herbivore_memory_fear_lifespan_ax.grid(True)

        herbivore_memory_fear_lifespan_ax2 = herbivore_memory_fear_lifespan_ax.twinx()
        line, = herbivore_memory_fear_lifespan_ax2.plot([], [], label='Herbivore Lifespan', linestyle='--')
        herbivore_memory_fear_lifespan_lines.append(line)
        herbivore_memory_fear_lifespan_ax2.set_ylim(0, 1000)
        herbivore_memory_fear_lifespan_ax2.set_ylabel('Lifespan', fontsize=10, labelpad=2)

        lines1, labels1 = herbivore_memory_fear_lifespan_ax.get_legend_handles_labels()
        lines2, labels2 = herbivore_memory_fear_lifespan_ax2.get_legend_handles_labels()
        herbivore_memory_fear_lifespan_ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        herbivore_memory_fear_lifespan_ax.set_title('Herbivore Memory, Fear, Lifespan')

        herbivore_trait_lines = []
        herbivore_traits = ['herbivore_speed', 'herbivore_energy_efficiency']
        for key in herbivore_traits:
            line, = herbivore_trait_ax.plot([], [], label=key.replace('_', ' ').title())
            herbivore_trait_lines.append(line)
        herbivore_trait_ax.set_xlim(0, 1000)
        herbivore_trait_ax.set_ylim(0, 2)
        herbivore_trait_ax.set_xlabel('Time Steps')
        herbivore_trait_ax.set_ylabel('Speed / Energy Efficiency', fontsize=10, labelpad=2)
        herbivore_trait_ax.grid(True)

        herbivore_trait_ax2 = herbivore_trait_ax.twinx()
        line, = herbivore_trait_ax2.plot([], [], label='Herbivore Lifespan', linestyle='--')
        herbivore_trait_lines.append(line)
        herbivore_trait_ax2.set_ylim(0, 1000)
        herbivore_trait_ax2.set_ylabel('Lifespan', fontsize=10, labelpad=2)

        lines1, labels1 = herbivore_trait_ax.get_legend_handles_labels()
        lines2, labels2 = herbivore_trait_ax2.get_legend_handles_labels()
        herbivore_trait_ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        herbivore_trait_ax.set_title('Herbivore Traits')

        carnivore_trait_lines = []
        carnivore_traits = ['carnivore_speed', 'carnivore_energy_efficiency']
        for key in carnivore_traits:
            line, = carnivore_trait_ax.plot([], [], label=key.replace('_', ' ').title())
            carnivore_trait_lines.append(line)
        carnivore_trait_ax.set_xlim(0, 1000)
        carnivore_trait_ax.set_ylim(0, 2)
        carnivore_trait_ax.set_xlabel('Time Steps')
        carnivore_trait_ax.set_ylabel('Speed / Energy Efficiency', fontsize=10, labelpad=2)
        carnivore_trait_ax.grid(True)

        carnivore_trait_ax2 = carnivore_trait_ax.twinx()
        line, = carnivore_trait_ax2.plot([], [], label='Carnivore Lifespan', linestyle='--')
        carnivore_trait_lines.append(line)
        carnivore_trait_ax2.set_ylim(0, 1000)
        carnivore_trait_ax2.set_ylabel('Lifespan', fontsize=10, labelpad=2)

        lines1, labels1 = carnivore_trait_ax.get_legend_handles_labels()
        lines2, labels2 = carnivore_trait_ax2.get_legend_handles_labels()
        carnivore_trait_ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        carnivore_trait_ax.set_title('Carnivore Traits')

        food_gene_lines = []
        food_gene_keys = ['herbivore_food_gene', 'carnivore_food_gene']
        for key in food_gene_keys:
            line, = food_gene_ax.plot([], [], label=key.replace('_', ' ').title())
            food_gene_lines.append(line)
        food_gene_ax.set_xlim(0, 1000)
        food_gene_ax.set_ylim(0, 1)
        food_gene_ax.set_xlabel('Time Steps')
        food_gene_ax.set_ylabel('Food Gene', fontsize=10, labelpad=2)
        food_gene_ax.set_title('Food Genes Over Time')
        food_gene_ax.legend(loc='upper left')
        food_gene_ax.grid(True)

        ani = animation.FuncAnimation(
            fig, self.update, interval=100,
            fargs=(herbivore_scatter, carnivore_scatter, food_scatter,
                   memory_fear_scatter, herbivore_trait_lines, carnivore_trait_lines,
                   food_gene_lines, herbivore_memory_fear_lifespan_lines),
            blit=True
        )
        plt.show()