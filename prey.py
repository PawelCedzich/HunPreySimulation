import pygame
import math
import random

class Prey:
    def __init__(self, x, y, radius=10, speed=2.5, can_rotate=True):  # Add can_rotate parameter
        self.x = x
        self.y = y
        self.radius = radius
        self.color = (0, 0, 255)  # Blue color
        self.speed = speed
        angle = random.uniform(0, 2 * math.pi)
        self.direction = (math.cos(angle), math.sin(angle))  # Random initial direction
        self.hunger = 100  # Hunger level starts at 100
        self.view_angle = 270  # Viewing angle in degrees
        self.view_distance = 150  # Reduced view distance by 75%
        self.action_timer = 0  # Timer to control action intervals
        self.current_action = None  # Current action
        self.can_rotate = can_rotate  # Store the can_rotate parameter
        self.reproduction_cooldown = 500  # Halved cooldown period before it can reproduce again

    def set_direction(self, dx, dy):
        self.direction = (dx, dy)

    def set_direction_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        length = math.sqrt(dx**2 + dy**2)
        if length != 0:
            dx /= length
            dy /= length
        # Smoothly change direction
        new_direction = (
            self.direction[0] * 0.9 + dx * 0.1,  # Adjust the factor to change rotation speed
            self.direction[1] * 0.9 + dy * 0.1
        )
        new_length = math.sqrt(new_direction[0]**2 + new_direction[1]**2)
        if new_length != 0:
            self.direction = (new_direction[0] / new_length, new_direction[1] / new_length)

    def set_random_direction(self):
        angle = random.uniform(0, 2 * math.pi)
        self.direction = (math.cos(angle), math.sin(angle))

    def move_forward(self):
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed

    def rotate_left(self, angle=10):
        angle_rad = math.radians(angle)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        self.direction = (
            self.direction[0] * cos_angle - self.direction[1] * sin_angle,
            self.direction[0] * sin_angle + self.direction[1] * cos_angle
        )

    def rotate_right(self, angle=10):
        self.rotate_left(-angle)

    def find_food(self, food_items):
        nearest_food = None
        nearest_distance = float('inf')
        for food in food_items:
            distance = math.sqrt((food.x - self.x)**2 + (food.y - self.y)**2)
            if distance < nearest_distance and distance <= self.view_distance:
                food_direction = (food.x - self.x, food.y - self.y)
                food_angle = math.degrees(math.atan2(food_direction[1], food_direction[0]))
                prey_angle = math.degrees(math.atan2(self.direction[1], self.direction[0]))
                relative_angle = (food_angle - prey_angle + 360) % 360
                if -self.view_angle / 2 <= relative_angle <= self.view_angle / 2:
                    nearest_food = food
                    nearest_distance = distance
        return nearest_food

    def update_position(self, width, height, food_items):
        nearest_food = self.find_food(food_items)
        if nearest_food:
            self.set_direction_towards(nearest_food.x, nearest_food.y)

        # Always move forward
        self.move_forward()

        # Wrap around the window edges
        if self.x < 0:
            self.x = width
        elif self.x > width:
            self.x = 0
        if self.y < 0:
            self.y = height
        elif self.y > height:
            self.y = 0

        self.reproduction_cooldown -= 1
        if self.hunger > 90 and self.reproduction_cooldown <= 0:
            return self.reproduce()

        if self.hunger <= 0:
            return False  # Prey dies
        return True  # Prey survives

    def decrease_hunger(self, amount=0.1):  # Reduced from 0.1 to 0.05
        self.hunger = max(0, self.hunger - amount)

    def draw_hunger_bar(self, window):
        pass  # Hide hunger bar

    def move_up(self):
        self.y -= self.speed

    def move_down(self):
        self.y += self.speed

    def move_left(self):
        self.x -= self.speed

    def move_right(self):
        self.x += self.speed

    def draw_looking_direction(self, window):
        pass  # Hide looking direction

    def draw_view_angle(self, window):
        pass  # Hide view angle

    def draw(self, window):
        pygame.draw.circle(window, self.color, (self.x, self.y), self.radius)
        # self.draw_hunger_bar(window)
        # self.draw_looking_direction(window)
        # self.draw_view_angle(window)

    def reproduce(self):
        self.reproduction_cooldown = 500  # Halved cooldown period before it can reproduce again
        new_prey = Prey(self.x, self.y)
        new_prey.set_random_direction()
        return new_prey
