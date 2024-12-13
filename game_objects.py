'''the overall structure of how this frogger implementation works is inspired by another
implementation of frogger that sadly had too big of a state space due to the large board size
https://github.com/jgubert/frogger/blob/master/frogger.py
'''
import pygame
from constants import (
    CELL_SIZE, FROG_COLOR, ENEMY_COLOR, PLATFORM_COLOR,
    BIG_PLATFORM_COLOR, ARRIVED_COLOR, GOAL_COLOR, GRID_COLS, GRID_ROWS
)

class Frog:
    def __init__(self, grid_x, grid_y):

        self.grid_x = grid_x
        self.grid_y = grid_y
        self.lives = 1
        self.width = 1
        self.height = 1

    def move(self, direction):
        new_x = self.grid_x
        new_y = self.grid_y

        if direction == 'up' and self.grid_y > 0:
            new_y -= 1
        elif direction == 'down' and self.grid_y < GRID_ROWS - 1:
            new_y += 1
        elif direction == 'left' and self.grid_x > 0:
            new_x -= 1
        elif direction == 'right' and self.grid_x < GRID_COLS - 1:
            new_x += 1

        self.grid_x = new_x
        self.grid_y = new_y

    def draw(self, surface):
        pygame.draw.rect(surface, FROG_COLOR, self.get_rect())

    def get_rect(self):
        return pygame.Rect(
            self.grid_x * CELL_SIZE,
            self.grid_y * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )

class Enemy:
    def __init__(self, grid_x, grid_y, direction, speed, width):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.direction = direction
        self.speed = speed
        self.width = width
        self.height = 1

    def move(self):
        if self.direction == 'right':
            self.grid_x += self.speed
            if self.grid_x >= GRID_COLS:
                self.grid_x = -self.width
        elif self.direction == 'left':
            self.grid_x -= self.speed
            if self.grid_x < -self.width:
                self.grid_x = GRID_COLS

    def draw(self, surface):
        pygame.draw.rect(surface, ENEMY_COLOR, self.get_rect())

    def get_rect(self):
        return pygame.Rect(
            self.grid_x * CELL_SIZE,
            self.grid_y * CELL_SIZE,
            CELL_SIZE * self.width,
            CELL_SIZE
        )

class Platform:
    def __init__(self, grid_x, grid_y, direction, speed, width):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.direction = direction
        self.speed = speed
        self.width = width
        self.height = 1

    def move(self):
        if self.direction == 'right':
            self.grid_x += self.speed
            if self.grid_x >= GRID_COLS:
                self.grid_x = -self.width
        elif self.direction == 'left':
            self.grid_x -= self.speed
            if self.grid_x < -self.width:
                self.grid_x = GRID_COLS

    def draw(self, surface):
        color = BIG_PLATFORM_COLOR if self.width >= 5 else PLATFORM_COLOR
        pygame.draw.rect(surface, color, self.get_rect())

    def get_rect(self):
        return pygame.Rect(
            self.grid_x * CELL_SIZE,
            self.grid_y * CELL_SIZE,
            CELL_SIZE * self.width,
            CELL_SIZE
        )

#goals, but they should only be goals if they are occupied
class ArrivedSlot:
    def __init__(self, grid_x, grid_y):

        self.grid_x = grid_x
        self.grid_y = grid_y
        self.width = 1
        self.height = 1
        self.occupied = False

    def occupy(self):
        self.occupied = True

    def draw(self, surface):
        color = GOAL_COLOR
        if self.occupied:
            color = ARRIVED_COLOR
        pygame.draw.rect(surface, color, self.get_rect())

    def get_rect(self):
        return pygame.Rect(
            self.grid_x * CELL_SIZE,
            self.grid_y * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
