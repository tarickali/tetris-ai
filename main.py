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
    def select(self, state: dict[str, Any]) -> int:
        return random.randint(0, 4)


def main():
    pygame.init()
    clock = pygame.time.Clock()

    config = load_config("classic")
    game = Game(config)
    renderer = Renderer(game)

    handler = InputHandler()
    agent = Agent()

    game.seed(1)
    game.start()

    for _ in range(10):
        game.transition(GameAction(3))

    path = Path.joinpath(Path.cwd(), "checkpoints/state_1.json")
    game.save(path, False)
    # game.load(path)

    # while not game.terminal():
    while False:
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
        "next": state["next_tetrominos"][0],
        "held": state["held_tetromino"],
        "score": state["score"],
    }


def test():
    config = load_config("classic")
    game = Game(config)
    agent = Agent()

    NUM_EPISODES = 1
    EPISODE_LENGTH = 10

    game.seed(0)
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

        history.append((observation, action))

        print(f"Action: {action}")
        print("==================================================")
        game.render()

    print(history)

    game.seed(0)
    game.start()
    for state, action in history:
        pass


def save_and_load():
    config = load_config("classic")
    game = Game(config)
    path = Path.joinpath(Path.cwd(), "checkpoints/state_1.json")
    game.load(path)

    print(game.state())

    # while not game.terminal():
    #     pass


if __name__ == "__main__":
    # main()
    test()
    # save_and_load()
