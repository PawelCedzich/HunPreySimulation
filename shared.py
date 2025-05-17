import random
import math

# Shared constants
WIDTH = 1200
HEIGHT = 1000
MAX_HUNGER = 100
MAX_SPEED = 5
RAY_UPDATE_FREQ = 5
NUM_RAYS = 8
FIELD_OF_VIEW = 360
RAY_ANGLE = FIELD_OF_VIEW / NUM_RAYS

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
        self.inputs_cache = None  # Cache sensory data
        self.tick_since_last_ray = 0
        self.view_distance = 100  # Default view distance for agents

    def move(self):
        rad = math.radians(self.direction)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed
        self.x = max(0, min(WIDTH, self.x))
        self.y = max(0, min(HEIGHT, self.y))

    def decrease_hunger(self):
        self.hunger -= self.speed * 0.05
        if self.hunger <= 0:
            self.alive = False

    def get_inputs(self, objects):
        # Update sensory data only every RAY_UPDATE_FREQ steps
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
