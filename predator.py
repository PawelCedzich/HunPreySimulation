from shared import Agent, MAX_STAMINA, MAX_SPEED
import math

class Predator(Agent):
    VIEW_ANGLE = 120  # przykładowa wartość, możesz zmienić wg potrzeb
    VIEW_DISTANCE = 100  # przykładowy zasięg widzenia dla Predator

    def __init__(self, genome, net):
        super().__init__(genome, net)
        self.view_distance = self.VIEW_DISTANCE  # indywidualny zasięg widzenia
        self.reproduction_cooldown = 0
        self.eat_cooldown = 0  # cooldown na jedzenie

    def update(self, preys):
        if not self.alive:
            return

        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
        if self.eat_cooldown > 0:
            self.eat_cooldown -= 1

        inputs = self.get_inputs(preys)
        output = self.net.activate(inputs)
        # --- OUTPUT sieci: output[0] = turn (-1..1), output[1] = speed (0..1) ---
        # output[0]: zmiana kierunku patrzenia (turn)
        # output[1]: prędkość ruchu (speed)
        # output[0] jest w zakresie [0, 1] (wyjście sieci)
        # (output[0] * 2 - 1) przekształca zakres [0, 1] na [-1, 1]
        # potem mnożymy przez 5, więc turn jest w zakresie [-5, 5] stopni
        turn = (output[0] * 2 - 1) * 5
        speed = max(output[1] * MAX_SPEED, 0)

        self.direction = (self.direction + turn) % 360
        self.speed = speed

        # Calculate movement distance for fitness reward
        prev_x, prev_y = self.x, self.y
        self.move()
        distance_moved = math.hypot(self.x - prev_x, self.y - prev_y)
        self.genome.fitness += distance_moved * 0.001  # Small reward for movement

        self.decrease_stamina()

        # Check for reproduction
        if self.stamina > 90 and self.reproduction_cooldown == 0:
            self.genome.fitness += 20  # Reward for reproduction
            self.stamina -= 40
            self.reproduction_cooldown = 30
            return "reproduce"

        for prey in preys:
            if (
                self.eat_cooldown == 0
                and prey.alive
                and math.hypot(prey.x - self.x, prey.y - self.y) < 15
            ):
                prey.alive = False
                self.stamina = min(MAX_STAMINA, self.stamina + 35)
                self.genome.fitness += 20
                self.eat_cooldown = 5  # blokada na 5 ticków
                break
