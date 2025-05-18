from shared import Agent, MAX_STAMINA, MAX_SPEED
import math

class Prey(Agent):
    VIEW_ANGLE = 180  # pole widzenia dla Prey (możesz zmieniać w przyszłości)

    def __init__(self, genome, net):
        super().__init__(genome, net)
        self.reproduction_cooldown = 0
        self.eat_cooldown = 0  # cooldown na jedzenie

    def update(self, foods, predators):
        if not self.alive:
            return

        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
        if self.eat_cooldown > 0:
            self.eat_cooldown -= 1

        inputs = self.get_inputs(foods + predators)
        output = self.net.activate(inputs)
        # --- OUTPUT sieci: output[0] = turn (-1..1), output[1] = speed (0..1) ---
        # output[0]: zmiana kierunku patrzenia (turn)
        # output[1]: prędkość ruchu (speed)
        turn = (output[0] * 2 - 1) * 5
        speed = max(output[1] * MAX_SPEED, 0)

        self.direction = (self.direction + turn) % 360
        self.speed = speed

        # Calculate movement distance for fitness reward
        prev_x, prev_y = self.x, self.y
        self.move()
        distance_moved = math.hypot(self.x - prev_x, self.y - prev_y)
        self.genome.fitness += distance_moved * 0.01  # Small reward for movement

        self.decrease_stamina()

        for food in foods:
            if self.eat_cooldown == 0 and food.alive and math.hypot(food.x - self.x, food.y - self.y) < 10:
                self.stamina = min(MAX_STAMINA, self.stamina + 30)
                food.alive = False
                self.eat_cooldown = 5  # blokada na 5 ticków
                break

        # Check for reproduction (po zjedzeniu!)
        if self.stamina > 90 and self.reproduction_cooldown == 0:
            self.genome.fitness += 20  # Reward for reproduction
            self.stamina -= 40  # Set stamina to 80% after reproduction
            self.reproduction_cooldown = 30
            return "reproduce"
