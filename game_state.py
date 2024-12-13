'''the overall structure of how this frogger implementation works is inspired by another
implementation of frogger that sadly had too big of a state space due to the large board size
https://github.com/jgubert/frogger/blob/master/frogger.py
'''
from collections import defaultdict
from constants import CELL_SIZE, GRID_COLS, GRID_ROWS, GAMETIME
from game_objects import Frog, Enemy, Platform, ArrivedSlot
import pygame

class GameState:
    def __init__(self, initial_level=1, fixed_level=False):
        self.frog = Frog(GRID_COLS // 2, GRID_ROWS - 1)
        self.score = 0
        self.level = initial_level
        self.time = GAMETIME
        self.game_over = False
        self.win = False
        self.visited_rows = set()
        self.reached_goal = False
        self.fixed_level = fixed_level

        #base velocity, increments at each level while spawn interval does not
        self.base_road_rows = {
            11: {'direction': 'right', 'speed': 0.25, 'width': 2, 'spawn_interval': 30},
            10: {'direction': 'left', 'speed': 0.5, 'width': 3, 'spawn_interval': 20},
            9:  {'direction': 'right', 'speed': 0.75, 'width': 2, 'spawn_interval': 30},
            8:  {'direction': 'left', 'speed': 1.0, 'width': 3, 'spawn_interval': 30},
            7:  {'direction': 'right', 'speed': 0.5, 'width': 3, 'spawn_interval': 30}
        }

        self.base_platform_rows = {
            5: {'direction': 'left', 'speed': 0.25, 'width': 3, 'spawn_interval': 20},
            4: {'direction': 'left', 'speed': 0.75, 'width': 6, 'spawn_interval': 10},
            3: {'direction': 'right', 'speed': 0.5, 'width': 4, 'spawn_interval': 15},
            2: {'direction': 'left', 'speed': 0.5, 'width': 3, 'spawn_interval': 10},
            1: {'direction': 'right', 'speed': 0.5, 'width': 3, 'spawn_interval': 10}
        }

        #starts with base gamestate
        self.setup_level()

        self.previous_score = 0
        self.previous_time = GAMETIME
        self.previous_lives = self.frog.lives

    def setup_level(self):
        self.enemies = []
        self.platforms = []
        self.arrived_slots = [ArrivedSlot(x, 0) for x in range(2, GRID_COLS, max(1, int(GRID_COLS / 5)))]

        self.road_rows = {}
        for row, props in self.base_road_rows.items():
            self.road_rows[row] = {
                'direction': props['direction'],
                'speed': props['speed'] * self.level,
                'width': props['width'],
                'spawn_interval': props['spawn_interval']
            }

        self.platform_rows = {}
        for row, props in self.base_platform_rows.items():
            self.platform_rows[row] = {
                'direction': props['direction'],
                'speed': props['speed'] * self.level,
                'width': props['width'],
                'spawn_interval': props['spawn_interval']
            }

        self.enemy_spawn_timers = {row: 0 for row in self.road_rows.keys()}
        self.platform_spawn_timers = {row: 0 for row in self.platform_rows.keys()}

        self.time = GAMETIME
        self.reset_frog_position()

    def spawn_enemy(self, row):
        properties = self.road_rows[row]
        direction = properties['direction']
        speed = properties['speed']
        width = properties['width']
        grid_x = -width if direction == 'right' else GRID_COLS
        enemy = Enemy(grid_x, row, direction, speed, width)
        self.enemies.append(enemy)

    def spawn_platform(self, row):
        properties = self.platform_rows[row]
        direction = properties['direction']
        speed = properties['speed']
        width = properties['width']
        grid_x = -width if direction == 'right' else GRID_COLS
        platform = Platform(grid_x, row, direction, speed, width)
        self.platforms.append(platform)

    #updates spawn times and resets them and spawns if interval is met
    def update_spawn_timers(self):
        for row in self.road_rows:
            self.enemy_spawn_timers[row] += 1
            if self.enemy_spawn_timers[row] >= self.road_rows[row]['spawn_interval']:
                self.spawn_enemy(row)
                self.enemy_spawn_timers[row] = 0

        for row in self.platform_rows:
            self.platform_spawn_timers[row] += 1
            if self.platform_spawn_timers[row] >= self.platform_rows[row]['spawn_interval']:
                self.spawn_platform(row)
                self.platform_spawn_timers[row] = 0


    def get_reward(self):
        if self.reached_goal:
            self.reached_goal = False
            self.visited_rows = set()
            return 10000, True

        if self.game_over:
            return -100, False
        else:
            current_row = self.frog.grid_y
            if current_row not in self.visited_rows:
                self.visited_rows.add(current_row)
                return (GRID_ROWS - current_row) * 10, False
            else:
                return 0, False

    def update(self, FPS):
        self.previous_score = self.score
        self.previous_time = self.time
        self.previous_lives = self.frog.lives

        self.update_spawn_timers()

        for enemy in self.enemies:
            enemy.move()

        for platform in self.platforms:
            platform.move()

        #Despawns cars and platforms out of bounds
        self.enemies = [enemy for enemy in self.enemies if -enemy.width < enemy.grid_x < GRID_COLS]
        self.platforms = [platform for platform in self.platforms if -platform.width < platform.grid_x < GRID_COLS]

        #checks roadkill (colissions with frog and cars)
        for enemy in self.enemies:
            if self.frog.get_rect().colliderect(enemy.get_rect()):
                self.frog.lives -= 1
                self.reset_frog_position()
                if self.frog.lives <= 0:
                    self.game_over = True
                break

        #checks if forgger is on a platform
        on_platform = False
        for platform in self.platforms:
            if self.frog.get_rect().colliderect(platform.get_rect()):
                on_platform = True
                if platform.direction == 'right':
                    self.frog.grid_x += platform.speed
                    self.frog.grid_x = min(self.frog.grid_x, GRID_COLS - self.frog.width)
                else:
                    self.frog.grid_x -= platform.speed
                    self.frog.grid_x = max(self.frog.grid_x, 0)
                break

        #frogger is in the lake if true, dies
        if 1 <= self.frog.grid_y <= 5 and not on_platform:
            self.frog.lives -= 1
            self.reset_frog_position()
            if self.frog.lives <= 0:
                self.game_over = True

        #Frog arrival
        if self.frog.grid_y == 0:
            BUFFER = 0.75 * CELL_SIZE
            valid_goal = False
            for slot in self.arrived_slots:
                #sensitivity for scoring, having only one frame one can score is unreasonable and glitchy
                buffered_rect = slot.get_rect().copy()
                buffered_rect.x -= BUFFER
                buffered_rect.width += 2 * BUFFER

                if self.frog.get_rect().colliderect(buffered_rect) and not slot.occupied:
                    slot.occupy()
                    self.score += 50 - int((GAMETIME - self.time) / 2)
                    self.time = GAMETIME
                    valid_goal = True
                    self.reset_frog_position()
                    self.reached_goal = True
                    break

            if not valid_goal:
                self.frog.grid_y += 1

        #if all slots are occupied the level increments and the board is reset
        if all(slot.occupied for slot in self.arrived_slots):
            if self.fixed_level:
                self.game_over = True
                self.win = True
            else:
                self.level += 1
                self.setup_level()

        #timer
        self.time -= 1 / FPS
        if self.time <= 0:
            self.frog.lives -= 1
            if self.frog.lives <= 0:
                self.game_over = True
            else:
                self.reset_frog_position()
                self.time = GAMETIME

    def reset_frog_position(self):
        self.frog.grid_x = GRID_COLS // 2
        self.frog.grid_y = GRID_ROWS - 1

    def is_terminal(self):
        return self.game_over

    def get_score(self):
        return self.score

    def get_gamestate(self, scale_factor=4):
        #the slowest objects can move at is .25. no matter what all speeds when multiplied by 4 are whole numbers.
        #Because objects can be between grid squares, we need to scale our grid to represent our grid in a binary array
        scaled_cols = GRID_COLS * scale_factor
        scaled_rows = GRID_ROWS
        gamestate = [[0 for _ in range(scaled_cols)] for _ in range(scaled_rows)]

        #these rows don't have any hazards
        safe_rows = [6, 12]
        for row in safe_rows:
            for x in range(scaled_cols):
                gamestate[row][x] = 1

        #logs
        for platform in self.platforms:
            platform_start = int(platform.grid_x * scale_factor)
            platform_end = int((platform.grid_x + platform.width) * scale_factor)
            for x in range(platform_start, platform_end):
                if 0 <= x < scaled_cols:
                    gamestate[platform.grid_y][x] = 1

        #arrived slots
        for x in range(scaled_cols):
            gamestate[0][x] = 0
        for slot in self.arrived_slots:
            if not slot.occupied:
                goal_start = int(slot.grid_x * scale_factor)
                goal_end = int((slot.grid_x + 1) * scale_factor)
                for xx in range(goal_start, goal_end):
                    if 0 <= xx < scaled_cols:
                        gamestate[0][xx] = 1

        #road rows are safe...
        road_rows = range(7, 12)
        for row in road_rows:
            for x in range(scaled_cols):
                gamestate[row][x] = 1

        #unless they have cars +_+
        for enemy in self.enemies:
            enemy_start = int(enemy.grid_x * scale_factor)
            enemy_end = int((enemy.grid_x + enemy.width) * scale_factor)
            for x in range(enemy_start, enemy_end):
                if 0 <= x < scaled_cols:
                    gamestate[enemy.grid_y][x] = 0

        frogger_position = (self.frog.grid_x, self.frog.grid_y)
        return gamestate, frogger_position


    #used for debugging
    def print_gamestate(self, scale_factor=4):
        gamestate, frogger_position = self.get_gamestate(scale_factor=scale_factor)
        print("Scaled Game State:")
        for row in gamestate:
            print("".join(str(cell) for cell in row))
        print("\nFrogger Position (Unscaled):")
        print(f"X: {frogger_position[0]}, Y: {frogger_position[1]}")
