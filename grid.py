import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Grid:
    def __init__(self, size, time_steps, reproduction_time):
        self.size = size
        self.time_steps = time_steps
        self.reproduction_time = reproduction_time
        self.last_division_time = 0
        self.last_food_spawn_time = 0
        self.organisms = []
        self.food_positions = self.spawn_food()
        self.food_touch_time = {}
        self.organism_timers = {}
        self.food_timer = 150
        self.population_history = []
        self.avg_speed_history = []
        self.avg_food_gene_history = []  # New
        self.food_count_history = []
        self.organism_speeds = {}
        self.running = True
        self.speed_data = []  # Track organism speeds
        self.survival_data = []  # Track lifespan
        self.food_interactions = {}  # Track food touches per organism
        self.frame_count = 0  # Keeps count

    def spawn_food(self):
        return [tuple(pos) for pos in np.random.randint(0, self.size, (50, 2))]

    def add_organisms(self, organisms):
        self.organisms = organisms
        for org in self.organisms:
            org.birth_time = 0
            self.organism_timers[org] = 0
            self.organism_speeds[org] = org.get_speed()
            self.speed_data.append(org.speed)
            self.food_interactions[org] = 0  # Initialize food interactions for each organism

    def position(self):
        x_vals = [org.x for org in self.organisms]
        y_vals = [org.y for org in self.organisms]
        return [x_vals, y_vals]

    def update(self, frame, scatter, food_scatter):
        if not self.running:
            return scatter, food_scatter

        new_organisms = []
        to_remove = []

        for idx, org in enumerate(self.organisms):
            org.move(self.food_positions)
            pos = (org.x, org.y)

            if org not in self.organism_timers:
                self.organism_timers[org] = frame

            if pos in self.food_positions and org not in self.food_touch_time:
                self.food_touch_time[org] = frame
                if org not in self.food_interactions:
                    self.food_interactions[org] = 0
                self.food_interactions[org] += 1
                if pos in self.food_positions:
                    self.food_positions.remove(pos)
                self.organism_timers[org] = frame

            # Division Logic
            if org in self.food_touch_time and frame - self.food_touch_time[org] >= self.reproduction_time:
                new_organisms.append(org.division())
                del self.food_touch_time[org]
                self.last_division_time = frame

            starvation_time = frame - self.organism_timers.get(org, 0)
            if starvation_time >= 100:
                to_remove.append(org)

        for org in to_remove:
            self.organisms.remove(org)
            self.organism_timers.pop(org, None)
            self.food_touch_time.pop(org, None)
            if org in self.organism_speeds:
                del self.organism_speeds[org]
            org.death_time = frame
            self.survival_data.append((org.speed, org.death_time - org.birth_time))

        for new_org in new_organisms:
            self.organism_speeds[new_org] = new_org.get_speed()
            self.food_interactions[new_org] = 0
        self.organisms.extend(new_organisms)

        if frame - self.last_food_spawn_time >= self.food_timer:
            self.food_positions.extend(self.spawn_food())
            self.last_food_spawn_time = frame

        org_positions = self.position()
        scatter.set_offsets(np.c_[org_positions[0], org_positions[1]])
        food_x, food_y = zip(*self.food_positions) if self.food_positions else ([], [])
        food_scatter.set_offsets(np.c_[food_x, food_y])

        self.population_history.append(len(self.organisms))
        avg_speed = np.mean([org.get_speed() for org in self.organisms]) if self.organisms else 0
        avg_food_gene = np.mean([org.get_food_gene() for org in self.organisms]) if self.organisms else 0
        self.avg_speed_history.append(avg_speed)
        self.avg_food_gene_history.append(avg_food_gene)  # new
        self.food_count_history.append(len(self.food_positions))

        if len(self.organisms) == 0:
            self.running = False
            print("All organisms are gone! Stopping animation.")

        return scatter, food_scatter

    def animate(self, fig, ax):
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(0, self.size)
        ax.set_ylim(0, self.size)
        food_scatter = ax.scatter([], [], c='green', s=30)
        scatter = ax.scatter([], [], c='red', s=20, marker='s')
        ani = animation.FuncAnimation(fig, self.update, frames=self.time_steps, interval=100, fargs=(scatter, food_scatter), blit=False, repeat=False)
        plt.show()
        return self.population_history, self.avg_speed_history, self.avg_food_gene_history, self.food_count_history, self.food_interactions

    def plot_graphs(self, population_history, avg_speed_history, avg_food_gene_history, food_count_history, food_interactions):
        # 1. Population History (Growth Curve)
        plt.figure(figsize=(8, 6), dpi=100)
        plt.plot(population_history)
        plt.title('Population Size Over Time (Growth Curve)')
        plt.xlabel('Time Step')
        plt.ylabel('Population Size')
        plt.show()

        # 2. Speed vs Time
        plt.figure(figsize=(8, 6), dpi=100)
        plt.plot(avg_speed_history, color='green')
        plt.title('Average Speed Over Time')
        plt.xlabel('Time Step')
        plt.ylabel('Average Speed')
        plt.show()

        # 3. Food Detection Value (food_gene) vs Time
        plt.figure(figsize=(8, 6), dpi=100)
        plt.plot(avg_food_gene_history, color='purple')
        plt.title('Average Food Detection (food_gene) Over Time')
        plt.xlabel('Time Step')
        plt.ylabel('Average Food Detection Value')
        plt.show()
