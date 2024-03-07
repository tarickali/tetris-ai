from __future__ import annotations
import copy


class Tetromino:
    def __init__(
        self, kind: int, shapes: list[list[list[int]]], position: tuple[int, int]
    ) -> None:
        self.kind = kind
        self.shapes = shapes
        self.rotation = 0
        self.position = position

    def rotate(self) -> None:
        self.rotation = (self.rotation + 1) % len(self.shapes)

    def copy(self) -> Tetromino:
        return copy.deepcopy(self)

    @property
    def shape(self) -> list[list[int]]:
        return self.shapes[self.rotation]

    @property
    def size(self) -> tuple[int, int]:
        return (len(self.shape[0]), len(self.shape))
