import pygame
from constants import (
    GRID_COLS, GRID_ROWS, CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT,
    BACKGROUND_COLOR, LAKE_COLOR, SAFE_ROW_COLOR, BLACK, WHITE
)

def draw_grid(surface):
    for x in range(GRID_COLS + 1):
        pygame.draw.line(
            surface,
            BLACK,
            (x * CELL_SIZE, 0),
            (x * CELL_SIZE, SCREEN_HEIGHT)
        )
    for y in range(GRID_ROWS + 1):
        pygame.draw.line(
            surface,
            BLACK,
            (0, y * CELL_SIZE),
            (SCREEN_WIDTH, y * CELL_SIZE)
        )

def draw_info(surface, state, font):
    info_text = f'Lives: {state.frog.lives}   Score: {state.score}   Level: {state.level}   Time: {int(state.time)}'
    text = font.render(info_text, True, WHITE)
    surface.blit(text, (10, SCREEN_HEIGHT - 30))

def draw_game(surface, state, render=True, font=None):
    if not render:
        return

    surface.fill(BACKGROUND_COLOR)

    #Lake
    pygame.draw.rect(
        surface,
        LAKE_COLOR,
        (
            0,
            1 * CELL_SIZE,
            SCREEN_WIDTH,
            5 * CELL_SIZE
        )
    )

    #Middle Safe ROw
    pygame.draw.rect(
        surface,
        SAFE_ROW_COLOR,
        (
            0,
            6 * CELL_SIZE,
            SCREEN_WIDTH,
            1 * CELL_SIZE
        )
    )

    #Road
    pygame.draw.rect(
        surface,
        BLACK,
        (
            0,
            7 * CELL_SIZE,
            SCREEN_WIDTH,
            5 * CELL_SIZE
        )
    )

    #Arrived 
    for slot in state.arrived_slots:
        slot.draw(surface)

    #Cars
    for enemy in state.enemies:
        enemy.draw(surface)

    #Logs
    for platform in state.platforms:
        platform.draw(surface)

    #Frog
    state.frog.draw(surface)

    #Grid with game info
    draw_grid(surface)
    if font:
        draw_info(surface, state, font)

    pygame.display.flip()
