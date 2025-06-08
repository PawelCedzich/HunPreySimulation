import pygame
import neat
import sys
import random
import math
from shared import WIDTH, HEIGHT, MAX_STAMINA
from food import Food
from prey import Prey
from predator import Predator
import matplotlib.pyplot as plt
import csv

# Parametry
FPS = 120
NUM_STEPS_PER_GEN = 1000  # Zwiększ liczbę kroków na generację

MAX_PREY = 150
MAX_PREDATORS = 100
RAY_UPDATE_FREQ = 5

NUM_RAYS = 8  # Więcej promieni
RAY_ANGLE = 360 / NUM_RAYS
MAX_SPEED = 5  # Większa prędkość
MAX_HUNGER = 100
MAX_TURN_ANGLE = 25  # Większy kąt skrętu

def init_agents(genomes, config, agent_class, max_agents):
    agents = []
    for i, (gid, genome) in enumerate(genomes):
        if i >= max_agents:
            break
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        agents.append(agent_class(genome, net))
    return agents

def run_live_training(config_prey, config_predator, generations=60):
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

    # Użyj liczebności z configów NEAT
    preys = init_agents(prey_genomes, config_prey, Prey, config_prey.pop_size)
    predators = init_agents(predator_genomes, config_predator, Predator, config_predator.pop_size)

    # Ustaw stamina na 90% na początku generacji
    for prey in preys:
        prey.stamina = MAX_STAMINA * 0.9
    for predator in predators:
        predator.stamina = MAX_STAMINA * 0.9

    foods = [Food(WIDTH, HEIGHT) for _ in range(250)]  # Więcej jedzenia na start

    # --- ZAPAMIĘTAJ CAŁĄ GENERACJĘ NA START ---
    all_preys = preys[:]
    all_predators = predators[:]

    # --- CSV LOGGING ---
    csv_filename = "simulation_stats.csv"
    # Otwórz plik CSV tylko raz na całą symulację
    with open(csv_filename, mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([
            "generation", "tick", "preys_alive", "predators_alive", "food_alive",
            "max_preys_this_gen", "max_predators_this_gen"
        ])

        max_preys_this_gen = len(preys)
        max_predators_this_gen = len(predators)

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
                    pygame.draw.circle(screen, (0, 0, 255), (int(prey.x), int(prey.y)), 7)
                    # draw_field_of_view(screen, prey, (0, 255, 255))
                    if result == "reproduce":
                        import copy
                        new_genome = copy.deepcopy(prey.genome)
                        new_genome.mutate(config_prey.genome_config)
                        new_net = neat.nn.FeedForwardNetwork.create(new_genome, config_prey)
                        offset = random.uniform(-10, 10)
                        child = Prey(new_genome, new_net)
                        child.x = min(max(prey.x + offset, 0), WIDTH)
                        child.y = min(max(prey.y + offset, 0), HEIGHT)
                        child.direction = random.uniform(0, 360)
                        child.stamina = MAX_STAMINA * 0.9  # Ustaw stamina dziecka na 90%
                        new_preys.append(child)
            preys.extend(new_preys)

            # UPDATE i RYSOWANIE PREDATORÓW
            new_predators = []
            for predator in predators:
                if predator.alive:
                    result = predator.update(preys)
                    pygame.draw.circle(screen, (255, 0, 0), (int(predator.x), int(predator.y)), 7)
                    # draw_field_of_view(screen, predator, (255, 255, 0))
                    predator.draw_hunger_bar(screen)
                    if result == "reproduce" and len(predators) + len(new_predators) < MAX_PREDATORS:
                        import copy
                        new_genome = copy.deepcopy(predator.genome)
                        new_genome.mutate(config_predator.genome_config)
                        new_net = neat.nn.FeedForwardNetwork.create(new_genome, config_predator)
                        offset = random.uniform(-10, 10)
                        child = Predator(new_genome, new_net)
                        child.x = min(max(predator.x + offset, 0), WIDTH)
                        child.y = min(max(predator.y + offset, 0), HEIGHT)
                        child.direction = random.uniform(0, 360)
                        child.stamina = MAX_STAMINA * 0.9  # Ustaw stamina dziecka na 90%
                        new_predators.append(child)
            predators.extend(new_predators)

            # Usuwanie martwych agentów i zjedzonych jedzenia
            # Odejmij fitness za śmierć
            for prey in preys:
                if not prey.alive:
                    prey.genome.fitness -= 20
            for predator in predators:
                if not predator.alive:
                    predator.genome.fitness -= 20

            preys = [p for p in preys if p.alive]
            predators = [p for p in predators if p.alive]
            foods = [f for f in foods if f.alive]

            # --- aktualizacja maksymalnych liczebności w tej generacji ---
            max_preys_this_gen = max(max_preys_this_gen, len(preys))
            max_predators_this_gen = max(max_predators_this_gen, len(predators))

            # Dorysowanie jedzenia jeśli za mało
            if len(foods) < 240:
                foods.append(Food(WIDTH, HEIGHT))

            # Draw food count
            draw_food_count(screen, foods, preys, predators, gen, step)

            pygame.display.flip()
            clock.tick(FPS)

            step += 1

            # Logowanie co 50 ticków
            if step % 50 == 0:
                alive_preys = sum(prey.alive for prey in preys)
                alive_predators = sum(predator.alive for predator in predators)
                alive_foods = sum(food.alive for food in foods)
                print(f"Tick {step} Gen {gen} - Preys: {alive_preys}, Predators: {alive_predators}, Food: {alive_foods}")
                # --- ZAPIS DO CSV ---
                csv_writer.writerow([
                    gen, step, alive_preys, alive_predators, alive_foods,
                    max_preys_this_gen, max_predators_this_gen
                ])
                csvfile.flush()

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
                preys = init_agents(prey_genomes, config_prey, Prey, config_prey.pop_size)
                # Ustaw stamina na 90% po nowej generacji
                for prey in preys:
                    prey.stamina = MAX_STAMINA * 0.9

                pop_predator.reporters.start_generation(gen)
                print(f"Predator population size: {config_predator.pop_size}")
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
                        for gid, genome in pop_predator.population.items():
                            genome.fitness = 0  # <-- DODAJ TO!
                else:
                    pop_predator.population = pop_predator.reproduction.reproduce(
                        pop_predator.config, pop_predator.species, pop_predator.config.pop_size, gen
                    )
                    # UPEWNIJ SIĘ, ŻE KAŻDY GENOM MA FITNESS
                    for genome in pop_predator.population.values():
                        if genome.fitness is None:
                            genome.fitness = 0
                    pop_predator.species.speciate(pop_predator.config, pop_predator.population, gen)
                predator_genomes = list(pop_predator.population.items())   
                predators = init_agents(predator_genomes, config_predator, Predator, config_predator.pop_size)
                # Ustaw stamina na 90% po nowej generacji
                for predator in predators:
                    predator.stamina = MAX_STAMINA * 0.9

                # Reset jedzenia, kroków i liczników
                foods = [Food(WIDTH, HEIGHT) for _ in range(250)]
                step = 0
                gen += 1
                # --- ZAPIS DO CSV NA KONIEC GENERACJI ---
                alive_preys = sum(prey.alive for prey in preys)
                alive_predators = sum(predator.alive for predator in predators)
                alive_foods = sum(food.alive for food in foods)
                csv_writer.writerow([
                    gen, step, alive_preys, alive_predators, alive_foods,
                    max_preys_this_gen, max_predators_this_gen
                ])
                csvfile.flush()
                print(f"Generacja {gen} zakończona.")

                # --- reset maksymalnych liczebności na nową generację ---
                max_preys_this_gen = len(preys)
                max_predators_this_gen = len(predators)
                # --- ZAPAMIĘTAJ CAŁĄ GENERACJĘ NA NOWO ---
                all_preys = preys[:]
                all_predators = predators[:]

    plt.ioff()
    plt.show()
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

def draw_food_count(screen, foods, preys, predators, gen=None, step=None):
    # Display the count of food, preys, predators, generation and ticks
    font = pygame.font.SysFont(None, 24)
    text = f"Food: {len(foods)} | Preys: {len(preys)} | Predators: {len(predators)}"
    if gen is not None and step is not None:
        text += f" | Gen: {gen} | Tick: {step}"
    rendered = font.render(text, True, (255, 255, 255))
    screen.blit(rendered, (10, 10))

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

    run_live_training(config_prey, config_predator, generations=200)  


if __name__ == "__main__":
    start_simulation()