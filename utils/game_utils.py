import numpy as np

__all__ = [
    "put_shape_in_array",
    "calculate_bumpiness",
    "calculate_height",
    "calculate_holes",
]


def put_shape_in_array(
    board: np.ndarray,
    shape: list[list[int]],
    position: tuple[int, int],
    num: int,
    inplace: bool = True,
) -> np.ndarray:
    if not inplace:
        board = board.copy()

    for y in range(len(shape)):
        for x in range(len(shape[y])):
            # Skip white-space of the block
            if shape[y][x] == 0:
                continue
            if not (
                0 <= position[1] + y < board.shape[1]
                and 0 <= position[0] + x < board.shape[0]
            ):
                raise KeyError(f"Index out of range. Cannot put block in array.")
            # Set the value at the grid positino to num
            board[position[1] + y][position[0] + x] = num

    return board


def calculate_bumpiness(board: np.ndarray) -> tuple[int, int]:
    heights = [0] * board.shape[1]
    for x in range(board.shape[1]):
        for y in range(board.shape[0]):
            if board[y][x] != 0:
                heights[x] = board.shape[0] - y
                break

    sum_bumpiness = 0
    max_bumpiness = 0
    for i in range(len(heights) - 1):
        bumpiness = abs(heights[i + 1] - heights[i])
        sum_bumpiness += bumpiness
        max_bumpiness = max(max_bumpiness, bumpiness)

    return sum_bumpiness, max_bumpiness


def calculate_height(board: np.ndarray) -> tuple[int, int, int]:
    sum_height = 0
    max_height = 0
    min_height = board.shape[0] + 1

    for x in range(board.shape[1]):
        for y in range(board.shape[0]):
            if board[y][x] != 0:
                height = board.shape[0] - y
                sum_height += height
                max_height = max(max_height, height)
                min_height = min(min_height, height)
                break

    # If the board is all 0, then min_height should be 0
    if min_height == board.shape[0] + 1:
        min_height = 0

    return sum_height, max_height, min_height


def calculate_holes(board: np.ndarray) -> int:
    holes = 0
    for x in range(board.shape[1]):
        ceiling = -1
        for y in range(board.shape[0]):
            if board[y][x] != 0:
                ceiling = y
            if board[y][x] == 0 and ceiling != -1:
                holes += y - ceiling
                ceiling = y
    return holes
