import random
import numpy as np

class Organism:
    _id_counter = 0  # Unique ID for lineage tracking

    def __init__(self, x, y, grid_size, cannibalism=False, lineage=None):
        self.x = x
        self.y = y
        self.grid_size = grid_size
        self.cannibalism = cannibalism
        self.rest_timer = 0

        # Unique ID and lineage for carnivores
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

        # Base traits
        self.food_gene = 0.15
        self.speed = 0.3 if not cannibalism else 0.5
        self.carnivore_detection = 4 if not cannibalism else 0

        # Lifespan and aging
        self.age = 0
        self.lifespan = np.random.randint(875, 1000) if not cannibalism else np.random.randint(900, 1200)

        # Herbivore-specific traits
        if not cannibalism:
            self.memory = 0.3
            self.fear = 0.2
            self.known_carnivore_ids = set()
            self.carnivore_sense = np.clip(np.random.normal(0.8, 0.2), 0, 1)
            # --- Spatial and Contextual Memory ---
            self.spatial_memory_capacity = 3  # Max number of food locations to remember
            # Each entry: {"pos": (x, y), "strength": float, "context": context_dict, "timestamp": t}
            self.spatial_memory = []
        else:
            self.memory = 0.0
            self.fear = 0.0
            self.known_carnivore_ids = None
            self.carnivore_sense = 0.0

        # Memory system (legacy, now handled by spatial_memory)
        self.memory_decay_base = 150
        self.visibility_radius = 5
        self.communication_radius = 7

        # Energy and metabolism
        self.energy_efficiency = 1.0
        self.frames_since_last_food = 0

    def current_context(self):
        """Return current context as a dict (can be expanded)."""
        return {
            "fear": round(self.fear, 1),
            "carnivores_seen": len(self.known_carnivore_ids),
        }

    def update_spatial_memory(self, food_pos, t):
        """Add or update a food memory with current context and initial strength."""
        context = self.current_context()
        # If already in memory, update timestamp and reset strength
        for mem in self.spatial_memory:
            if mem["pos"] == food_pos:
                mem["strength"] = 1.0
                mem["timestamp"] = t
                mem["context"] = context
                return
        # If not, add new memory (evict weakest if over capacity)
        if len(self.spatial_memory) >= self.spatial_memory_capacity:
            weakest = min(self.spatial_memory, key=lambda m: m["strength"])
            self.spatial_memory.remove(weakest)
        self.spatial_memory.append({"pos": food_pos, "strength": 1.0, "context": context, "timestamp": t})

    def decay_spatial_memory(self, t):
        """Decay all memories using a power-law kernel (fractional calculus inspired)[6]."""
        for mem in self.spatial_memory:
            dt = max(1, t - mem["timestamp"])
            # Power-law decay: strength ~ (dt+1)^-alpha, alpha in [0.3, 0.7]
            alpha = 0.5 + 0.3 * (1 - self.memory)
            mem["strength"] = max(0.0, 1.0 / ((dt + 1) ** alpha))
        # Remove memories below threshold
        self.spatial_memory = [m for m in self.spatial_memory if m["strength"] > 0.05]

    def retrieve_spatial_memory(self):
        """Retrieve the best-matching memory based on context similarity."""
        if not self.spatial_memory:
            return None
        current = self.current_context()
        # Context similarity: 1 - normalized sum of absolute differences
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
        # With probability proportional to top score, use that memory
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
        # Try spatial/contextual memory first
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

        # Handle resting period for carnivores
        if self.cannibalism and self.rest_timer > 0:
            self.rest_timer -= 1
            return

        # Decay all spatial memories
        if not self.cannibalism:
            self.decay_spatial_memory(t)

        # Fear decay
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
            offspring = Organism(self.x, self.y, self.grid_size, cannibalism=True, lineage=self.lineage)
        else:
            offspring = Organism(self.x, self.y, self.grid_size, cannibalism=False)
            offspring.known_carnivore_ids = set(self.known_carnivore_ids)
            offspring.carnivore_sense = np.clip(np.random.normal(self.carnivore_sense, 0.05), 0, 1)
            offspring.spatial_memory_capacity = self.spatial_memory_capacity
            offspring.spatial_memory = [dict(m) for m in self.spatial_memory]  # Deep copy

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

            mutation_chance = 0.005 if carnivores_exist else 0.1
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
