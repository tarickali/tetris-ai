from __future__ import annotations
from typing import Any
from enum import Enum
import random

from constants import SHAPES
from .grid import Grid
from .tetromino import Tetromino


class GameAction(Enum):
    RIGHT = 0
    LEFT = 1
    DOWN = 2
    DROP = 3
    ROTATE = 4
    HOLD = 5


class Game:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.grid: Grid = None
        self.current_tetromino: Tetromino = None
        self.next_tetrominos: list[int] = []
        self.held_tetromino: int = -1

        self.score: int = 0
        self.lines: int = 0
        self.level: int = 0
        self.can_hold: bool = True

        self._tetromino_bag_size = 7
        self._score_multipliers = [100, 200, 300, 400]

    def start(self) -> None:
        self.grid = Grid(self.width, self.height)
        # Generate bag_size + 1 tetrominos with the last being used for the current tetromino
        self.next_tetrominos = self.generate_tetrominos(self._tetromino_bag_size + 1)
        self.current_tetromino = self.create_tetromino(
            self.next_tetrominos.pop(), (self.width // 2, 0)
        )
        self.held_tetromino = -1

        self.score = 0
        self.lines = 0
        self.level = 1
        self.can_hold = True

    def transition(self, action: GameAction = None) -> None:
        if action is None:
            action = GameAction.DOWN

        tetromino = self.current_tetromino.copy()
        match action:
            case GameAction.RIGHT:
                tetromino.position = (tetromino.position[0] + 1, tetromino.position[1])
                if self.grid.check_valid(tetromino):
                    self.current_tetromino = tetromino
            case GameAction.LEFT:
                tetromino.position = (tetromino.position[0] - 1, tetromino.position[1])
                if self.grid.check_valid(tetromino):
                    self.current_tetromino = tetromino
            case GameAction.DOWN:
                tetromino.position = (tetromino.position[0], tetromino.position[1] + 1)
                if self.grid.check_valid(tetromino):
                    self.current_tetromino = tetromino
                else:
                    tetromino.position = (
                        tetromino.position[0],
                        tetromino.position[1] - 1,
                    )
                    self.place_tetromino(tetromino)
            case GameAction.DROP:
                while self.grid.check_valid(tetromino):
                    tetromino.position = (
                        tetromino.position[0],
                        tetromino.position[1] + 1,
                    )
                tetromino.position = (tetromino.position[0], tetromino.position[1] - 1)
                self.place_tetromino(tetromino)
            case GameAction.ROTATE:
                tetromino.rotate()
                if self.grid.check_valid(tetromino):
                    self.current_tetromino = tetromino
            case GameAction.HOLD:
                if self.can_hold:
                    # If no tetromino is currently being held, use the next tetromino
                    if self.held_tetromino == -1:
                        if len(self.next_tetrominos) == 0:
                            self.next_tetrominos = self.generate_tetrominos(
                                self._tetromino_bag_size
                            )
                        self.held_tetromino = self.next_tetrominos.pop()
                    self.current_tetromino = self.create_tetromino(
                        self.held_tetromino, (self.width // 2, 0)
                    )
                    self.held_tetromino = tetromino.kind
                    self.can_hold = False
        # TODO:
        # - Update level
        # - How does level affect game?

        return self.get_state()

    def terminal(self) -> bool:
        return not self.grid.check_valid(self.current_tetromino)

    def create_tetromino(self, kind: int, position: tuple[int, int]) -> Tetromino:
        return Tetromino(kind, SHAPES[kind - 1], position)

    def place_tetromino(self, tetromino: Tetromino):
        self.grid.place(tetromino)
        lines = self.grid.clear_lines()
        self.lines += lines
        self.score += lines * self._score_multipliers[lines]
        if len(self.next_tetrominos) >= 1:
            self.current_tetromino = self.create_tetromino(
                self.next_tetrominos.pop(), (self.width // 2, 0)
            )
        # Generate new tetrominos if all the next tetrominos have been used
        if len(self.next_tetrominos) == 0:
            self.next_tetrominos = self.generate_tetrominos(self._tetromino_bag_size)

        # Clear hold state if tetromino was placed
        self.can_hold = True

    def get_state(self) -> dict[str, Any]:
        board = self.grid.get_board()

        for x in range(self.current_tetromino.size[0]):
            for y in range(self.current_tetromino.size[1]):
                # Skip white-space of the tetromino
                if self.current_tetromino.shape[y][x] == 0:
                    continue
                # Set the value at the grid positino to the tetromino's kind
                board[self.current_tetromino.position[1] + y][
                    self.current_tetromino.position[0] + x
                ] = self.current_tetromino.kind

        return {
            "board": board,
            "next_tetrominos": self.next_tetrominos,
            "held_tetromino": self.held_tetromino,
            "score": self.score,
            "lines": self.lines,
        }

    @staticmethod
    def generate_tetrominos(k: int) -> int | list[int]:
        tetrominos = random.choices(population=range(1, len(SHAPES) + 1), k=k)
        return tetrominos if k > 1 else tetrominos[0]
