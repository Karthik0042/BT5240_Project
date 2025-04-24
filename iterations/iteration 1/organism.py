import random
import numpy as np

class Organism:
    def __init__(self, x, y, grid_size, canbalism=False):
        self.x = x
        self.y = y
        self.grid_size = grid_size
        self.food_gene = 0.2
        self.speed = 0.3
        self.canbalism = canbalism
        self.carnivore_detection = 5  # Used only by herbivores
        self.age = 0
        self.lifespan = np.random.randint(150, 300) if not canbalism else np.random.randint(800, 950)

    def gene_food(self, food_positions):
        return self.food_gene if food_positions else 0.0

    def detect_and_flee(self, other_organisms):
        nearest_threat = None
        min_distance = float('inf')

        for org in other_organisms:
            if org.canbalism:
                dist = abs(org.x - self.x) + abs(org.y - self.y)
                if dist <= self.carnivore_detection and dist < min_distance:
                    nearest_threat = org
                    min_distance = dist

        if nearest_threat:
            dx = -np.sign(nearest_threat.x - self.x)
            dy = -np.sign(nearest_threat.y - self.y)
            self.x = max(0, min(self.grid_size - 1, self.x + dx))
            self.y = max(0, min(self.grid_size - 1, self.y + dy))
            return True
        return False

    def move_towards_food(self, food_positions):
        if not food_positions or self.food_gene == 0.0:
            self.move_random()
            return

        nearest_food = min(food_positions, key=lambda f: abs(f[0] - self.x) + abs(f[1] - self.y))
        dx = np.sign(nearest_food[0] - self.x)
        dy = np.sign(nearest_food[1] - self.y)

        if random.random() < self.food_gene:
            move_direction = random.choice([(dx, 0), (0, dy)]) if dx and dy else (dx, dy)
            self.x = max(0, min(self.grid_size - 1, self.x + move_direction[0]))
            self.y = max(0, min(self.grid_size - 1, self.y + move_direction[1]))
        else:
            self.move_random()

    def move_towards_prey(self, other_organisms):
        herbivores = [o for o in other_organisms if not o.canbalism]
        if not herbivores or random.random() > self.food_gene:
            self.move_random()
            return

        nearest_prey = min(herbivores, key=lambda o: abs(o.x - self.x) + abs(o.y - self.y))
        dx = np.sign(nearest_prey.x - self.x)
        dy = np.sign(nearest_prey.y - self.y)

        move_direction = random.choice([(dx, 0), (0, dy)]) if dx and dy else (dx, dy)
        self.x = max(0, min(self.grid_size - 1, self.x + move_direction[0]))
        self.y = max(0, min(self.grid_size - 1, self.y + move_direction[1]))

    def move_random(self):
        direction = random.choice(["up", "down", "left", "right"])
        if random.random() < self.speed:
            if direction == "up" and self.y < self.grid_size - 1:
                self.y += 1
            elif direction == "down" and self.y > 0:
                self.y -= 1
            elif direction == "left" and self.x > 0:
                self.x -= 1
            elif direction == "right" and self.x < self.grid_size - 1:
                self.x += 1

    def move(self, food_positions, other_organisms):
        self.age += 1
        if self.canbalism:
            self.move_towards_prey(other_organisms)
            return
        if self.detect_and_flee(other_organisms):
            return
        self.food_gene = self.gene_food(food_positions)
        if self.food_gene > 0.0:
            self.move_towards_food(food_positions)
        else:
            self.move_random()

    def is_dead(self):
        return self.age >= self.lifespan

    def division(self):
        offspring = Organism(self.x, self.y, self.grid_size, canbalism=self.canbalism)
        offspring.food_gene = self.food_gene + np.random.normal(0, 0.1)
        offspring.speed = self.speed + np.random.normal(0, 0.1)

        if not self.canbalism:
            offspring.canbalism = random.random() < 0.1
            offspring.carnivore_detection = self.carnivore_detection + np.random.normal(0, 0.5)
            offspring.lifespan = max(30, self.lifespan + int(np.random.normal(0, 10)))
            offspring.carnivore_detection = self.carnivore_detection +np.random.normal(0.5,1)
        else:
            offspring.lifespan = max(50, self.lifespan + int(np.random.normal(0, 5)))
        return offspring
