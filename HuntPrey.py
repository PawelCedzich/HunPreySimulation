import pygame
import neat
import sys
import random
import math
from shared import WIDTH, HEIGHT
from food import Food
from prey import Prey
from predator import Predator
import matplotlib.pyplot as plt

# Parametry
FPS = 30
NUM_STEPS_PER_GEN = 500
MAX_PREY = 200  # Updated from 200 to 100
MAX_PREDATORS = 170  # Updated from 150 to 100
RAY_UPDATE_FREQ = 5  # update ray tracing co 5 ticków

NUM_RAYS = 8
FIELD_OF_VIEW = 360
RAY_ANGLE = FIELD_OF_VIEW / NUM_RAYS
MAX_SPEED = 5
MAX_HUNGER = 100

class Agent:
    def __init__(self, genome, net):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.direction = random.uniform(0, 360)
        self.speed = 0
        self.hunger = MAX_HUNGER * 0.5
        self.alive = True
        self.genome = genome
        self.net = net
        self.inputs_cache = None  # cache sensorycznych danych
        self.tick_since_last_ray = 0
        self.view_distance = 100  # Default view distance for agents

    def move(self):
        rad = math.radians(self.direction)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed
        self.x = max(0, min(WIDTH, self.x))
        self.y = max(0, min(HEIGHT, self.y))

    def decrease_hunger(self):
        self.hunger -= self.speed * 0.1
        if self.hunger <= 0:
            self.alive = False

    def get_inputs(self, objects):
        # aktualizuj sensoryczne dane tylko co RAY_UPDATE_FREQ kroków
        if self.tick_since_last_ray >= RAY_UPDATE_FREQ or self.inputs_cache is None:
            self.inputs_cache = []
            for i in range(NUM_RAYS):
                ray_dir = (self.direction + i * RAY_ANGLE) % 360
                dist, obj_type = self.cast_ray(ray_dir, objects)
                self.inputs_cache.append(dist / WIDTH)
                self.inputs_cache.append(obj_type)
            self.inputs_cache.append(self.hunger / MAX_HUNGER)
            self.tick_since_last_ray = 0
        else:
            self.tick_since_last_ray += 1

        return self.inputs_cache

    def cast_ray(self, ray_dir, objects):
        min_dist = WIDTH
        obj_type = 0
        rad = math.radians(ray_dir)
        for obj in objects:
            if not obj.alive:
                continue
            dx = obj.x - self.x
            dy = obj.y - self.y
            angle_to_obj = math.degrees(math.atan2(dy, dx)) % 360
            angle_diff = abs((ray_dir - angle_to_obj + 180) % 360 - 180)
            if angle_diff < RAY_ANGLE / 2:
                dist = math.hypot(dx, dy)
                if dist < min_dist:
                    min_dist = dist
                    obj_type = 1
        return min_dist, obj_type

def init_agents(genomes, config, agent_class, max_agents):
    agents = []
    for i, (gid, genome) in enumerate(genomes):
        if i >= max_agents:
            break
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        agents.append(agent_class(genome, net))
    return agents

# Global variables for population tracking
population_data = {"preys": [], "predators": []}

def update_population_chart():
    plt.clf()
    plt.plot(population_data["preys"], label="Preys")
    plt.plot(population_data["predators"], label="Predators")
    plt.xlabel("Generation")
    plt.ylabel("Population")
    plt.title("Final Population Per Generation")
    plt.legend()
    plt.ylim(0, 200)  # Fixed scale for population
    plt.xticks(range(len(population_data["preys"])))  # Generations displayed every 1
    plt.draw()  # Draw the updated plot
    plt.pause(0.01)  # Pause to allow real-time updates

def run_live_training(config_prey, config_predator, generations=30):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Symulacja drapieżnik-ofiara z NEAT")
    clock = pygame.time.Clock()

    pop_prey = neat.Population(config_prey)
    pop_predator = neat.Population(config_predator)

    gen = 0
    step = 0

    prey_genomes = list(pop_prey.population.items())
    predator_genomes = list(pop_predator.population.items())

    preys = init_agents(prey_genomes, config_prey, Prey, MAX_PREY)
    predators = init_agents(predator_genomes, config_predator, Predator, MAX_PREDATORS)

    foods = [Food(WIDTH, HEIGHT) for _ in range(80)]  # Pass dimensions to Food

    plt.ion()  # Enable interactive mode for matplotlib
    while gen < generations:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((30, 30, 30))

        # RYSOWANIE JEDZENIA
        for food in foods:
            if food.alive:
                pygame.draw.circle(screen, (0, 255, 0), (int(food.x), int(food.y)), 4)

        # UPDATE i RYSOWANIE PREY
        for prey in preys:
            if prey.alive:
                prey.update(foods, predators)
                pygame.draw.circle(screen, (0, 0, 255), (int(prey.x), int(prey.y)), 6)
                #draw_agent_direction(screen, prey, (0, 255, 255))  # Dodaj rysowanie kierunku

        # UPDATE i RYSOWANIE PREDATORÓW
        for predator in predators:
            if predator.alive:
                predator.update(preys)
                pygame.draw.circle(screen, (255, 0, 0), (int(predator.x), int(predator.y)), 8)
                #draw_agent_direction(screen, predator, (255, 255, 0))  # Dodaj rysowanie kierunku

        # Usuwanie martwych agentów i zjedzonych jedzenia
        preys = [p for p in preys if p.alive]
        predators = [p for p in predators if p.alive]
        foods = [f for f in foods if f.alive]

        # Dorysowanie jedzenia jeśli za mało
        if len(foods) < 30:
            foods.append(Food(WIDTH, HEIGHT))  # Pass dimensions to Food

        # Draw food count
        draw_food_count(screen, foods, preys, predators)

        pygame.display.flip()
        clock.tick(FPS)

        step += 1

        # Logowanie co 50 ticków
        if step % 50 == 0:
            alive_preys = sum(prey.alive for prey in preys)
            alive_predators = sum(predator.alive for predator in predators)
            alive_foods = sum(food.alive for food in foods)  
            print(f"Tick {step} Gen {gen} - Preys: {alive_preys}, Predators: {alive_predators}, Food: {alive_foods}")

        # Koniec generacji
        if step >= NUM_STEPS_PER_GEN:
            # Zapisz końcową populację dla wykresu
            population_data["preys"].append(len(preys))
            population_data["predators"].append(len(predators))            
            population_data["predators"].append(len(predators))
            update_population_chart()  # Aktualizuj wykres tylko przy przejściu do nowej generacjit()  # Aktualizuj wykres tylko przy przejściu do nowej generacji

            # Fitness za przeżycieycie
            for prey in preys:
                if prey.alive:
                    prey.genome.fitness += 10
            for predator in predators:
                if predator.alive:      
                    predator.genome.fitness += 10

            # Ewolucja NEAT
            pop_prey.reporters.start_generation(gen)
            pop_prey.population = pop_prey.reproduction.reproduce(pop_prey.config, pop_prey.species, pop_prey.config.pop_size, gen) 
            prey_genomes = list(pop_prey.population.items())   
            preys = init_agents(prey_genomes, config_prey, Prey, MAX_PREY)

            pop_predator.reporters.start_generation(gen)
            print(f"Predator population size: {config_predator.pop_size}")  # Debugging log
            pop_predator.population = pop_predator.reproduction.reproduce(pop_predator.config, pop_predator.species, pop_predator.config.pop_size, gen) 
            pop_predator.species.speciate(pop_predator.config, pop_predator.population, gen)
            predator_genomes = list(pop_predator.population.items())   
            predators = init_agents(predator_genomes, config_predator, Predator, MAX_PREDATORS)

            # Reset jedzenia, kroków i licznikówjedzenia, kroków i liczników
            foods = [Food(WIDTH, HEIGHT) for _ in range(80)]  # Ensure each generation starts with 80 food items[Food(WIDTH, HEIGHT) for _ in range(80)]  # Ensure each generation starts with 80 food items
            step = 0
            gen += 1            
            print(f"Generacja {gen} zakończona.")

    plt.ioff()  # Disable interactive mode Disable interactive mode
    plt.show()  # Show the final plot    plt.show()  # Show the final plot
    pygame.quit()  


def draw_agent_direction(screen, agent, color):
    # Draw a line indicating the agent's direction direction
    rad = math.radians(agent.direction)
    end_x = agent.x + math.cos(rad) * 20
    end_y = agent.y + math.sin(rad) * 20   
    pygame.draw.line(screen, color, (agent.x, agent.y), (end_x, end_y), 2)

def draw_field_of_view(screen, agent, color):
    pass  # Do not draw the view angle or cone

def draw_food_count(screen, foods, preys, predators):
    # Display the count of food, preys, and predators
    font = pygame.font.SysFont(None, 24)
    text = font.render(f"Food: {len(foods)} | Preys: {len(preys)} | Predators: {len(predators)}", True, (255, 255, 255))    
    screen.blit(text, (10, 10))

def start_simulation():
    # Load NEAT configuration for prey
    config_prey = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        'neat-prey-config.txt'  # Ensure this file exists and is correctly formatted
    )

    # Load NEAT configuration for predators
    config_predator = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        'neat-predator-config.txt'  # Ensure this file exists and is correctly formatted
    )

    run_live_training(config_prey, config_predator, generations=30)  




if __name__ == "__main__":
    start_simulation()