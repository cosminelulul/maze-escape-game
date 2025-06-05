import turtle
import random
import math
import heapq
import os
import sys
import time


# ====================== #
# === CONFIGURATIONS === #
# ====================== #
TILE_SIZE = 40
GRID_WIDTH = 48
GRID_HEIGHT = 27

SPIKE_SPACING_MIN_DISTANCE = 4
NUM_SPIKES_PER_MAP = 50

PLAYER_SPEED = 200   # Lower = faster (ms)
ENTITY_SPEED = 250  # Lower = faster (ms)

# ====================== #
# ==== UTILITIES ======= #
# ====================== #
def rgb_to_turtle_color(r, g, b):
    return (r / 255.0, g / 255.0, b / 255.0)

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

# ====================== #
# === GAME OBJECTS ==== #
# ====================== #
class GameObject:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.sprite = turtle.Turtle()
        self.sprite.penup()
        self.sprite.shape(image)
        self.sprite.speed(0)
        self.update_position()

    def update_position(self):
        self.sprite.goto(self.x * TILE_SIZE - 960 + TILE_SIZE // 2,
                         self.y * TILE_SIZE - 540 + TILE_SIZE // 2)

class Spike(GameObject):
    def __init__(self, x, y, sprite = None):
        super().__init__(x, y, sprite)
        self.sprite.shapesize(0.1, 0.1)

class Entity(GameObject):
    def __init__(self, x, y):
        monster_choice = random.choice([monster1_sprite,monster2_sprite])
        super().__init__(x, y, monster_choice)
        self.path = []

    def compute_path(self, target_x, target_y, game):
        def heuristic(a, b):
            return math.hypot(a[0] - b[0], a[1] - b[1])

        start = (self.x, self.y)
        goal = (target_x, target_y)

        frontier = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            _, current = heapq.heappop(frontier)

            if current == goal:
                break

            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)]:
                next_pos = (current[0] + dx, current[1] + dy)
                if not game.is_valid_move(*next_pos):
                    continue

                step_cost = math.hypot(dx, dy)
                new_cost = cost_so_far[current] + step_cost
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(goal, next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current

        path = []
        current = goal
        while current != start:
            if current not in came_from:
                return []
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    def move_towards(self, target_x, target_y, game):

        if self.x == target_x and self.y == target_y:
            return

        if abs(self.x - target_x) + abs(self.y - target_y) == 1:
            self.path = [(target_x, target_y)]

        dx = target_x - self.x
        dy = target_y - self.y

        aggression = min(5, game.score // 200)
        predicted_x = target_x + (dx // max(abs(dx), 1)) * aggression if dx != 0 else target_x
        predicted_y = target_y + (dy // max(abs(dy), 1)) * aggression if dy != 0 else target_y

        predicted_x = max(0, min(GRID_WIDTH - 1, predicted_x))
        predicted_y = max(0, min(GRID_HEIGHT - 1, predicted_y))

        if not self.path or (self.path and not game.is_valid_move(*self.path[0])):
            self.path = self.compute_path(predicted_x, predicted_y, game)

        if self.path:
            next_x, next_y = self.path.pop(0)
            self.x = next_x
            self.y = next_y
            self.update_position()



class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, player_sprite)

    def move(self, dx, dy, game):
        new_x = self.x + dx
        new_y = self.y + dy

        if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
            game.map_index = (game.map_index + 1) % len(game.maps)
            game.load_map(game.map_index)
            return

        if game.is_valid_move(new_x, new_y):
            self.x = new_x
            self.y = new_y
            self.update_position()

class PowerUp(GameObject):
    def apply(self, game):
        pass

class Fruit(PowerUp):
    def __init__(self, x, y):
        fruit = random.choice([powerup1_sprite,powerup2_sprite,powerup3_sprite])
        super().__init__(x, y, fruit)
        self.sprite.shapesize(0.4, 0.4)

    def apply(self, game):
        game.player_boosted = True
        game.player_speed = PLAYER_SPEED // 2
        turtle.ontimer(game.remove_boost, 5000)
        self.score_multiplier = 5


class Shield(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, shield_sprite)
        self.sprite.shapesize(0.4, 0.4)

    def apply(self, game):
        game.has_shield = True

# ====================== #
# ===== GAME CORE ===== #
# ====================== #

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
       base_path = sys._MEIPASS
    else:
         base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


# ====================== #
# ====== SPRITES ======= #
# ====================== #


player_sprite = get_resource_path("assets/Player.gif")
monster1_sprite = get_resource_path("assets/Monster1.gif")
monster2_sprite = get_resource_path("assets/Monster2.gif")

cactus1_sprite = get_resource_path("assets/Cactus1.gif")
cactus2_sprite = get_resource_path("assets/Cactus2.gif")

tree1_sprite = get_resource_path("assets/Tree1.gif")
tree2_sprite = get_resource_path("assets/Tree2.gif")
rock_sprite = get_resource_path("assets/Rock.gif")

powerup1_sprite = get_resource_path("assets/GoldenApple.gif")
powerup2_sprite = get_resource_path("assets/SuspisciouslyGoodCarrot.gif")
powerup3_sprite = get_resource_path("assets/SmokyGrapes.gif")
shield_sprite = get_resource_path("assets/Shield.gif")

sand_bg = get_resource_path("assets/Sand.gif")
grass_bg = get_resource_path("assets/Grass.gif")
snow_bg = get_resource_path("assets/Snow.gif")

# ====================== #
# ====== Biomes ======= #
# ====================== #

biomes = {
    "Desert": {
        "assets": [cactus1_sprite, cactus2_sprite],
        "weights": [50,50],
        "bg": sand_bg
    },
    "Snowy Tundra": {
        "assets": [tree2_sprite, rock_sprite],
        "weights": [80, 20],
        "bg": snow_bg
    },
    "Tundra": {
        "assets": [tree1_sprite, rock_sprite],
        "weights": [75, 25],
        "bg": grass_bg
    }
}


class Game:
    def __init__(self):
        self.window = turtle.Screen()
        canvas = self.window.getcanvas()
        root = canvas.winfo_toplevel()
        root.attributes('-fullscreen', True)
        self.window.title("Maze Runner")
        self.text_objects = []
        self.sprites = [player_sprite,monster1_sprite,monster2_sprite,cactus1_sprite,cactus2_sprite,tree1_sprite,tree2_sprite,rock_sprite,powerup1_sprite, powerup2_sprite,powerup3_sprite,shield_sprite]
        self.biomes = [sand_bg,snow_bg,grass_bg]
        self.window.setup(width=1920, height=1080)
        self.window.tracer(0)

        for s in self.sprites:
            self.window.register_shape(s)

        for b in self.biomes:
            self.window.addshape(b)

        self.biome = random.choice(list(biomes.keys()))
        self.biome_data = biomes[self.biome]

        self.running = False
        self.player_move_timer = None
        self.score = 0
        self.map_index = 0
        self.maps = [self.generate_map() for _ in range(3)]
        self.score_multiplier = 1

        self.move_loop_calls = 0
        self.player_loop_started = False

        self.has_shield = False
        self.player_boosted = False
        self.player_speed = PLAYER_SPEED

        self.score_display = turtle.Turtle()
        self.score_display.hideturtle()
        self.score_display.color("black")
        self.score_display.penup()
        self.score_display.goto(800, 450)
        self.update_score_display()

        self.write_Text(150, 'Welcome to the Maze Runner! Avoid the monster while obtaining a score as high as possible.', "black")
        self.write_Text(75, 'The Monster can kill you in one hit. Pick up shields to avoid death, pick up fruits to gain speed!.', "black")
        self.write_Text(0,'Press SPACE TO START',"black")

        self.window.listen()
        self.window.onkey(self.start_game, "space")
        self.window.onkey(self.restart_game, "r")
        self.window.onkey(self.exit_fullscreen, "Escape")


    def exit_fullscreen(self):
        canvas = self.window.getcanvas()
        root = canvas.winfo_toplevel()
        root.attributes('-fullscreen', False)

    def write_Text(self, ypos, string,color):
        text = turtle.Turtle()
        text.hideturtle()
        text.penup()
        text.color(color)
        text.goto(0, ypos)
        text.write(string, align="center", font=("Arial", 24, "bold"))
        self.text_objects.append(text)

    def delete_text(self):
        for t in self.text_objects:
            t.clear()
            t.hideturtle()
        self.text_objects.clear()


    def cleanup_objects(self):
        for obj in getattr(self, "spikes", []):
            obj.sprite.ht()
            obj.sprite.clear()
            obj.sprite.reset()

        for obj in getattr(self, "powerups", []):
            obj.sprite.ht()
            obj.sprite.clear()
            obj.sprite.reset()

        if hasattr(self, "player") and self.player:
            self.player.sprite.ht()
            self.player.sprite.clear()
            self.player.sprite.reset()
            self.player = None

        if hasattr(self, "entity") and self.entity:
            self.entity.sprite.hideturtle()
            self.entity.sprite.clear()
            self.entity.sprite.reset()
            self.entity = None

        if hasattr(self, "score_display") and self.score_display:
            self.score_display.clear()
            self.score_display.hideturtle()


        self.spikes = []
        self.powerups = []
        self.player = None
        self.entity = None


    def generate_map(self):
        grid = [["." for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        placed = []
        attempts = 0

        while len(placed) < NUM_SPIKES_PER_MAP and attempts < 500:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            too_close = any(distance((x, y), pos) < SPIKE_SPACING_MIN_DISTANCE for pos in placed)
            if not too_close:
                placed.append((x, y))
                grid[y][x] = "S"
            attempts += 1
        return grid

    def load_map(self, index):
        for spike in getattr(self, "spikes", []):
            spike.sprite.hideturtle()
        for p in getattr(self, "powerups", []):
            p.sprite.hideturtle()

        self.spikes = []
        self.powerups = []
        self.matrix = self.maps[index]

        for y, row in enumerate(self.matrix):
            for x, cell in enumerate(row):
                if cell == "S":
                    spike = Spike(x, y, random.choices(self.biome_data["assets"], weights = self.biome_data["weights"], k=1)[0])
                    self.spikes.append(spike)

        # Fruit
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if self.matrix[y][x] == ".":
                drink = Fruit(x, y)
                self.powerups.append(drink)
                break

        # Shield
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if self.matrix[y][x] == "." and all(p.x != x or p.y != y for p in self.powerups):
                shield = Shield(x, y)
                self.powerups.append(shield)
                break

        self.player.x, self.player.y = GRID_WIDTH // 2, GRID_HEIGHT // 2
        self.entity.x, self.entity.y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
        self.player.update_position()
        self.entity.update_position()


    def start_game(self):
        self.window.tracer(0)
        if not self.running:
            self.window.bgpic(self.biome_data["bg"])
            self.running = True
            self.score = 0
            self.delete_text()
            self.update_score_display()

            if self.player_move_timer is not None:
                self.window.ontimer(None, self.player_move_timer)

            self.player = Player(GRID_WIDTH // 2, GRID_HEIGHT // 2)
            self.entity = Entity(random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            self.spikes = []
            self.powerups = []

            self.has_shield = False
            self.player_boosted = False
            self.player_speed = PLAYER_SPEED

            self.setup_key_hold()

            self.load_map(self.map_index)
            self.update_player()
            self.update_entity()

            if not self.player_loop_started:
                self.player_loop_started = True
                self.window.ontimer(self.move_player_continuous, self.player_speed)

    def setup_key_hold(self):
        self.keys_held = {"w": False, "a": False, "s": False, "d": False}

        self.window.onkeypress(lambda: self.set_key("w", True), "w")
        self.window.onkeypress(lambda: self.set_key("a", True), "a")
        self.window.onkeypress(lambda: self.set_key("s", True), "s")
        self.window.onkeypress(lambda: self.set_key("d", True), "d")

        self.window.onkeyrelease(lambda: self.set_key("w", False), "w")
        self.window.onkeyrelease(lambda: self.set_key("a", False), "a")
        self.window.onkeyrelease(lambda: self.set_key("s", False), "s")
        self.window.onkeyrelease(lambda: self.set_key("d", False), "d")

        self.window.listen()

    def set_key(self, key, state):
        self.keys_held[key] = state

    def move_player_continuous(self):
        self.move_loop_calls += 1
        if self.running:
            dx = dy = 0
            if self.keys_held["w"]:
                dy += 1
            if self.keys_held["s"]:
                dy -= 1
            if self.keys_held["a"]:
                dx -= 1
            if self.keys_held["d"]:
                dx += 1

            if dx != 0 or dy != 0:
                norm = math.hypot(dx, dy)
                dx = round(dx / norm) if norm != 0 else 0
                dy = round(dy / norm) if norm != 0 else 0
                self.player.move(dx, dy, self)
                self.update_player()

                # !!!!Always reset the timer cleanly!!!!
            self.window.getcanvas().winfo_toplevel().after(self.player_speed, self.move_player_continuous)


    def update_score_display(self):
        self.score_display.clear()
        self.score_display.write(f"SCORE: {self.score}", align="left", font=("Arial", 16, "bold"))

    def is_valid_move(self, x, y):
        for spike in self.spikes:
            if spike.x == x and spike.y == y:
                return False
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT

    def update_player(self):
        if self.running:
            self.score += 10
            self.update_score_display()

            for powerup in self.powerups[:]:
                if powerup.x == self.player.x and powerup.y == self.player.y:
                    powerup.apply(self)
                    powerup.sprite.hideturtle()
                    self.powerups.remove(powerup)

            self.window.update()

    def update_entity(self):
        if not self.running:
            return


        self.entity.move_towards(self.player.x, self.player.y,self)

        if self.entity.x == self.player.x and self.entity.y == self.player.y:
            if self.has_shield:
                self.has_shield = False
                print("Shield absorbed the hit!")

                saved_text = turtle.Turtle()
                saved_text.hideturtle()
                saved_text.penup()
                saved_text.color("white")
                saved_text.goto(0, 0)
                saved_text.write("SAVED!", align="center", font=("Arial", 40, "bold"))
                self.window.ontimer(saved_text.clear, 1000)

                self.player_boosted = True
                self.player_speed = PLAYER_SPEED // 2
                self.score_multiplier = 5

                self.has_shield = True
                self.window.ontimer(lambda: setattr(self, 'has_shield', False), 3000)

                self.window.ontimer(self.remove_boost, 5000)
            else:
                self.running = False
                self.show_game_over()
                return

        self.window.update()
        adjusted_speed = max(30, ENTITY_SPEED - self.score // 100)
        self.window.ontimer(self.update_entity, adjusted_speed)

    def show_game_over(self):
        rem_score = self.score
        self.running = False
        self.cleanup_objects()

        if rem_score < 1000:

            # Game over message
            self.end_text = turtle.Turtle()
            self.end_text.hideturtle()
            self.end_text.penup()
            self.end_text.color("red")
            self.end_text.goto(0, 0)
            self.end_text.write(f"Game Over! Score: {self.score}\nPress R to Try Again",
                                align="center", font=("Arial", 24, "bold"))

            self.window.listen()
            self.window.onkey(self.restart_game, "r")



    def restart_game(self):
        if not self.running:
            self.end_text.clear()
            self.player_loop_started = False

            self.cleanup_objects()

            self.window.tracer(0)
            self.window.clear()
            self.window.bgpic("")

            self.window.update()

            self.start_game()

    def remove_boost(self):
        self.player_boosted = False
        self.player_speed = PLAYER_SPEED

# ====================== #
# ===== RUN GAME ====== #
# ====================== #
game = Game()
turtle.done()