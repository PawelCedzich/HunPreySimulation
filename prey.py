from shared import Agent, MAX_STAMINA, MAX_SPEED
import math

class Prey(Agent):
    VIEW_ANGLE = 150  # pole widzenia dla Prey (zmienione z 180 na 235)
    VIEW_DISTANCE = 130  # zasięg widzenia dla Prey

    def __init__(self, genome, net):
        super().__init__(genome, net)
        self.view_distance = self.VIEW_DISTANCE  # indywidualny zasięg widzenia
        self.reproduction_cooldown = 0
        self.eat_cooldown = 0  # cooldown na jedzenie

    def update(self, foods, predators, preys=None):
        if not self.alive:
            return

        self.ticks_alive += 1  # aktualizacja liczby przeżytych ticków

        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
        if self.eat_cooldown > 0:
            self.eat_cooldown -= 1

        # Przekazuj wszystkie obiekty do raycastingu: jedzenie, inne preys, predatory
        if preys is None:
            objects = foods + predators
        else:
            objects = foods + predators + [prey for prey in preys if prey is not self]

        inputs = self.get_inputs(objects)
        output = self.net.activate(inputs)

        turn = (output[0] * 2 - 1) * 5
        #self.genome.fitness -= abs(turn) * 0.05  # Kara za skręt
        speed = max(output[1] * MAX_SPEED * 1.2, 0) 

        self.direction = (self.direction + turn) % 360
        self.speed = speed

        # Calculate movement distance for fitness reward
        self.move()
        #self.genome.fitness += self.speed * 0.05  # Small reward for movement

        self.decrease_stamina()

        for food in foods:
            if self.eat_cooldown == 0 and food.alive and math.hypot(food.x - self.x, food.y - self.y) < 15:
                self.stamina = min(MAX_STAMINA, self.stamina + 30)
                food.alive = False
                self.eat_cooldown = 25  # blokada na 10 ticków
                self.genome.fitness += 5  # Nagroda za zjedzenie jedzenia
                break

        # Check for reproduction (po zjedzeniu!)
        if self.stamina > 90 and self.reproduction_cooldown == 0:
            self.genome.fitness += 10  # Reward for reproduction
            self.stamina -= 40  # Set stamina to 80% after reproduction
            self.reproduction_cooldown = 50
            return "reproduce"

    def draw_hunger_bar(self, screen):
        """
        Rysuje pasek głodu (staminy) nad prey.
        """
        import pygame

        bar_width = 40
        bar_height = 6
        x = int(self.x)
        y = int(self.y) - 25  # nad głową

        # Tło paska (szare)
        pygame.draw.rect(screen, (80, 80, 80), (x - bar_width // 2, y, bar_width, bar_height))
        # Wypełnienie (zielone do czerwonego w zależności od staminy)
        stamina_ratio = max(0, min(1, self.stamina / MAX_STAMINA))
        fill_width = int(bar_width * stamina_ratio)
        color = (
            int(255 * (1 - stamina_ratio)),
            int(255 * stamina_ratio),
            0
        )
        pygame.draw.rect(screen, color, (x - bar_width // 2, y, fill_width, bar_height))
        # Ramka
        pygame.draw.rect(screen, (0, 0, 0), (x - bar_width // 2, y, bar_width, bar_height), 1)

    # Usuń całą metodę get_inputs z tej klasy!
