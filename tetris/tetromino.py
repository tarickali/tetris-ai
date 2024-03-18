from __future__ import annotations
from typing import Any
import copy


class Tetromino:
    def __init__(
        self,
        kind: str,
        position: tuple[int, int],
        rotation: int,
        num: int,
        shapes: list[list[list[int]]],
    ) -> None:
        self.kind = kind  # used for indexing into game.shapes
        self.position = position  # for placement on grid (top-left)
        self.rotation = rotation  # index into shapes
        self.num = num  # used for intger grid
        self.shapes = shapes  # references index in game.shapes

    def rotate(self) -> None:
        self.rotation = (self.rotation + 1) % len(self.shapes)

    def copy(self) -> Tetromino:
        return copy.deepcopy(self)

    @property
    def state(self) -> dict[str, Any]:
        return {"kind": self.kind, "position": self.position, "rotation": self.rotation}

    @property
    def shape(self) -> list[list[int]]:
        return self.shapes[self.rotation]

    @property
    def size(self) -> tuple[int, int]:
        return (len(self.shape[0]), len(self.shape))
