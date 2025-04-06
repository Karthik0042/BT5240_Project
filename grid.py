import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Grid:
    def __init__(self, size, time_steps):
        self.size = size
        self.time_steps = time_steps
        self.last_division_time = 0
        self.last_food_spawn_time = 0
        self.organisms = []
        self.food_positions = self.spawn_food()
        self.food_touch_time = {}
        self.organism_timers = {}
        self.food_timer = 200
        self.population_history = []
        self.avg_speed_history = []
        self.food_count_history = []
        self.organism_speeds = {}
        self.running = True
        self.speed_data = []  # Track organism speeds
        self.survival_data = []  # Track lifespan
        self.food_interactions = {}  # Track food touches per organism
        self.frame_count = 0 #Keeps count

    def spawn_food(self):
        return [tuple(pos) for pos in np.random.randint(0, self.size, (50, 2))]

    def add_organisms(self, organisms):
        self.organisms = organisms
        for org in self.organisms:
            org.birth_time = 0
            self.organism_timers[org] = 0
            self.organism_speeds[org] = org.get_speed()
            self.speed_data.append(org.speed)
            self.food_interactions[org] = 0 # Initialize food interactions for each organism

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
            if org in self.food_touch_time and frame - self.food_touch_time[org] >= 50:
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
        self.avg_speed_history.append(avg_speed)
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
        return self.population_history, self.avg_speed_history, self.food_count_history, self.food_interactions

    def plot_graphs(self, population_history, avg_speed_history, food_count_history, food_interactions):
        fig, axs = plt.subplots(4, 1, figsize=(8, 12),dpi=100)

        # Population History
        axs[0].plot(population_history)
        axs[0].set_title('Population Size Over Time')
        axs[0].set_xlabel('Time Step')
        axs[0].set_ylabel('Population Size')

        # Average Speed History
        axs[1].plot(avg_speed_history, color='green')
        axs[1].set_title('Average Speed Over Time')
        axs[1].set_xlabel('Time Step')
        axs[1].set_ylabel('Average Speed')

        # Food Count History
        axs[2].plot(food_count_history, color='red')
        axs[2].set_title('Food Count Over Time')
        axs[2].set_xlabel('Time Step')
        axs[2].set_ylabel('Food Count')

        # Food Interactions
        interactions = list(food_interactions.values())
        axs[3].hist(interactions, bins=20, alpha=0.7, color='purple')
        axs[3].set_title('Food Interaction Distribution')
        axs[3].set_xlabel('Number of Food Touches')
        axs[3].set_ylabel('Number of Organisms')

        plt.tight_layout()
        plt.show()
