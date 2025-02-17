import pygame
import random

class Food:
    def __init__(self, x, y, radius=5):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = (0, 255, 0)  # Green color

    def draw(self, window):
        pygame.draw.circle(window, self.color, (self.x, self.y), self.radius)

    @staticmethod
    def spawn_random(width, height):
        x = random.randint(0, width)
        y = random.randint(0, height)
        return Food(x, y)
