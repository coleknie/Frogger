'''Q learning agent for Frogger'''

'''Several parts of functionality are inspired by a tutorial by Cristian Leo, mainly how Q values are stored.
I have never used pickle before and it proved useful: https://github.com/cristianleoo/Reinforcement-Learning?tab=readme-ov-file'''

import random
from collections import defaultdict
import pickle

class QAgent:
    def __init__(self, actions, alpha=0.5, gamma=0.99, lambda_=0.5,
                 epsilon=1.0, epsilon_decay=0.99999, min_epsilon=0.01, initial_epsilon=1.0):
                 #initial epsilon is for when we have to reset epsilon
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.lambda_ = lambda_
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.initial_epsilon = initial_epsilon

        self.Q = {}
        self.EligibilityTraces = {}

    #levels are stored separately due to Q table issues
    def ensure_level_exists(self, level):
        if level not in self.Q:
            self.Q[level] = defaultdict(float)
        if level not in self.EligibilityTraces:
            self.EligibilityTraces[level] = defaultdict(float)


    #used when training multiple levels, or when forogger hits a goal.
    def reset_epsilon(self):
        self.epsilon = self.initial_epsilon

    def get_flattened_state(self, state, position, level):
        flat_state = tuple(cell for row in state for cell in row)
        return (flat_state, position)

    def choose_action(self, state, position, level):

        self.ensure_level_exists(level)
        flattened_state = self.get_flattened_state(state, position, level)
        if random.random() < self.epsilon:
            #explore
            action = random.choice(self.actions)
            self.reset_traces(level)
            return action, True

        else:
            #exploit
            q_values = [self.Q[level][(flattened_state, a)] for a in self.actions]
            max_q = max(q_values)
            max_actions = [a for a, q in zip(self.actions, q_values) if q == max_q]
            action = random.choice(max_actions)
            return action, False

    
    def update(self, state, position, action, reward, next_state, next_position, level, next_level, done):

        self.ensure_level_exists(level)
        self.ensure_level_exists(next_level)

        flattened_state = self.get_flattened_state(state, position, level)
        next_flattened_state = self.get_flattened_state(next_state, next_position, next_level)

        current_q = self.Q[level][(flattened_state, action)]
        if done:
            target = reward
        else:
            successor_max = max([self.Q[next_level][(next_flattened_state, a)] for a in self.actions])
            target = reward + self.gamma * successor_max
        delta = target - current_q

        self.EligibilityTraces[level][(flattened_state, action)] += 1

        #update state action values based on eligbility trace and current reward
        for (s, a), e in list(self.EligibilityTraces[level].items()):
            self.Q[level][(s, a)] += self.alpha * delta * e
            if done:
                self.EligibilityTraces[level][(s, a)] = 0
            else:
                self.EligibilityTraces[level][(s, a)] *= self.gamma * self.lambda_

        if not done:
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)


    #traces reset upon 1) taking a random action and 2) scoring (this does not mean winning)
    def reset_traces(self, level=None):
        if level is not None:
            self.EligibilityTraces[level] = defaultdict(float)
        else:
            for lvl in self.EligibilityTraces.keys():
                self.EligibilityTraces[lvl] = defaultdict(float)

    def save_q_table(self, filename='q_table.pkl'):
        with open(filename, 'wb') as f:
            pickle.dump(self.Q, f)

    def load_q_table(self, filename='q_table.pkl'):
        try:
            with open(filename, 'rb') as f:
                loaded_q = pickle.load(f)
                self.Q = {}
                for lvl, q_values in loaded_q.items():
                    self.Q[lvl] = defaultdict(float, q_values)

            print("Q table found. Using q_table.pkl.")

        except FileNotFoundError:
            print("No Q-table found :(, starting from square one (shameless gridworld pun).")
            self.Q = {}

        # eset Eligibility Trace tables after load
        self.EligibilityTraces = {}
        for lvl in self.Q.keys():
            self.EligibilityTraces[lvl] = defaultdict(float)
