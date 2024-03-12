import sys
import pygame
import random

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

        pygame.event.clear()

    def process(self, command: int) -> GameAction:
        action = self.mapping.get(command)
        pygame.event.clear()
        return action


class Agent:
    def select(self) -> int:
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

    # path = Path.joinpath(Path.cwd(), "checkpoints/state_1.json")
    # game.save(path, False)
    # game.load(path)

    while not game.terminal():
        command = agent.select()
        action = handler.process(command)
        game.transition(action)
        renderer.render()

        clock.tick(FPS)
        pygame.time.wait(DELAY_TIME)

    pygame.quit()
    sys.exit()


def test():
    config = load_config("classic")
    game = Game(config)

    game.seed(0)
    game.start()
    game.render()

    # while not game.terminal():
    #     pass


if __name__ == "__main__":
    test()
