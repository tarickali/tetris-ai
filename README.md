# tetris-ai

A highly customizable Tetris engine designed to train AI agents.

## Introduction

How you ever wonder what Tetris would be like if you could change the shape of the world? Or even perhaps even the shape of the tetrominos themselves? Or what about the generation distribution of next tetrominos? How would different game dynamics and structures affect the behavior of optimal play? Would an AI agent trained on one variant be able to adapt to another?

These are some just fundamental questions that gave rise to the creation of this project. I thought it would be tedious to have to implement a new version of Tetris each time someone would want to run different AI experiments on the different variants of the game. And I was not able to find a simple to use and customizable implementation of Tetris anywhere else. So I decided to fill that gap with this project.

In a quick summary this project is intended to give easy access to a customizable implementation of the classic Tetris game. The primary reason for this is to allow users to examine and explore the behavior of AI agents across different game variants.

## Main idea behind the project

To be able to use this project, I think it is important to know the idea behind the code. Otherwise, you may not understand why and how to use this project for your own experiments.

The main idea behind this project is to construct an abstract representation of Tetris by only specifying the required components of a Game that are filled in by concrete descriptions specified in a configuration file. The abstract respresentations of Tetris are the grid, tetrominos, and the different tetrominos in a game state (current tetromino, next tetrominos, and held tetrominos).

A more detailed explanation of the components of a game and the required structure of configuration files can be found in the `docs/` folder.

## What do this project include?

This project is primarily meant to be just an engine to create Tetris variants. However, I could not help myself but to implement a few AI agents on different variants myself, partly because of my own interest in the problem but also to showcase how this project works.

The folder structure of this project is as follows:

```{}
engine/
    game.py
    grid.py
    tetromino.py
agents/
    genetic.py
    dqn.py
utils/
configs/
renderer.py
```

The `engine` and `agent` folders are self-explanatory about what they contain. In `utils/` there are utility functions to deal with configuration files and game state information. In `configs` there are a few example configuration files (mostly for inspiration). And `renderer.py` is a simple pygame UI for visualizing the game (look at `docs/` to understand its limitations).

## Usage

Although this project is not implemented as a `gymasium` environment, it nevertheless shares a familiar workflow. Here is the simplest code to run the environment.

```{python}
from tetris import Game
from tetris.utils import load_config

// If using a custom a config dictionary
config = {}
// If using built-in config file
config = load_config("classic")

game = Game(config)

state = game.start() # Start the game
while not game.terminal():
    action = ... # Add agent to get action
    state = game.transition(action) # Apply action to game
    game.render() # Render game in terminal
```

Note that unlike `gymnasium` environments, the `transition` method does not return a terminal signal or the transition reward. Instead, this information must be computed by the user when constructing an observation (see `docs/` about observations).

Look at `docs/recipes.md` for more example driver code.

## Future work and research questions

I like to think that this project is only a step towards to researching the generalizability of AI agent behavior across game variants. This project no doubt has faults, however, I hope that it inspires someone else to abstract a game or environment they are intereseted in and provide an interface to experiment for research.

With that being said, here are some future work and research questions to get you going with this project.

1. **Game Difficulties:** The classic game of Tetris is already a daunting task for an agent to master. In fact, classic Tetris is known to be NP-Complete even with the full sequence of tetrominos known. If classic Tetris is hard to train on, are there non-trivial variants that are easy to train on, as measured by training time and/or total score?
   1. Challenging follow-up: is there a relationship between game complexity and training difficulty? What game factors play a role in this relationship?
2. **State Information:** Usually only a few tetrominos are known in advanced, and typically only the immediate next tetromino is used to train an agent. What if the agent had access to the next n tetrominos? Would this allow an agent to train faster?
3. **Rewards:** Reward engineering is both an artform and a science. Usually the game score or some computed fitness function of the game state are used as the reward signal of the game. How would modifying the scoring system affect the agent's training? Does having large differences between line scores affect the agent's behavior? Does this affect the agent's ability to learn the optimal behavior of continuous play?
4. **Generalization:** If an agent already knows how to play one variant, can it effectively play another? How long does it take for the agent to adapt? Does intermixing different variants during training allow for generalized behavior to arise faster?
5. **Curriculum:** It is clear that some variants and sub-state spaces are easier to learn one than others. For example only using I shapes is easier than using only S and Z shapes which is easier than using all of the classic shapes. Does exposing an agent to a principled curriculum of progressively difficult variants result in more efficient overall training?
   - Note: this question is open-ended and requires significant work to first construct a curriculum and then apply it on an agent's training in a principled manner. The main problems deal with regressive behavior (an agent performs worse on simpler variants after learning harder one) and performance metrics (what is a satisficatory return before an agent can progress to the next task).

## Requirements

All requirements to run this project can be found in `requirements.txt`. To install you can clone this repo and simple run:

```{}
pip install -r requirements.txt
```

The main requirements to run the game are `numpy` and `pygame`, however, to train and run any AI agents, you will also need to install `torch` and `matplotlib`.

## Contributing

If this project intrigues you and you are interested in either contributing to this project or working on another similar project please contact me!
