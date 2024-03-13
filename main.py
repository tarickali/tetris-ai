from typing import Any
import sys
import pygame
import random
from pathlib import Path

from tetris.game import Game, GameAction
from renderer import Renderer
from configs import load_config

FPS = 60
DELAY_TIME = 60


class InputHandler:
    def __init__(self) -> None:
        self.mapping = {
            0: GameAction.RIGHT,
            1: GameAction.LEFT,
            2: GameAction.DOWN,
            3: GameAction.DROP,
            4: GameAction.ROTATE,
            5: GameAction.HOLD,
        }

        # pygame.event.clear()

    def process(self, command: int) -> GameAction:
        action = self.mapping.get(command)
        # pygame.event.clear()
        return action


class Agent:
    def __init__(self) -> None:
        self.rng = random.Random(0)

    def select(self, state: dict[str, Any]) -> int:
        return self.rng.randint(0, 4)


def main():
    pygame.init()
    clock = pygame.time.Clock()

    config = load_config("classic")
    game = Game(config)
    renderer = Renderer(game)

    handler = InputHandler()
    agent = Agent()

    while not game.terminal():
        command = agent.select()
        action = handler.process(command)
        game.transition(action)
        renderer.render()

        clock.tick(FPS)
        pygame.time.wait(DELAY_TIME)

    pygame.quit()
    sys.exit()


def make_observation(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "grid": state["grid"],
        "curr": state["current_tetromino"]["kind"],
        "next": state["next_tetrominos"],
        "held": state["held_tetromino"],
        "info": state["info"],
    }


def test():
    config = load_config("classic")
    game = Game(config)
    agent = Agent()

    NUM_EPISODES = 1
    EPISODE_LENGTH = 10

    game.seed()
    game.start()

    # for _ in range(NUM_EPISODES):
    #     pass

    history = []

    game.render()
    for _ in range(EPISODE_LENGTH):
        state = game.state()
        observation = make_observation(state)
        action = GameAction(agent.select(observation))
        game.transition(action)

        # history.append(
        #     (observation["curr"], observation["next"], observation["held"], action)
        # )

        print(f"Action: {action}")
        print("==================================================")
        game.render()

    # print(history)

    # game.seed(0)
    # game.start()
    # for state, action in history:
    #     pass


def save_and_load():
    config = load_config("classic")
    game = Game(config)

    game.seed(1)
    game.start()

    for _ in range(15):
        game.transition(GameAction(3))

    path = Path.joinpath(Path.cwd(), "checkpoints/state_1.json")
    game.save(path, False)

    print(game.state())
    print(game.bagged_tetrominos)

    game.start()
    path = Path.joinpath(Path.cwd(), "checkpoints/state_1.json")
    game.load(path)

    print(game.state())
    print(game.bagged_tetrominos)


if __name__ == "__main__":
    # main()
    test()
    # save_and_load()
