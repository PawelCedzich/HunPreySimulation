from shared import Agent, MAX_HUNGER, MAX_SPEED
import math

class Predator(Agent):
    def update(self, preys):
        if not self.alive:
            return

        inputs = self.get_inputs(preys)
        output = self.net.activate(inputs)

        turn = (output[0] * 2 - 1) * 20
        speed = output[1] * MAX_SPEED

        self.direction = (self.direction + turn) % 360
        self.speed = speed

        # Calculate movement distance for fitness reward
        prev_x, prev_y = self.x, self.y
        self.move()
        distance_moved = math.hypot(self.x - prev_x, self.y - prev_y)
        self.genome.fitness += distance_moved * 0.01  # Small reward for movement

        self.decrease_hunger()

        # Check for reproduction
        if self.hunger > 90:  # Hunger threshold for reproduction
            self.genome.fitness += 20  # Reward for reproduction
            self.hunger = MAX_HUNGER * 0.8  # Set hunger to 80% after reproduction

        for prey in preys:
            if prey.alive and math.hypot(prey.x - self.x, prey.y - self.y) < 15:
                prey.alive = False
                self.hunger = min(MAX_HUNGER, self.hunger + 50)
                self.genome.fitness += 50
                break
