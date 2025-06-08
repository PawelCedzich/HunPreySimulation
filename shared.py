import random
import math

# Shared constants
WIDTH = 1700
HEIGHT = 1000
MAX_STAMINA = 100
MAX_SPEED = 3
RAY_UPDATE_FREQ = 5
NUM_RAYS = 8
FIELD_OF_VIEW = 360
RAY_ANGLE = FIELD_OF_VIEW / NUM_RAYS
MAX_TURN_ANGLE = 15  # stopni na tick

class Agent:
    def __init__(self, genome, net):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.direction = random.uniform(0, 360)
        self.speed = 0
        self.stamina = MAX_STAMINA * 0.5
        self.alive = True
        self.genome = genome
        self.net = net
        self.inputs_cache = None  # Cache sensory data
        self.tick_since_last_ray = 0
        self.view_distance = 100  # Default view distance for agents
        self.ticks_alive = 0  # licznik przeżytych ticków

    def move(self):
        # Wywołuj po apply_network_output!
        rad = math.radians(self.direction)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed
        self.x = max(0, min(WIDTH, self.x))
        self.y = max(0, min(HEIGHT, self.y))

    def decrease_stamina(self):
        self.stamina -= 0.3 - (0.025 * abs(self.speed))
        if self.stamina > MAX_STAMINA:
            self.stamina = MAX_STAMINA
        if self.stamina <= 0:
            self.alive = False

    def get_inputs(self, objects):
        # Update sensory data only every RAY_UPDATE_FREQ steps
        if self.tick_since_last_ray >= RAY_UPDATE_FREQ or self.inputs_cache is None:
            self.inputs_cache = []
            for i in range(NUM_RAYS):
                ray_dir = (self.direction + i * RAY_ANGLE) % 360
                dist, obj_type, obj_dir, obj_speed = self.cast_ray(ray_dir, objects)
                # One-hot encoding typu obiektu
                is_prey = 1 if obj_type == 1 else 0
                is_predator = 1 if obj_type == 2 else 0
                is_food = 1 if obj_type == 3 else 0
                self.inputs_cache.append(dist / WIDTH)
                self.inputs_cache.append(is_prey)
                self.inputs_cache.append(is_predator)
                self.inputs_cache.append(is_food)
                self.inputs_cache.append(obj_dir / 360.0)
                self.inputs_cache.append(obj_speed / MAX_SPEED)
            # Dodatkowo własna stamina (lub hunger)
            self.inputs_cache.append(self.stamina / MAX_STAMINA)
            self.tick_since_last_ray = 0
        else:
            self.tick_since_last_ray += 1

        return self.inputs_cache

    def cast_ray(self, ray_dir, objects):
        min_dist = WIDTH
        obj_type = 0
        obj_dir = 0.0
        obj_speed = 0.0
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
                    # Typ obiektu: 1 = Prey, 2 = Predator, 3 = Food, 0 = brak
                    if hasattr(obj, "direction") and hasattr(obj, "speed"):
                        # Prey lub Predator
                        obj_type = 1 if obj.__class__.__name__ == "Prey" else 2
                        obj_dir = obj.direction
                        obj_speed = obj.speed
                    else:
                        obj_type = 3  # Food
                        obj_dir = 0.0
                        obj_speed = 0.0
        return min_dist, obj_type, obj_dir, obj_speed

    def apply_network_output(self, output):
        """
        Oczekiwane outputy sieci:
        output[0]: zmiana kierunku patrzenia (turn), zakres [-1, 1]
        output[1]: prędkość (speed), zakres [0, 1]
        """
        # Ogranicz i przeskaluj outputy
        turn = max(-1, min(1, output[0])) * MAX_TURN_ANGLE
        speed = max(0, min(1, output[1])) * MAX_SPEED
        self.direction = (self.direction + turn) % 360
        self.speed = speed
