import random
import numpy as np

class Organism:
    def __init__(self, x, y, grid_size, cannibalism=False):
        self.x = x
        self.y = y
        self.grid_size = grid_size
        self.cannibalism = cannibalism
        self.rest_timer = 0  # New: Rest period counter

        # Base traits
        self.food_gene = 0.15
        self.speed = 0.3 if not cannibalism else 0.5
        self.carnivore_detection = 9 if not cannibalism else 0

        # Lifespan and aging
        self.age = 0
        self.lifespan = np.random.randint(875, 1000) if not cannibalism else np.random.randint(900, 1200)

        # Herbivore-specific traits
        self.memory = 0.3 if not cannibalism else 0.0
        self.fear = 0.5 if not cannibalism else 0.0
        self.known_carnivores = set() if not cannibalism else None

        # Memory system
        self.last_food_location = None
        self.memory_timer = 0
        self.memory_decay_base = 150
        self.visibility_radius = 5
        self.communication_radius = 7

        # Energy and metabolism
        self.energy_efficiency = 1.0
        self.frames_since_last_food = 0

    def gene_food(self, food_positions):
        return self.food_gene if food_positions else 0.0

    def detect_and_flee(self, other_organisms):
        if not self.known_carnivores:
            return False

        nearest_threat = None
        min_distance = float('inf')

        # Dynamic detection range based on fear (PMC7196326)
        effective_detection = self.carnivore_detection * (1 + 0.5 * self.fear)

        for org in other_organisms:
            if org in self.known_carnivores:
                dist = abs(org.x - self.x) + abs(org.y - self.y)
                if dist <= effective_detection and dist < min_distance:
                    nearest_threat = org
                    min_distance = dist

        if nearest_threat:
            # Sigmoid fear response (WorldScientific)
            fear_increase = 0.8 / (1 + np.exp(-0.5 * (min_distance - 3)))
            self.fear = min(1.0, self.fear + fear_increase)

            # Energy cost of fleeing (Frontiers)
            self.energy_efficiency = max(0.5, self.energy_efficiency - 0.1 * fear_increase)

            # Movement probability with diminishing returns (PMC7196326)
            effective_speed = self.speed * (1 + 2.5 * (self.fear ** 0.7))
            if random.random() < effective_speed:
                dx = -np.sign(nearest_threat.x - self.x)
                dy = -np.sign(nearest_threat.y - self.y)
                self.x = max(0, min(self.grid_size - 1, self.x + dx))
                self.y = max(0, min(self.grid_size - 1, self.y + dy))
            return True
        return False

    def move_towards_food(self, food_positions):
        if not food_positions and self.last_food_location and random.random() < self.memory:
            target_food = self.last_food_location
        elif food_positions:
            target_food = min(food_positions, key=lambda f: abs(f[0] - self.x) + abs(f[1] - self.y))
            self.last_food_location = target_food
        else:
            self.move_random()
            return

        dx = np.sign(target_food[0] - self.x)
        dy = np.sign(target_food[1] - self.y)
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
        self.frames_since_last_food += 1
        if not self.cannibalism:
            self.communicate_carnivore(other_organisms)

        # Handle resting period for carnivores
        if self.cannibalism and self.rest_timer > 0:
            self.rest_timer -= 1
            return

        # Memory system
        if self.last_food_location:
            self.memory_timer += 1
            memory_decay = self.memory_decay_base * (1 - 0.6 * self.fear)
            if self.memory_timer >= memory_decay or random.random() > self.memory:
                self.last_food_location = None
                self.memory_timer = 0

        # Fear decay
        self.fear = max(0.0, self.fear - 0.05)

        if self.cannibalism:
            self.move_towards_prey(other_organisms)
        elif not self.detect_and_flee(other_organisms):
            self.food_gene = self.gene_food(food_positions)
            if self.food_gene > 0.0:
                self.move_towards_food(food_positions)
            else:
                self.move_random()

    def is_dead(self):
        return self.age >= self.lifespan

    def division(self, carnivores_exist=False):
        offspring = Organism(self.x, self.y, self.grid_size, cannibalism=self.cannibalism)
        offspring.known_carnivores = set() if not offspring.cannibalism else None

        # Reproduction thresholds
        if not self.cannibalism and self.frames_since_last_food >= 40:
            self.frames_since_last_food = 0
        elif self.cannibalism and self.frames_since_last_food >= 60:
            self.frames_since_last_food = 0

        # Mutation system
        speed_mut = np.random.normal(0, 0.1)
        offspring.speed = max(0.1, self.speed + speed_mut)
        offspring.energy_efficiency = max(0.5, self.energy_efficiency * np.exp(-abs(speed_mut)))

        food_mut = np.random.normal(0, 0.05)
        offspring.food_gene = max(0.05, self.food_gene + food_mut)

        if not self.cannibalism:
            mem_mut = np.random.normal(0, 0.1)
            offspring.memory = max(0, self.memory + mem_mut)
            offspring.fear = max(0, self.fear - mem_mut * 0.5)
            offspring.lifespan *= (1 - 0.3 * self.fear)
            offspring.food_gene *= (1 - 0.2 * self.fear)

            det_mut = np.random.normal(0, 0.3)
            offspring.carnivore_detection = max(1, self.carnivore_detection + det_mut)
            offspring.lifespan = max(100, self.lifespan * np.exp(-abs(det_mut) / 10))

            vis_mut = np.random.normal(0, 0.4)
            offspring.visibility_radius = max(1, self.visibility_radius + vis_mut)
            offspring.communication_radius = max(1, self.communication_radius * np.exp(-abs(vis_mut) / 5))

            mutation_chance = 0.05 if carnivores_exist else 0.15
            offspring.cannibalism = random.random() < mutation_chance
        else:
            accuracy_mut = np.random.normal(0, 0.05)
            offspring.food_gene = max(0.05, self.food_gene + accuracy_mut)
            offspring.speed = max(0.2, self.speed * np.exp(-abs(accuracy_mut) * 1.5))
            det_mut = np.random.normal(0, 0.2)
            offspring.carnivore_detection = max(1, self.carnivore_detection + det_mut)
            offspring.lifespan = max(150, self.lifespan * np.exp(-abs(det_mut) / 12))

        return offspring

    def witness_cannibalization(self, carnivore, prey_pos):
        dist = abs(prey_pos[0] - self.x) + abs(prey_pos[1] - self.y)
        if dist <= self.visibility_radius:
            self.known_carnivores.add(carnivore)
            self.fear = min(1.0, self.fear + 0.6)
            self.communicate_carnivore(carnivore)
            return True
        return False

    def communicate_carnivore(self, other_organisms):
        """Networked fear propagation using spatial decay"""
        comm_radius = self.communication_radius * (1 + 0.3 * self.fear)

        for org in other_organisms:
            if not org.cannibalism and org != self:
                dist = abs(org.x - self.x) + abs(org.y - self.y)
                if dist <= comm_radius:
                    # Transfer knowledge with spatial decay
                    org.known_carnivores.update(self.known_carnivores)

                    # Fear transfer (diminishes with distance)
                    fear_transfer = 0.4 * (1 - dist / comm_radius)
                    org.fear = min(1.0, org.fear + fear_transfer * (1 - org.fear))

                    # Collective memory enhancement
                    org.memory = min(1.0, org.memory + 0.1 * fear_transfer)


