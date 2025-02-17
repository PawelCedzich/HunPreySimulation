import pygame
import random
import math
from prey import Prey

class Hunter:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.color = (255, 0, 0)  # Red color
        self.speed = 3
        self.hunger = 100
        self.view_angle = 135  # View angle in degrees
        self.view_distance = 90  # View distance
        self.direction = (random.uniform(-1, 1), random.uniform(-1, 1))
        # Normalize the direction vector
        direction_length = math.sqrt(self.direction[0] ** 2 + self.direction[1] ** 2)
        self.direction = (self.direction[0] / direction_length, self.direction[1] / direction_length)
        self.reproduction_cooldown = 1000  # Longer cooldown period before it can reproduce again

    def update_position(self, width, height, preys):
        self.find_and_follow_prey(preys)
        self.move_forward()

        # Wrap around the edges
        if self.x < 0:
            self.x = width
        elif self.x > width:
            self.x = 0
        if self.y < 0:
            self.y = height
        elif self.y > height:
            self.y = 0

        # Check if hunger is below 0
        if self.hunger <= 0:
            return False  # Hunter dies

        self.reproduction_cooldown -= 1
        if self.hunger > 90 and self.reproduction_cooldown <= 0:
            return self.reproduce()

        return True  # Hunter survives

    def find_prey(self, preys):
        nearest_prey = None
        nearest_distance = float('inf')
        for prey in preys:
            distance = math.sqrt((prey.x - self.x) ** 2 + (prey.y - self.y) ** 2)
            if distance < nearest_distance and distance <= self.view_distance:
                prey_direction = (prey.x - self.x, prey.y - self.y)
                prey_angle = math.degrees(math.atan2(prey_direction[1], prey_direction[0]))
                hunter_angle = math.degrees(math.atan2(self.direction[1], self.direction[0]))
                relative_angle = (prey_angle - hunter_angle + 360) % 360
                if -self.view_angle / 2 <= relative_angle <= self.view_angle / 2:
                    nearest_prey = prey
                    nearest_distance = distance
        return nearest_prey

    def decrease_hunger(self):
        self.hunger -= 0.1

    def draw(self, window):
        pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw view angle lines
        start_angle = math.degrees(math.atan2(self.direction[1], self.direction[0])) - self.view_angle / 2
        end_angle = start_angle + self.view_angle
        start_line = (self.x + self.view_distance * math.cos(math.radians(start_angle)),
                      self.y + self.view_distance * math.sin(math.radians(start_angle)))
        end_line = (self.x + self.view_distance * math.cos(math.radians(end_angle)),
                    self.y + self.view_distance * math.sin(math.radians(end_angle)))
        pygame.draw.line(window, self.color, (self.x, self.y), start_line, 1)
        pygame.draw.line(window, self.color, (self.x, self.y), end_line, 1)

    def move_forward(self):
        self.x += self.speed * self.direction[0]
        self.y += self.speed * self.direction[1]

    def rotate_direction(self, angle):
        angle_rad = math.radians(angle)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        new_direction_x = self.direction[0] * cos_angle - self.direction[1] * sin_angle
        new_direction_y = self.direction[0] * sin_angle + self.direction[1] * cos_angle
        self.direction = (new_direction_x, new_direction_y)

    def find_and_follow_prey(self, preys):
        target_prey = self.find_prey(preys)
        if target_prey:
            dx, dy = target_prey.x - self.x, target_prey.y - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance != 0:
                self.direction = (dx / distance, dy / distance)

    def eat_prey(self, prey):
        self.hunger = min(100, self.hunger + 30)  # Replenish 30% food

    def reproduce(self):
        self.reproduction_cooldown = 1000  # Longer cooldown period before it can reproduce again
        new_hunter = Hunter(self.x, self.y)
        new_hunter.set_random_direction()
        return new_hunter

    def set_random_direction(self):
        angle = random.uniform(0, 2 * math.pi)
        self.direction = (math.cos(angle), math.sin(angle))
