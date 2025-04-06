import random
import numpy as np

class Organism:
    def __init__(self, x, y, grid_size, speed):
        self.x = x
        self.y = y
        self.grid_size = grid_size
        self.speed = speed
        self.food_count = 0
        self.birth_time = 0
        self.death_time = None

    def get_speed(self):
        return self.speed

    def move_random(self):
        direction = random.choice(["up", "down", "left", "right"])
        if direction == "up" and self.y < self.grid_size - 1:
            self.y += 1
        elif direction == "down" and self.y > 0:
            self.y -= 1
        elif direction == "left" and self.x > 0:
            self.x -= 1
        elif direction == "right" and self.x < self.grid_size - 1:
            self.x += 1

    def move_towards_food(self, food_positions):
        if not food_positions:
            self.move_random()
            return

        nearest_food = min(food_positions, key=lambda f: (f[0] - self.x)**2 + (f[1] - self.y)**2)
        dx = np.sign(nearest_food[0] - self.x)
        dy = np.sign(nearest_food[1] - self.y)

        if random.random() < self.speed:
            self.x = max(0, min(self.grid_size - 1, self.x + dx))
            self.y = max(0, min(self.grid_size - 1, self.y + dy))
        else:
            self.move_random()

    def move(self, food_positions):
        self.move_towards_food(food_positions)

    def division(self):
        child = Organism(self.x, self.y, self.grid_size, self.speed)
        child.birth_time = self.birth_time
        return child
