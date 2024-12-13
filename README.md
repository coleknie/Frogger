Software Requirements: Python 3.8 or later
The requirements in the requirements.txt file: install with pip install -r requirements.txt
Hardware Requirements: This was run on a 2020 Macbook Pro with 16GB memory, which slowed it down quite a bit, but the laptop used has appeared to be in decline for some time, so it is not entirely clear. I reccomend at least 8GB of RAM.

Explanation of project: This project aimed and succeded at using Q-Learning to beat an implentation of the frogger game in python.
The goal of the game is to get as many frogs across to the goals (only one frog for each goal) by dodging enemies (cars) and riding on platforms (logs) to avoid drowining in the lake between the start and goal.

The project began with me attempting to use an existing pygame implementation of frogger, but this proved too difficult as the state space was unnecesarily large due to the way it used sprites and pixels to detect colissions and represent positions of frogger and objects.

This over-complicated my ability to meaningfully use Q-learning, SARSA or Monte Carlo Tree Search. Instead, I converted the pygame code into something far more simple, a gird world interpretation of frogger. This would involve a 13 (rows) by 17 (columns) grid. Objects move as slow as .25 square spaces per frame, making the actual grid 13 x 68. This was a drastically smaller state space.
I changed up the rules for simplicity a bit. The spawn rate of objects does not increase when level increases, instead only the speed does. I chose to represent state space as frogger's location (unscaled). The domain for that is x: (0, 16) and y (0,12). However, frogger's x position can have a decimal ending in .25, .5 or .75. This is because platforms can move at these speeds.
The 13x17(x4) grid is simply a map of the current board state with 0s indicated unsafe positions and 1s indicaing safe positions. Because each row in frogger has a fixed velocity (vis-a-vis the level), we only need to give our Q-learning agent frogger's position, a current board state of safe locations, and the level. The basic rules of frogger remain the same.

To train my agent, I assigned rewards to going further (closer to the goal/home row). Every time an episode started, I keep track of the farthest row he gets. He only incurs a reward when getting to the next row. This is to prevent frogger from staying in the same row endlessly and also to discourage moving back and forth between rows to reep rewards.
I also used eligibility tracing (lambda) to assign positive rewards to successful paths.

I used the following values to train my agent: alpha=0.5, gamma=0.9995, lambda_=0.5, epsilon=1.0, epsilon_decay=0.999, min_epsilon=0.05
We start with such a high epsilon value because frogger has a hard time waiting for platforms to come. By encouraging exploration with an epsilon decay and minimum epsilon of 0.05, it allows frogger to more quickly learn that crossing the river, no matter how daunting, will reep rewards.

Here is how to run my code:
To play frogger yourself (it has a low fps and is choppy, be warned!)
  python main.py --mode keyboard --render
To train 2 levels (it needs at least 10,000 episodes for level 2, in my experience, but I would probably recommend 15000):
  python main.py --mode train --levels 2  --episodes_per_level 10000
Alternatively, you could run it with render enabled:
  python main.py --mode train --render --levels 2  --episodes_per_level 10000

Finally, to see if your frog has learned anything useful or will be eaten by a sea monster never to see the light of day again, try:
python main.py --mode ai --render

In all cases, the score will print to the terminal after each game over or win.

References:
My Q Learning section was partially inspired by Cristian Leo's reinforcement learning tutorial:
https://github.com/cristianleoo/Reinforcement-Learning/blob/main/2.%20Q-Learning/main.py

Along with my frogger logic, which though different was informed by João Pedro Gubert de Souza's work implementing a similar pygame frogger.
https://github.com/jgubert/frogger

I also cite the course material, including the Pacman assignments, for informing how I represented gamestates.
