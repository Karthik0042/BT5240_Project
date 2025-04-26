import random
import numpy as np

class Organism:
    def __init__(self, x, y, grid_size, cannibalism=False):
        self.x = x
        self.y = y
        self.grid_size = grid_size
        self.food_gene = 0.15
        self.speed = 0.3
        self.cannibalism = cannibalism
        self.carnivore_detection = 9  # Increased from 7
        self.age = 0
        self.lifespan = np.random.randint(875, 1000) if not cannibalism else np.random.randint(750, 950)  # Reduced from 800–950
        self.memory = 0.25 if not cannibalism else 0.0
        self.fear = 0.75 if not cannibalism else 0.0
        self.known_carnivores = set() if not cannibalism else None
        self.last_food_location = None
        self.memory_timer = 0
        self.memory_decay_base = 125
        self.visibility_radius = 4.75
        self.communication_radius = 6.5
        self.energy_efficiency = 1.0

    def gene_food(self, food_positions):
        return self.food_gene if food_positions else 0.0

    def detect_and_flee(self, other_organisms):
        nearest_threat = None
        min_distance = float('inf')

        for org in other_organisms:
            if org in self.known_carnivores:
                dist = abs(org.x - self.x) + abs(org.y - self.y)
                if dist <= self.carnivore_detection and dist < min_distance:
                    nearest_threat = org
                    min_distance = dist

        if nearest_threat:
            self.fear = min(1.0, self.fear + 0.45)  # Increased from 0.3
            effective_speed = self.speed * (1 + self.fear)
            if random.random() < effective_speed:
                dx = -np.sign(nearest_threat.x - self.x)
                dy = -np.sign(nearest_threat.y - self.y)
                self.x = max(0, min(self.grid_size - 1, self.x + dx))
                self.y = max(0, min(self.grid_size - 1, self.y + dy))
            return True
        return False

    def move_towards_food(self, food_positions):
        if not food_positions and self.last_food_location and random.random() < self.memory:
            nearest_food = self.last_food_location
        elif food_positions:
            nearest_food = min(food_positions, key=lambda f: abs(f[0] - self.x) + abs(f[1] - self.y))
        else:
            self.move_random()
            return

        dx = np.sign(nearest_food[0] - self.x)
        dy = np.sign(nearest_food[1] - self.y)

        if random.random() < self.food_gene:
            move_direction = random.choice([(dx, 0), (0, dy)]) if dx and dy else (dx, dy)
            self.x = max(0, min(self.grid_size - 1, self.x + move_direction[0]))
            self.y = max(0, min(self.grid_size - 1, self.y + move_direction[1]))
        else:
            self.move_random()

    def move_towards_prey(self, other_organisms):
        herbivores = [o for o in other_organisms if not o.cannibalism]
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

    def move(self, food_positions, other_organisms, movement_cost=1.0):
        self.age += movement_cost * (1 + self.fear)
        if self.last_food_location:
            self.memory_timer += 1
            memory_decay = self.memory_decay_base * (1 - self.fear)
            if self.memory_timer >= memory_decay or random.random() > self.memory:
                self.last_food_location = None
                self.memory_timer = 0
        self.fear = max(0.0, self.fear - 0.05)

        if self.cannibalism:
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
        offspring = Organism(self.x, self.y, self.grid_size, cannibalism=self.cannibalism)
        offspring.food_gene = max(0, min(1, self.food_gene + np.random.normal(0, 0.1)))
        offspring.speed = max(0, min(1, self.speed + np.random.normal(0, 0.15)))
        offspring.energy_efficiency = max(0.5, min(1.5, self.energy_efficiency + np.random.normal(0, 0.05)))
        if not self.cannibalism:
            memory_mutation = np.random.normal(0, 0.1)
            offspring.memory = max(0, min(1, self.memory + memory_mutation))
            offspring.fear = max(0, min(1, self.fear - memory_mutation * 0.5))
            offspring.cannibalism = random.random() < 0.1
            offspring.carnivore_detection = max(1, self.carnivore_detection + np.random.normal(0, 0.5))
            offspring.lifespan = max(30, self.lifespan + int(np.random.normal(0, 10)))
            offspring.lifespan = int(offspring.lifespan * (1 - self.fear * 0.5))
            offspring.visibility_radius = max(1, self.visibility_radius + np.random.normal(0, 0.5))
            offspring.communication_radius = max(1, self.communication_radius + np.random.normal(0, 0.5))
        else:
            offspring.lifespan = max(50, self.lifespan + int(np.random.normal(0, 5)))
        return offspring

    def witness_cannibalization(self, carnivore, prey_pos):
        dist = abs(prey_pos[0] - self.x) + abs(prey_pos[1] - self.y)
        if dist <= self.visibility_radius:
            self.known_carnivores.add(carnivore)
            self.fear = min(1.0, self.fear + 0.55)  # Increased from 0.4
            return True
        return False

    def communicate_carnivore(self, other_organisms, carnivore):
        for org in other_organisms:
            if not org.cannibalism and org != self:
                dist = abs(org.x - self.x) + abs(org.y - self.y)
                if dist <= self.communication_radius:
                    org.known_carnivores.add(carnivore)
                    org.fear = min(1.0, org.fear + 0.45)  # Increased from 0.3