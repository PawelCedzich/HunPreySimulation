from shared import Agent, MAX_STAMINA, MAX_SPEED
import math

class Predator(Agent):
    VIEW_ANGLE = 180    
    VIEW_DISTANCE = 100

    def __init__(self, genome, net):
        super().__init__(genome, net)
        self.view_distance = self.VIEW_DISTANCE
        self.reproduction_cooldown = 0
        self.eat_cooldown = 0  

    def update(self, preys, predators=None):
        if not self.alive:
            return

        self.ticks_alive += 1 

        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
        if self.eat_cooldown > 0:
            self.eat_cooldown -= 1

        if predators is None:
            objects = preys
        else:
            objects = preys + [pred for pred in predators if pred is not self]

        inputs = self.get_inputs(objects)
        output = self.net.activate(inputs)

        turn = (output[0] * 2 - 1) * 5
        speed = max(output[1] * MAX_SPEED * 1.2, 0)

        self.direction = (self.direction + turn) % 360
        self.speed = speed

        self.move()
        self.decrease_stamina()

        # Polowanie na prey
        for prey in preys:
            if prey.alive and math.hypot(prey.x - self.x, prey.y - self.y) < 15:
                self.stamina = min(MAX_STAMINA, self.stamina + 40)
                prey.alive = False
                self.eat_cooldown = 25
                self.genome.fitness += 10
                break

        # Rozmnażanie
        if self.stamina > 90 and self.reproduction_cooldown == 0:
            self.genome.fitness += 10
            self.stamina -= 40
            self.eat_cooldown = 35
            self.reproduction_cooldown = 50
            return "reproduce"

    def draw_hunger_bar(self, screen):
        """
        Rysuje pasek głodu (staminy) nad predatorem.
        """
        import pygame  # Upewnij się, że pygame jest zainstalowany

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
        # Opcjonalnie: ramka
        pygame.draw.rect(screen, (0, 0, 0), (x - bar_width // 2, y, bar_width, bar_height), 1)
