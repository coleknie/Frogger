import pygame
import sys
import argparse
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, GAMETIME
from q_agent import QAgent
from game_state import GameState
from render import draw_game
import time

def main(mode, render, max_levels, episodes_per_level, screen, font):
    if mode == 'train':
        FPS = 10000
    else:
        FPS = 7

    if mode == 'train':
        #Training,
        actions = ['up', 'down', 'left', 'right']
        agent = QAgent(actions=actions, alpha=0.5, gamma=0.9995, lambda_=0.5,
                       epsilon=1.0, epsilon_decay=0.999, min_epsilon=0.05, initial_epsilon=1.0)
        agent.load_q_table('q_table.pkl')

        episode_count = 0

        for lvl in range(1, max_levels + 1):
            agent.reset_epsilon()
            for ep in range(episodes_per_level):
                episode_count += 1
                state = GameState(initial_level=lvl, fixed_level=True)
                total_reward = 0

                while True:
                    pygame.time.Clock().tick(FPS)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            agent.save_q_table()
                            pygame.quit()
                            sys.exit()

                    current_state, current_position = state.get_gamestate()
                    action, is_exploration = agent.choose_action(current_state, current_position, state.level)
                    state.frog.move(action)

                    previous_lives = state.frog.lives
                    state.update(FPS)
                    next_state, next_position = state.get_gamestate()

                    if state.is_terminal():
                        if state.win:
                            reward, goal_reached = 10000, False
                        else:
                            reward, goal_reached = 0, False
                    else:
                        reward, goal_reached = state.get_reward()

                    total_reward += reward

                    agent.update(
                        state=current_state,
                        position=current_position,
                        action=action,
                        reward=reward,
                        next_state=next_state,
                        next_position=next_position,
                        level=state.level,
                        next_level=state.level,
                        done=state.is_terminal()
                    )

                    #RESET ELIGIBILITY TRACES WHEN FROGGER DIES
                    if (state.frog.lives < previous_lives) and not state.game_over:
                        agent.reset_traces(state.level)
                    if goal_reached:
                        agent.reset_traces(state.level)
                    if render and screen and font:
                        draw_game(screen, state, render=render, font=font)

                    if state.is_terminal():
                        print(f'Level {lvl}, Episode {episode_count}: Score = {state.score}, Total Reward = {total_reward}')
                        agent.save_q_table()
                        break

        print("Training complete. Enjoy youself a gooseburger and some fine food.")
        agent.save_q_table()

    elif mode == 'ai':
        # AI Mode, epsilon = 0. We are using the leanred policy, - Note, no Q values are actually being updated
        actions = ['up', 'down', 'left', 'right']
        agent = QAgent(actions=actions, alpha=0.5, gamma=0.9995, lambda_=0.5,
                       epsilon=0.0, epsilon_decay=0.999, min_epsilon=0.05, initial_epsilon=0.0)
        agent.load_q_table('q_table.pkl')

        state = GameState(initial_level=1, fixed_level=False)
        state.frog.lives = 3
        episode_number = 1
        total_reward = 0

        while True:
            pygame.time.Clock().tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    agent.save_q_table()
                    pygame.quit()
                    sys.exit()

            current_state, current_position = state.get_gamestate()
            action, is_exploration = agent.choose_action(current_state, current_position, state.level)
            state.frog.move(action)

            previous_lives = state.frog.lives
            state.update(FPS)
            next_state, next_position = state.get_gamestate()

            if state.is_terminal():
                if state.win:
                    reward, goal_reached = 10000, False
                else:
                    reward, goal_reached = 0, False
            else:
                reward, goal_reached = state.get_reward()

            total_reward += reward

            if render and screen and font:
                draw_game(screen, state, render=render, font=font)

            if state.is_terminal():
                print(f'Episode {episode_number}: Score = {state.score}') #prints episode number and score (rather than reward)
                episode_number += 1
                total_reward = 0
                state = GameState(initial_level=1, fixed_level=False)

    elif mode == 'keyboard':
        # Keyboard Mode
        state = GameState(initial_level=1, fixed_level=False)
        state.frog.lives = 3
        episode_number = 1
        total_reward = 0
        while True:
            pygame.time.Clock().tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                state.frog.move('up')
            elif keys[pygame.K_DOWN]:
                state.frog.move('down')
            elif keys[pygame.K_LEFT]:
                state.frog.move('left')
            elif keys[pygame.K_RIGHT]:
                state.frog.move('right')

            previous_lives = state.frog.lives
            state.update(FPS)
            next_state, next_position = state.get_gamestate()

            if state.is_terminal():
                if state.win:
                    reward, goal_reached = 10000, False
                else:
                    reward, goal_reached = 0, False
            else:
                reward, goal_reached = state.get_reward()

            total_reward += reward
            if render and screen and font:
                draw_game(screen, state, render=render, font=font)

            if state.is_terminal():
                print(f'Episode {episode_number}: Score = {state.score}, Total Reward = {total_reward}')
                episode_number += 1
                total_reward = 0
                # Reset to level 1 after death
                state = GameState(initial_level=1, fixed_level=False)

if __name__ == "__main__":
    pygame.init()

    parser = argparse.ArgumentParser(description='Frogger Q-Lambda Agent')
    parser.add_argument('--mode', type=str, choices=['train', 'ai', 'keyboard'], required=True, help='Mode: train, ai, or keyboard')
    parser.add_argument('--render', action='store_true', help='Toggle rendering (default- disabled)')
    parser.add_argument('--levels', type=int, default=1, help='Number of levels to train through (defaul- 1)')
    parser.add_argument('--episodes_per_level', type=int, default=5000, help='Number of episodes per level in training (default- 5,000), at least 10,000 recommende for advanced levels')
    args = parser.parse_args()

    if args.render:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Frogger Q-Lambda')
        font = pygame.font.SysFont(None, 24)
    else:
        screen = None
        font = None

    clock = pygame.time.Clock()
    main(mode=args.mode, render=args.render, max_levels=args.levels, episodes_per_level=args.episodes_per_level, screen=screen, font=font)