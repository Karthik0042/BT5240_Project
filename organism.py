# organism.py

import random

class Organism:
    def __init__(self, x, y, grid_size):
        self.x = x
        self.y = y
        self.grid_size = grid_size  # Store grid size for boundary checks

    def move(self):
        """Move the organism randomly in one of four directions."""
        direction = random.choice(["up", "down", "left", "right"])

        if direction == "up" and self.y < self.grid_size - 1:
            self.y += 1
        elif direction == "down" and self.y > 0:
            self.y -= 1
        elif direction == "left" and self.x > 0:
            self.x -= 1
        elif direction == "right" and self.x < self.grid_size - 1:
            self.x += 1
