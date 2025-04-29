import random
import numpy as np

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

def convex_tradeoff(x, y, budget=1.0):
    return (x**0.7 + y**0.7) <= budget**0.7

def concave_tradeoff(x, y, budget=1.0):
    return (x**1.3 + y**1.3) <= budget**1.3

class Organism:
    _id_counter = 0

    def __init__(self, x, y, grid_size, cannibalism=False, lineage=None, generation=0):
        self.x = x
        self.y = y
        self.grid_size = grid_size
        self.cannibalism = cannibalism
        self.rest_timer = 0
        self.generation = generation

        self.id = Organism._id_counter
        Organism._id_counter += 1
        if cannibalism:
            if lineage is None:
                self.lineage = set([self.id])
            else:
                self.lineage = set(lineage)
                self.lineage.add(self.id)
        else:
            self.lineage = None

        # --- Early generations: all traits start low and similar, then improve ---
        if generation < 5:
            base = 0.13 + 0.04 * generation
            if not cannibalism:
                self.traits = {
                    "lifespan": base,
                    "speed": base,
                    "food_gene": base,
                    "carnivore_detection": base,
                    "memory": base,
                    "energy_efficiency": base,
                }
            else:
                self.traits = {
                    "lifespan": base,
                    "speed": base,
                    "stealth": base,
                    "energy_efficiency": base,
                    "food_gene": base,  # Ensure carnivores have food_gene from the start
                }
        else:
            if not cannibalism:
                raw = np.abs(np.random.normal([0.2, 0.2, 0.2, 0.2, 0.1, 0.1], 0.07, 6))
                alloc = softmax(raw)
                while not convex_tradeoff(alloc[0], alloc[1]):
                    raw = np.abs(np.random.normal([0.2, 0.2, 0.2, 0.2, 0.1, 0.1], 0.07, 6))
                    alloc = softmax(raw)
                self.traits = {
                    "lifespan": alloc[0],
                    "speed": alloc[1],
                    "food_gene": alloc[2],
                    "carnivore_detection": alloc[3],
                    "memory": alloc[4],
                    "energy_efficiency": alloc[5],
                }
            else:
                raw = np.abs(np.random.normal([0.25, 0.25, 0.25, 0.1, 0.15], 0.07, 5))
                alloc = softmax(raw)
                while not concave_tradeoff(alloc[1], alloc[2]):
                    raw = np.abs(np.random.normal([0.25, 0.25, 0.25, 0.1, 0.15], 0.07, 5))
                    alloc = softmax(raw)
                self.traits = {
                    "lifespan": alloc[0],
                    "speed": alloc[1],
                    "stealth": alloc[2],
                    "energy_efficiency": alloc[3],
                    "food_gene": alloc[4],  # Carnivores now evolve food_gene too
                }

        # --- Map trait allocations to actual values ---
        if not cannibalism:
            self.lifespan = int(500 + 1500 * self.traits["lifespan"])
            self.speed = 0.05 + 0.85 * self.traits["speed"]
            self.food_gene = 0.05 + 0.45 * self.traits["food_gene"]
            self.carnivore_detection = 2 + 12 * self.traits["carnivore_detection"]
            self.memory = 0.05 + 0.9 * self.traits["memory"]
            self.energy_efficiency = 0.5 + 0.5 * self.traits["energy_efficiency"]
            self.fear = 0.2
            self.known_carnivore_ids = set()
            self.carnivore_sense = np.clip(np.random.normal(0.8, 0.2), 0, 1)
            self.spatial_memory_capacity = int(2 + 6 * self.traits["memory"])
            self.spatial_memory = []
        else:
            self.lifespan = int(600 + 1200 * self.traits["lifespan"])
            self.speed = 0.1 + 0.8 * self.traits["speed"]
            self.stealth = 0.05 + 0.9 * self.traits["stealth"]
            self.energy_efficiency = 0.5 + 0.5 * self.traits["energy_efficiency"]
            self.food_gene = 0.05 + 0.45 * self.traits["food_gene"]  # Now evolves for carnivores
            self.hunting_strategy = random.choices(
                ["ambush", "pursuit"],
                weights=[self.stealth, self.speed]
            )[0]
            self.memory = 0.0
            self.fear = 0.0
            self.known_carnivore_ids = None
            self.carnivore_sense = 0.0

        self.memory_decay_base = 150
        self.visibility_radius = 5
        self.communication_radius = 7
        self.frames_since_last_food = 0
        self.age = 0

    def current_context(self):
        return {
            "fear": round(self.fear, 1),
            "carnivores_seen": len(self.known_carnivore_ids) if self.known_carnivore_ids is not None else 0,
        }

    def update_spatial_memory(self, food_pos, t):
        context = self.current_context()
        for mem in self.spatial_memory:
            if mem["pos"] == food_pos:
                mem["strength"] = 1.0
                mem["timestamp"] = t
                mem["context"] = context
                return
        if len(self.spatial_memory) >= self.spatial_memory_capacity:
            weakest = min(self.spatial_memory, key=lambda m: m["strength"])
            self.spatial_memory.remove(weakest)
        self.spatial_memory.append({"pos": food_pos, "strength": 1.0, "context": context, "timestamp": t})

    def decay_spatial_memory(self, t):
        for mem in self.spatial_memory:
            dt = max(1, t - mem["timestamp"])
            alpha = 0.5 + 0.3 * (1 - self.memory)
            mem["strength"] = max(0.0, 1.0 / ((dt + 1) ** alpha))
        self.spatial_memory = [m for m in self.spatial_memory if m["strength"] > 0.05]

    def retrieve_spatial_memory(self):
        if not self.spatial_memory:
            return None
        current = self.current_context()
        def context_similarity(mem_ctx, cur_ctx):
            fear_sim = 1 - abs(mem_ctx["fear"] - cur_ctx["fear"])
            carni_sim = 1 - abs(mem_ctx["carnivores_seen"] - cur_ctx["carnivores_seen"]) / max(1, cur_ctx["carnivores_seen"] + 1)
            return 0.7 * fear_sim + 0.3 * carni_sim
        scored = []
        for mem in self.spatial_memory:
            sim = context_similarity(mem["context"], current)
            score = sim * mem["strength"]
            scored.append((score, mem["pos"]))
        if not scored:
            return None
        scored.sort(reverse=True)
        top_score, top_pos = scored[0]
        if random.random() < top_score:
            return top_pos
        return None

    def gene_food(self, food_positions):
        return self.food_gene if food_positions else 0.0

    def detect_and_flee(self, other_organisms):
        if self.cannibalism:
            return False
        nearest_threat = None
        min_distance = float('inf')
        effective_detection = self.carnivore_detection * (1 + 0.5 * self.fear)
        for org in other_organisms:
            if not org.cannibalism:
                continue
            known = False
            if hasattr(org, 'lineage') and org.lineage is not None and self.known_carnivore_ids and self.known_carnivore_ids.intersection(org.lineage):
                known = True
            elif self.carnivore_sense > 0 and random.random() < self.carnivore_sense:
                if hasattr(org, 'lineage') and org.lineage is not None:
                    self.known_carnivore_ids.update(org.lineage)
                known = True
            if known:
                dist = abs(org.x - self.x) + abs(org.y - self.y)
                if dist <= effective_detection and dist < min_distance:
                    nearest_threat = org
                    min_distance = dist
        if nearest_threat:
            fear_increase = 0.8 / (1 + np.exp(-0.5 * (min_distance - 3)))
            self.fear = min(1.0, self.fear + fear_increase)
            self.energy_efficiency = max(0.5, self.energy_efficiency - 0.1 * fear_increase)
            effective_speed = self.speed * (1 + 2.5 * (self.fear ** 0.7))
            if random.random() < effective_speed:
                dx = -np.sign(nearest_threat.x - self.x)
                dy = -np.sign(nearest_threat.y - self.y)
                self.x = max(0, min(self.grid_size - 1, self.x + dx))
                self.y = max(0, min(self.grid_size - 1, self.y + dy))
            return True
        return False

    def move_towards_food(self, food_positions, t):
        mem_target = self.retrieve_spatial_memory()
        if not food_positions and mem_target:
            target_food = mem_target
        elif food_positions:
            target_food = min(food_positions, key=lambda f: abs(f[0] - self.x) + abs(f[1] - self.y))
            self.update_spatial_memory(target_food, t)
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

    def move(self, food_positions, other_organisms, movement_cost=1.0, t=0):
        self.age += movement_cost * (1 + self.fear)
        self.frames_since_last_food += 1
        if not self.cannibalism:
            self.communicate_carnivore(other_organisms)
        if self.cannibalism and self.rest_timer > 0:
            self.rest_timer -= 1
            return
        if not self.cannibalism:
            self.decay_spatial_memory(t)
        self.fear = max(0.0, self.fear - 0.05)
        if self.cannibalism:
            self.move_towards_prey(other_organisms)
        elif not self.detect_and_flee(other_organisms):
            self.food_gene = self.gene_food(food_positions)
            if self.food_gene > 0.0:
                self.move_towards_food(food_positions, t)
            else:
                self.move_random()

    def is_dead(self):
        return self.age >= self.lifespan

    def division(self, carnivores_exist=False):
        if self.cannibalism:
            offspring = Organism(self.x, self.y, self.grid_size, cannibalism=True, lineage=self.lineage, generation=self.generation+1)
            keys = list(self.traits.keys())
            alloc = np.array([self.traits[k] for k in keys])
            alloc += np.random.normal(0, 0.04, len(alloc))
            alloc = np.clip(alloc, 0.01, None)
            alloc = softmax(alloc)
            while not concave_tradeoff(alloc[1], alloc[2]):
                alloc = np.abs(alloc + np.random.normal(0, 0.03, len(alloc)))
                alloc = softmax(alloc)
            for i, k in enumerate(keys):
                offspring.traits[k] = alloc[i]
            offspring.lifespan = int(600 + 1200 * offspring.traits["lifespan"])
            offspring.speed = 0.1 + 0.8 * offspring.traits["speed"]
            offspring.stealth = 0.05 + 0.9 * offspring.traits["stealth"]
            offspring.energy_efficiency = 0.5 + 0.5 * offspring.traits["energy_efficiency"]
            offspring.food_gene = 0.05 + 0.45 * offspring.traits["food_gene"]  # Now evolves for carnivores
            offspring.hunting_strategy = random.choices(
                ["ambush", "pursuit"],
                weights=[offspring.stealth, offspring.speed]
            )[0]
        else:
            offspring = Organism(self.x, self.y, self.grid_size, cannibalism=False, generation=self.generation+1)
            keys = list(self.traits.keys())
            alloc = np.array([self.traits[k] for k in keys])
            alloc += np.random.normal(0, 0.04, len(alloc))
            alloc = np.clip(alloc, 0.01, None)
            alloc = softmax(alloc)
            while not convex_tradeoff(alloc[0], alloc[1]):
                alloc = np.abs(alloc + np.random.normal(0, 0.03, len(alloc)))
                alloc = softmax(alloc)
            for i, k in enumerate(keys):
                offspring.traits[k] = alloc[i]
            offspring.lifespan = int(500 + 1500 * offspring.traits["lifespan"])
            offspring.speed = 0.05 + 0.85 * offspring.traits["speed"]
            offspring.food_gene = 0.05 + 0.45 * offspring.traits["food_gene"]
            offspring.carnivore_detection = 2 + 12 * offspring.traits["carnivore_detection"]
            offspring.memory = 0.05 + 0.9 * offspring.traits["memory"]
            offspring.energy_efficiency = 0.5 + 0.5 * offspring.traits["energy_efficiency"]
            offspring.known_carnivore_ids = set(self.known_carnivore_ids)
            offspring.carnivore_sense = np.clip(np.random.normal(self.carnivore_sense, 0.05), 0, 1)
            offspring.spatial_memory_capacity = int(2 + 6 * offspring.traits["memory"])
            offspring.spatial_memory = [dict(m) for m in self.spatial_memory]
            mutation_chance = 0.002 if carnivores_exist else 0.1  # Make carnivore emergence more likely
            offspring.cannibalism = random.random() < mutation_chance
        return offspring

    def witness_cannibalization(self, carnivore, prey_pos):
        dist = abs(prey_pos[0] - self.x) + abs(prey_pos[1] - self.y)
        if dist <= self.visibility_radius and not self.cannibalism:
            if hasattr(carnivore, 'lineage') and carnivore.lineage is not None:
                self.known_carnivore_ids.update(carnivore.lineage)
            self.fear = min(1.0, self.fear + 0.6)
            self.communicate_carnivore(None)
            return True
        return False

    def communicate_carnivore(self, other_organisms):
        if self.cannibalism or not hasattr(self, 'known_carnivore_ids'):
            return
        if other_organisms is None:
            return
        comm_radius = self.communication_radius * (1 + 0.3 * self.fear)
        for org in other_organisms:
            if not org.cannibalism and org != self:
                dist = abs(org.x - self.x) + abs(org.y - self.y)
                if dist <= comm_radius:
                    if hasattr(org, 'known_carnivore_ids') and self.known_carnivore_ids:
                        before = len(org.known_carnivore_ids)
                        org.known_carnivore_ids.update(self.known_carnivore_ids)
                        after = len(org.known_carnivore_ids)
                        if after > before:
                            org.communicate_carnivore(other_organisms)
                        fear_transfer = 0.4 * (1 - dist / comm_radius)
                        org.fear = min(1.0, org.fear + fear_transfer * (1 - org.fear))
                        org.memory = min(1.0, org.memory + 0.1 * fear_transfer)
