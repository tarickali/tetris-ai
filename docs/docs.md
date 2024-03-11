# Documentation

## Usage

Below is a snippet for how to use this project. The source file is expected to be at the same level as the `tetris` folder.

```{python}
from tetris import Game
from configs import classic_config
from agent import Agent

def main():
    config = {
        "grid": {"shape": (10, 40)}
        "tetrominos": {
            "shapes": classic["shapes"]
            "colors": classic["colors"]
        }
        "systems: {
            "generation": {
                "bag_size": 7,
                "minimum_next": 1,
            },
            "holding": {
                "pause": 1
            }
        }
    }

    game = Game(classic_config)
    game.start()

    agent = Agent()

    while not game.terminal():
        pass
```

## Game

### Constants and Variables

The main `Game` object is designed to be agnostic to several customizable variables. The general overview of the variable aspects of a game are:

1. Gridworld dimensions
2. Tetromino shapes, rotation sequences, and colors
3. Generation system for tetrominos
4. Holding system
5. Scoring and level system
<!-- 5. Visible next tetrominos -->

<!--
- The multipliers used for the scoring system
- The speed multipliers for each level
- The built-in game down-action frequency
- The generating distribution for tetrominos
- Holding stop duration
- Amount of next tetrominos that are visible
- Different rendering system?
-->

The hard-coded and constant aspects of the game mainly concern the rules and transition dynamics of the game. In particular:

1. Game actions are set to the standard set of six actions {right, left, down, drop, rotate, and hold} with each affecting the game state in the expected way
2. New tetrominos are always placed such that the topleft entry of the shape is at (grid width / 2, 0)
3. Terminal state of the game is reached when the new tetrominos collide with the grid

### State

The state encapsulates everything needed to build and restore the `Game`. The game state is a dictionary composed of the following.

#### Board

A list of lists of integers that represent the underlying board of the grid. The entries of the board range from 0 -> K where 0 represent empty gridcells and the values in {1,...,K} represent the kind of shape of that block (primarily used for rendering purposes).

#### Current Tetromino

A dictionary of containing the kind, shapes, rotation, and position of the current tetromino. Practically, the most important aspects of this object are the position and shape value at the rotation index.

#### Next Tetrominos

A list of integers representing the kinds of the next tetrominos. Note that depending on the generation system, the length of this list will vary from 1 to T, where T is the max number specified.

#### Held Tetromino

An integer representing the kind of tetromino that is currently being held. If no tetromino is currently being held then value is -1.

#### Info

A dictionary containing game-level information such as score, lines, and hold duration.

#### System

A dictionary of objects and values that deal with functionalities outside the game. Namely, since Tetris has a random component to it, to ensure that subseqeunt iterations from a state are the same, we need to store the RNG state.

### Observation

Observations are what are provided to an agent so that they may select their action. Regardless of the concrete observation used, all observations are derived from the game state. Since different game configurations and AI experiments have different observations that are more suitable, the construction of an observation is best left for the user/experimenter.

However, a set of concrete observations are provided for reference and quick-use.

### Methods

The most important methods for the game object are: `start`, `transition`, `terminal`, `save`, and `load`.

Notes:

- Need config and state to create a game from a saved state. Use config for init and load with state
- Start is used to create default initial state
- Transition is used to apply the action to the current state resulting in a new state
- Terminal is to used to check if the game is finished
- Save is used to return the full state object
