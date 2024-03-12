import numpy as np
from .tetromino import Tetromino


class Grid:
    def __init__(self, width: int, height: int) -> None:
        self.board = np.zeros((height, width), dtype=int)

    def check_inbounds(self, tetromino: Tetromino) -> bool:
        for x in range(tetromino.size[0]):
            for y in range(tetromino.size[1]):
                if tetromino.shape[y][x] == 0:
                    continue
                # Check if the position is within the board
                if not (
                    0 <= tetromino.position[0] + x < self.width
                    and 0 <= tetromino.position[1] + y < self.height
                ):
                    return False
        return True

    def check_overlap(self, tetromino: Tetromino) -> bool:
        for x in range(tetromino.size[0]):
            for y in range(tetromino.size[1]):
                if tetromino.shape[y][x] == 0:
                    continue
                if (
                    self.board[tetromino.position[1] + y][tetromino.position[0] + x]
                    != 0
                ):
                    return True
        return False

    def check_valid(self, tetromino: Tetromino) -> bool:
        return self.check_inbounds(tetromino) and not self.check_overlap(tetromino)

    def place(self, tetromino: Tetromino) -> None:
        for x in range(tetromino.size[0]):
            for y in range(tetromino.size[1]):
                if tetromino.shape[y][x] == 0:
                    continue
                self.board[tetromino.position[1] + y][
                    tetromino.position[0] + x
                ] = tetromino.num

    def clear_lines(self) -> int:
        lines = 0
        for row in range(self.height):
            if all(col != 0 for col in self.board[row]):
                for r in range(row, 0, -1):
                    self.board[r] = self.board[r - 1]
                self.board[0] = [0] * self.width
                lines += 1
        return lines

    def load(self, state: list[list[int]]) -> None:
        self.board = np.array(state)

    def state(self) -> np.ndarray:
        return self.board.copy()

    @property
    def width(self) -> int:
        return self.board.shape[1]

    @property
    def height(self) -> int:
        return self.board.shape[0]
