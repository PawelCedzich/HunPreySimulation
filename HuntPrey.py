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
RAY_ANGLE = 360 / NUM_RAYS  # domyślny kąt, ale nie używaj FIELD_OF_VIEW tutaj
MAX_SPEED = 5
MAX_HUNGER = 100
MAX_TURN_ANGLE = 15  # stopni na tick

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
        self.view_angle = getattr(self, "VIEW_ANGLE", 360)  # domyślnie 360, nadpisywane w Prey/Predator

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
            # --- Używaj indywidualnego pola widzenia ---
            local_fov = getattr(self, "VIEW_ANGLE", 360)
            local_ray_angle = local_fov / NUM_RAYS
            start_angle = self.direction - (local_fov / 2)
            for i in range(NUM_RAYS):
                ray_dir = (start_angle + i * local_ray_angle) % 360
                dist, obj_type = self.cast_ray(ray_dir, objects, local_fov)
                self.inputs_cache.append(dist / WIDTH)
                self.inputs_cache.append(obj_type)
            self.inputs_cache.append(self.hunger / MAX_HUNGER)
            self.tick_since_last_ray = 0
        else:
            self.tick_since_last_ray += 1

        return self.inputs_cache

    def cast_ray(self, ray_dir, objects, fov):
        min_dist = WIDTH
        obj_type = 0
        rad = math.radians(ray_dir)
        for obj in objects:
            if not obj.alive:
                continue
            dx = obj.x - self.x
            dy = obj.y - self.y
            angle_to_obj = math.degrees(math.atan2(dy, dx)) % 360
            # --- MODYFIKACJA: angle_diff zależne od fov ---
            angle_diff = abs((ray_dir - angle_to_obj + 180) % 360 - 180)
            if angle_diff < (fov / NUM_RAYS) / 2:
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

    # --- ZAPAMIĘTAJ CAŁĄ GENERACJĘ NA START ---
    all_preys = preys[:]
    all_predators = predators[:]

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
        new_preys = []
        for prey in preys:
            if prey.alive:
                result = prey.update(foods, predators)
                pygame.draw.circle(screen, (0, 0, 255), (int(prey.x), int(prey.y)), 6)
                # draw_field_of_view(screen, prey, (0, 255, 255))  # <--- ZAKOMENTUJ TĘ LINIĘ ABY WYŁĄCZYĆ STOŻEK PREY
                if result == "reproduce":
                    import copy
                    new_genome = copy.deepcopy(prey.genome)
                    new_genome.mutate(config_prey.genome_config)
                    new_net = neat.nn.FeedForwardNetwork.create(new_genome, config_prey)
                    # Tworzenie nowego osobnika obok rodzica
                    offset = random.uniform(-10, 10)
                    child = Prey(new_genome, new_net)
                    child.x = min(max(prey.x + offset, 0), WIDTH)
                    child.y = min(max(prey.y + offset, 0), HEIGHT)
                    child.direction = random.uniform(0, 360)
                    new_preys.append(child)
        preys.extend(new_preys)

        # UPDATE i RYSOWANIE PREDATORÓW
        new_predators = []
        for predator in predators:
            if predator.alive:
                result = predator.update(preys)
                pygame.draw.circle(screen, (255, 0, 0), (int(predator.x), int(predator.y)), 8)
                # draw_field_of_view(screen, predator, (255, 255, 0))  # <--- ZAKOMENTUJ TĘ LINIĘ ABY WYŁĄCZYĆ STOŻEK PREDATOR
                if result == "reproduce" and len(predators) + len(new_predators) < MAX_PREDATORS:
                    import copy
                    new_genome = copy.deepcopy(predator.genome)
                    new_genome.mutate(config_predator.genome_config)
                    new_net = neat.nn.FeedForwardNetwork.create(new_genome, config_predator)
                    # Tworzenie nowego osobnika obok rodzica
                    offset = random.uniform(-10, 10)
                    child = Predator(new_genome, new_net)
                    child.x = min(max(predator.x + offset, 0), WIDTH)
                    child.y = min(max(predator.y + offset, 0), HEIGHT)
                    child.direction = random.uniform(0, 360)
                    new_predators.append(child)
        predators.extend(new_predators)

        # Usuwanie martwych agentów i zjedzonych jedzenia
        preys = [p for p in preys if p.alive]
        predators = [p for p in predators if p.alive]
        foods = [f for f in foods if f.alive]

        # Dorysowanie jedzenia jeśli za mało
        if len(foods) < 60:
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
            # Fitness za przeżycie
            for prey in preys:
                if prey.alive:
                    prey.genome.fitness += 10
            for predator in predators:
                if predator.alive:      
                    predator.genome.fitness += 10

            # Ewolucja NEAT
            pop_prey.reporters.start_generation(gen)
            
            # Sprawdź czy populacja i species mają osobników
            population_empty = not pop_prey.population or all(len(s.members) == 0 for s in pop_prey.species.species.values())
            if population_empty:
                print("Prey population or all species extinct! Rescuing best genome from previous generation.")
                if all_preys and len(all_preys) > 0:
                    best_prey = max(all_preys, key=lambda p: p.genome.fitness)
                    best_genome = best_prey.genome
                    pop_prey = neat.Population(config_prey)
                    for gid, genome in pop_prey.population.items():
                        genome.connections = best_genome.connections.copy()
                        genome.nodes = best_genome.nodes.copy()
                        genome.fitness = 0
                else:
                    print("Brak osobników do uratowania, restart populacji.")
                    pop_prey = neat.Population(config_prey)
            else:
                pop_prey.population = pop_prey.reproduction.reproduce(
                    pop_prey.config, pop_prey.species, pop_prey.config.pop_size, gen
                )
            prey_genomes = list(pop_prey.population.items())   
            preys = init_agents(prey_genomes, config_prey, Prey, MAX_PREY)

            pop_predator.reporters.start_generation(gen)
            print(f"Predator population size: {config_predator.pop_size}")  # Debugging log
            # --- ELITISM: rescue best genome if extinct ---
            if not pop_predator.population:
                print("Predator population extinct! Rescuing best genome from previous generation.")
                if all_predators and len(all_predators) > 0:
                    best_pred = max(all_predators, key=lambda p: p.genome.fitness)
                    best_genome = best_pred.genome
                    pop_predator = neat.Population(config_predator)
                    for gid, genome in pop_predator.population.items():
                        genome.connections = best_genome.connections.copy()
                        genome.nodes = best_genome.nodes.copy()
                        genome.fitness = 0
                else:
                    pop_predator = neat.Population(config_predator)
            else:
                pop_predator.population = pop_predator.reproduction.reproduce(
                    pop_predator.config, pop_predator.species, pop_predator.config.pop_size, gen
                )
                pop_predator.species.speciate(pop_predator.config, pop_predator.population, gen)
            predator_genomes = list(pop_predator.population.items())   
            predators = init_agents(predator_genomes, config_predator, Predator, MAX_PREDATORS)

            # Reset jedzenia, kroków i liczników
            foods = [Food(WIDTH, HEIGHT) for _ in range(80)]
            step = 0
            gen += 1            
            print(f"Generacja {gen} zakończona.")

            # --- ZAPAMIĘTAJ CAŁĄ GENERACJĘ NA NOWO ---
            all_preys = preys[:]
            all_predators = predators[:]

    plt.ioff()  # Disable interactive mode Disable interactive mode
    plt.show()  # Show the final plot    plt.show()  # Show the final plot
    pygame.quit()  

def draw_field_of_view(screen, agent, color):
    # Rysuj pole widzenia jako wycinek koła (łuk) zarówno dla predatorów jak i prey
    if not hasattr(agent, "VIEW_ANGLE"):
        return
    fov = getattr(agent, "VIEW_ANGLE", 360)
    length = 80  # długość promienia widzenia (możesz zmienić)
    center = (int(agent.x), int(agent.y))
    left_angle = agent.direction - fov / 2
    right_angle = agent.direction + fov / 2

    # Punkty na łuku
    arc_points = []
    num_arc_points = 16  # im więcej, tym gładszy łuk
    for i in range(num_arc_points + 1):
        angle = math.radians(left_angle + i * (fov / num_arc_points))
        x = int(agent.x + math.cos(angle) * length)
        y = int(agent.y + math.sin(angle) * length)
        arc_points.append((x, y))

    # Rysuj linie od środka do końców łuku
    pygame.draw.line(screen, color, center, arc_points[0], 1)
    pygame.draw.line(screen, color, center, arc_points[-1], 1)
    # Rysuj łuk (po okręgu)
    pygame.draw.lines(screen, color, False, arc_points, 1)

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