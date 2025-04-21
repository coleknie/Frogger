# Frogger Q-Learning Agent 🐸

This project implements a reinforcement learning agent trained using **Q-Learning** to play a grid-based version of the classic game **Frogger**. The goal is to get as many frogs across the map to safe zones while avoiding hazards like cars and water.

## 🧠 Project Overview

The original attempt used a `pygame`-based Frogger, but the pixel-based sprite representation created an overly large state space, making it impractical for Q-Learning, SARSA, or MCTS approaches.  
Instead, the environment was simplified into a **13x17 grid world** with fractional movement along the x-axis (0.25 resolution), leading to a more manageable **13x68** state space.

Frogger’s position, a board-safe-state map, and the level number are used as inputs to the agent.

**Key rules:**

- Object spawn rates are fixed; only speed increases with level.
- State space: `(x, y)` position where `x ∈ [0, 16]` (with .25 increments), `y ∈ [0, 12]`.
- Reward shaping encourages moving forward only (no back-and-forth exploitation).
- Uses **eligibility traces** (λ) to reinforce useful paths.

## 🏗️ Software Requirements

- Python **3.8+**

Install dependencies:

```bash
pip install -r requirements.txt
```

## 💻 Hardware Requirements

This was originally developed and tested on a **2020 MacBook Pro with 16GB RAM**. Performance may vary depending on your machine.  
Minimum recommendation: **8GB of RAM**.

## 🎮 Running the Project

All actions print a score to the terminal after each round (win or lose).

### ▶️ Play Frogger manually (keyboard-controlled)

```bash
python main.py --mode keyboard --render
```

> ⚠️ Note: Low FPS and some choppiness may occur.

---

### 🤖 Train the agent (2 levels, 10,000 episodes per level)

```bash
python main.py --mode train --levels 2 --episodes_per_level 10000
```

Optionally with rendering:

```bash
python main.py --mode train --render --levels 2 --episodes_per_level 10000
```

> 💡 It’s recommended to run **15,000+ episodes** per level for best results.

---

### 🧪 Let the AI play (watch the trained model)

```bash
python main.py --mode ai --render
```

---

## ⚙️ Training Parameters

- `alpha = 0.5` (learning rate)  
- `gamma = 0.9995` (discount factor)  
- `lambda = 0.5` (eligibility trace)  
- `epsilon = 1.0` → decays by `0.999` per episode to `min_epsilon = 0.05`

High initial exploration helps the agent learn patience (e.g., waiting for logs to float by before crossing water).

---

## 📚 References & Inspiration

- **Q-Learning Logic**:  
  Inspired by Cristian Leo’s [Q-Learning tutorial](https://github.com/cristianleoo/Reinforcement-Learning/blob/main/2.%20Q-Learning/main.py)
  
- **Frogger Environment Structure**:  
  Influenced by João Pedro Gubert de Souza’s [pygame frogger](https://github.com/jgubert/frogger)

- **State Representation**:  
  Informed by the classic **Pacman AI projects** used in many reinforcement learning courses.

---

Enjoy watching your frog learn — or get eaten by sea monsters 🐊!
