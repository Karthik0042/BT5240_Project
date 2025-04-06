# organism.py

import random

class Organism:
    def __init__(self, x, y, grid_size):
        self.x = x
        self.y = y
        self.grid_size = grid_size

    def move(self):
        # Moving the organism in a random directions
        direction = random.choice(["up", "down", "left", "right"])

        if direction == "up" and self.y < self.grid_size - 1:
            self.y += 1
        elif direction == "down" and self.y > 0:
            self.y -= 1
        elif direction == "left" and self.x > 0:
            self.x -= 1
        elif direction == "right" and self.x < self.grid_size - 1:
            self.x += 1
            
    def  division(self):
        # Mitosis of the organism
        return Organism(self.x, self.y, self.grid_size)
