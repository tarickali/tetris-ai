import pygame
import sys
import random

from tetris.constants import GRID_SHAPE, FPS, DELAY_TIME
from tetris.game import Game, GameAction
from renderer import Renderer


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
        action = self.mapping.get(command, GameAction.NONE)
        pygame.event.clear()
        return action


class Agent:
    def select(self) -> int:
        return random.randint(0, 4)


def main():
    pygame.init()
    clock = pygame.time.Clock()

    input_handler = InputHandler()
    renderer = Renderer()
    game = Game(*GRID_SHAPE)
    agent = Agent()

    game.start()
    while not game.terminal():
        command = agent.select()
        action = input_handler.process(command)
        # action = input_handler.process()
        state = game.transition(action)
        renderer.render(state)

        clock.tick(FPS)
        pygame.time.wait(DELAY_TIME)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
