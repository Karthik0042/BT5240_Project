import random
import numpy as np


class Organism:
    def __init__(self, x, y, grid_size):
        self.x = x
        self.y = y
        self.grid_size = grid_size
        self.food_gene = 0.0  # Determines movement behavior

    def gene_food(self, food_positions):
        gene_food = 0.5
        if not food_positions:
            return 0.0
        return gene_food  # For now, set to 1.0 if food exists, can be modified for evolution

    def move_towards_food(self, food_positions):
        if not food_positions or self.food_gene == 0.0:
            self.move_random()
            return

        # Find the nearest food source
        nearest_food = min(food_positions, key=lambda f: abs(f[0] - self.x) + abs(f[1] - self.y))
        dx = np.sign(nearest_food[0] - self.x)
        dy = np.sign(nearest_food[1] - self.y)

        # Move towards food with a slight randomness factor
        if random.random() < self.food_gene:  # Higher food_gene means stronger targeting
            if dx != 0 and dy != 0:
                move_direction = random.choice([(dx, 0), (0, dy)])
            else:
                move_direction = (dx, dy)
        else:
            self.move_random()
            return

        self.x = max(0, min(self.grid_size - 1, self.x + move_direction[0]))
        self.y = max(0, min(self.grid_size - 1, self.y + move_direction[1]))

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

    def move(self, food_positions):
        self.food_gene = self.gene_food(food_positions)
        if self.food_gene > 0.0:
            self.move_towards_food(food_positions)
        else:
            self.move_random()

    def division(self):
        offspring = Organism(self.x, self.y, self.grid_size)
        offspring.food_gene = self.food_gene  # Inherit gene
        return offspring