import numpy as np

__all__ = ["calculate_bumpiness", "calculate_height", "calculate_holes"]


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
