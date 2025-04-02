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
        self.food_touch_time = {}  # Track when an organism first touches food
        self.organism_timers = {}
        self.food_timer = 200 # Hyperparameter # Track how long since an organism last touched food

    def spawn_food(self):
        return [tuple(pos) for pos in np.random.randint(0, self.size, (15, 2))]

    def add_organisms(self, organisms):
        self.organisms = organisms
        for org in self.organisms:
            self.organism_timers[org] = 0

    def position(self):
        x_vals = [org.x for org in self.organisms]
        y_vals = [org.y for org in self.organisms]
        return [x_vals, y_vals]

    def update(self, frame, scatter, food_scatter):
        new_organisms = []
        to_remove = []
        coordinates = []
        for idx,org in enumerate(self.organisms):

            org.move(self.food_positions)
            (x,y)= org.coordinates()
            coordinates.append(f'Coordintate of org {idx} is {(x,y)}')

            pos = (org.x, org.y)

            if org not in self.organism_timers:
                self.organism_timers[org] = frame  # Initialize starvation timer

            if pos in self.food_positions and org not in self.food_touch_time:
                self.food_touch_time[org] = frame
                self.food_positions.remove(pos)  # Remove food immediately after touch
                self.organism_timers[org] = frame  # Reset starvation timer
                print("The organism touched the food")

            # Divide if organism touched food 50 frames ago
            if org in self.food_touch_time and frame - self.food_touch_time[org] >= 50:
                new_organisms.append(org.division())
                #new_organisms.append(org.division())
               # new_organisms.append(org.division())
                del self.food_touch_time[org]

            # Increment starvation timer
            if org in self.organism_timers:
                starvation_time = frame - self.organism_timers[org]
            else:
                starvation_time = 0

            # Kill organism if no food in 500 frames
            if starvation_time >= 100:
                to_remove.append(org)

        # Remove dead organisms
        for org in to_remove:
            self.organisms.remove(org)
            self.organism_timers.pop(org, None)
            self.food_touch_time.pop(org, None)

        # Add new organisms
        self.organisms.extend(new_organisms)

        # Respawn food every 300 frames
        if frame - self.last_food_spawn_time >= self.food_timer and len(self.food_positions) == 0:
            self.food_positions = self.spawn_food()
            self.last_food_spawn_time = frame

        # Update scatter plot
        org_positions = self.position()
        scatter.set_offsets(np.c_[org_positions[0], org_positions[1]])
        food_x, food_y = zip(*self.food_positions) if self.food_positions else ([], [])
        food_scatter.set_offsets(np.c_[food_x, food_y])
        print(coordinates)

        return scatter, food_scatter

    def animate(self, fig, ax):
        ax.set_xticks(np.arange(0, self.size, 1), minor=True)
        ax.set_yticks(np.arange(0, self.size, 1), minor=True)
        ax.grid(which="minor", color="gray", linestyle="-", linewidth=0.1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(0, self.size)
        ax.set_ylim(0, self.size)

        food_scatter = ax.scatter([], [], c='green', s=30)
        scatter = ax.scatter([], [], c='red', s=20,marker='s')
        ax.set_facecolor('blue')


        ani = animation.FuncAnimation(fig, self.update, interval=100, fargs=(scatter, food_scatter), blit=True)
        plt.show()
