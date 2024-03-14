from typing import Any
import random

from tetris.game import Game, GameAction
from utils.game_utils import calculate_bumpiness, calculate_height, calculate_holes
from configs import load_config


class Agent:
    def __init__(self) -> None:
        self.rng = random.Random(0)

    def select(self) -> int:
        return self.rng.randint(2, 3)


def make_observation(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "grid": state["grid"],
        "curr": state["current_tetromino"]["kind"],
        "next": state["next_tetrominos"],
        "held": state["held_tetromino"],
        "info": state["info"],
    }


def test_1():
    EPISODE_LENGTH = 10

    config = load_config("classic")
    game = Game(config)
    game.seed(0)
    game.start()

    agent = Agent()

    # game.render()
    for _ in range(EPISODE_LENGTH):
        game.render()
        state = game.state()
        action = GameAction(agent.select())
        print(f"bumpiness: {calculate_bumpiness(state['grid']['board'])}")
        print(f"holes: {calculate_holes(state['grid']['board'])}")
        print(f"height: {calculate_height(state['grid']['board'])}")
        print("==================================================")
        print(f"Action: {action}")
        print("==================================================")
        game.transition(action)


if __name__ == "__main__":
    test_1()
