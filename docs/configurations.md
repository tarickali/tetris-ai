# Game Configurations

## Introduction

The only differentiating aspect of this project compared to other tetris projects is the configurability of games. As such, to make use of this project, it is important to know what one can and can't do with a configuration file.

## Features

All configurations must be in a `json` file and have the following form:

```{}
{
    "grid": list[int, int],
    "tetrominos": dict[str, list[list[list]]],
    "systems": {
        "transition": dict[str, Any],
        "generation: dict[str, Any]
        "scoring": dict[str, Any],
    }
}
"
```

### Grid

The grid of the game can really only be configured by changing its shape. The expected list is [height, width].

### Tetrominos

Tetrominos can be configured according to their shapes. Each tetromino has a name, e.g. "T", "J", "E", "CustomPiece", etc. and a list of its rotations. Each rotation is a 2D list of 0s and 1s that represent the shape of the tetromino. The sequence of different shapes in the list represent the rotation order of that tetromino.

Note that although enforcing users to input the rotations for each tetromino may be tedious, it provides with fine-grain control over the rotation dynamics of each tetromino. In particular, there is no explicit limitation that a specific tetromino has to have the same underlying shape across rotations. For example, one can define a custom tetromino that goes from an long-I to a short-I and then back. In this way, shapes can be morphed through rotations.

To make it easier to customize a game, a dictionary of the original and some custom tetrominos is defined in `examples/tetrominos.py`.

#### Notes to Keep in Mind

- The order that each tetromino is defined matters since the initial shape is the default shape that will placed on the grid and the sequence are typically considered to be right rotations (although this does not matter and is not necessary).
- Ideally, to keep games "easy", shapes should not have closed shapes (like B, P, Q), however, although more difficult, a game is still playable with these shapes. It would be interesting to see how agents deal with such a problem.
- It is useful to have counter-parts for each tetromino in a game to balance the game, but this again is not necessary.
- To progressively make a game more difficult, look into generation system to adjust the distribution of tetrominos being produced.

### Systems

#### Transition

The transition expects a dictionary of the following form:

```{}
"enforce-down": {
    "active": bool
    "actions": list[str]
}
```

#### Generation

The transition expects a dictionary of the following form:

```{}
{
    "bag-size": int
    "next-size": int
    "distribution: {
        "type": "uniform" | "custom"
        "weights": dict[str, int] # only if type is custom
    }
}
```

#### Scoring

The transition expects a dictionary of the following form:

```{}
"type": "lines"
"lines": list[int]
```

or

```{}
"type": "multipliers"
"base": int
"multipliers": list[int]
```

## Examples

Examples of different configurations can be found in `configs/`.

## Important note

It is important to note that not all game configurations make sense and that the configuration options provided in this project may not fully capture the different dynamics you want. Nevertheless, I believe it is a good first step towards generalizing environments for training AI agents.
