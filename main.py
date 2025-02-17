import pygame
import sys
import time
import random
from prey import Prey
from food import Food
from hunter import Hunter

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("HunPrey Simulation")

# Set up the clock for managing the frame rate
clock = pygame.time.Clock()

# Set up font for displaying prey count
font = pygame.font.SysFont(None, 36)

preys = [Prey(random.randint(0, width), random.randint(0, height)) for _ in range(5)]
food_items = []
hunters = [Hunter(random.randint(0, width), random.randint(0, height)) for _ in range(2)]
last_food_spawn_time = time.time()

def update_logic():
    global last_food_spawn_time
    # Update each prey's logic
    new_preys = []
    for prey in preys:
        result = prey.update_position(width, height, food_items)
        if result is False:
            preys.remove(prey)  # Remove prey if it dies
            continue
        elif isinstance(result, Prey):
            new_preys.append(result)
        prey.decrease_hunger()

        # Check for food collision
        for food in food_items:
            if pygame.Rect(prey.x - prey.radius, prey.y - prey.radius, prey.radius * 2, prey.radius * 2).colliderect(
                pygame.Rect(food.x - food.radius, food.y - food.radius, food.radius * 2, food.radius * 2)):
                prey.hunger = min(100, prey.hunger + 25)
                food_items.remove(food)

    preys.extend(new_preys)

    # Update each hunter's logic
    new_hunters = []
    for hunter in hunters[:]:
        result = hunter.update_position(width, height, preys)
        if result is False:
            hunters.remove(hunter)  # Remove hunter if it dies
            continue
        elif isinstance(result, Hunter):
            new_hunters.append(result)
        hunter.decrease_hunger()

        # Check for prey collision
        for prey in preys:
            if pygame.Rect(hunter.x - hunter.radius, hunter.y - hunter.radius, hunter.radius * 2, hunter.radius * 2).colliderect(
                pygame.Rect(prey.x - prey.radius, prey.y - prey.radius, prey.radius * 2, prey.radius * 2)):
                hunter.eat_prey(prey)
                preys.remove(prey)

    hunters.extend(new_hunters)

    # Spawn three food items every second
    current_time = time.time()
    if current_time - last_food_spawn_time > 1:
        for _ in range(3):
            food_items.append(Food.spawn_random(width, height))
        last_food_spawn_time = current_time

def draw():
    # Drawing code goes here
    window.fill((0, 0, 0))  # Fill the screen with black
    for prey in preys:
        prey.draw(window)
    for food in food_items:
        food.draw(window)
    for hunter in hunters:
        hunter.draw(window)

    # Draw prey count
    prey_count_text = font.render(f"Prey Count: {len(preys)}", True, (255, 255, 255))
    window.blit(prey_count_text, (10, 10))

def main():
    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        update_logic()
        draw()

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__": 
    main()