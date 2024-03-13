from __future__ import annotations
from typing import Any
from collections import deque
from enum import Enum
from random import Random

import numpy as np

from .grid import Grid
from .tetromino import Tetromino
from utils import save_json, load_json


class GameAction(Enum):
    RIGHT = 0
    LEFT = 1
    DOWN = 2
    DROP = 3
    ROTATE = 4
    HOLD = 5


class Game:
    def __init__(self, config: dict[str, Any]) -> None:
        self.width = config["width"]
        self.height = config["height"]
        self.shapes = config["shapes"]
        self.colors = config["colors"]

        self.stoi = {s: i + 1 for i, s in enumerate(sorted(self.shapes))} | {"": 0}
        self.itos = {i + 1: s for i, s in enumerate(sorted(self.shapes))} | {0: ""}

        self.grid: Grid = Grid(self.width, self.height)
        self.current_tetromino: Tetromino = None
        self.next_tetrominos: deque[str] = deque([])
        self.held_tetromino: str = ""

        self.info = {}

        self._tetromino_bag_size = 7
        self._score_multipliers = [100, 200, 300, 400]

        self.rng = Random()

    def start(self) -> None:
        self.grid.empty()
        # Generate bag_size + 1 tetrominos with the last being used for the current tetromino
        self.next_tetrominos.extend(
            self.generate_tetrominos(self._tetromino_bag_size + 1)
        )
        self.current_tetromino = self.create_tetromino(
            self.next_tetrominos.popleft(), (self.width // 2, 0)
        )
        self.held_tetromino = ""

        self.info = {"score": 0, "lines": 0, "level": 1, "time": 0, "can_hold": True}

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
                    self.place(tetromino)
            case GameAction.DROP:
                while self.grid.check_valid(tetromino):
                    tetromino.position = (
                        tetromino.position[0],
                        tetromino.position[1] + 1,
                    )
                tetromino.position = (tetromino.position[0], tetromino.position[1] - 1)
                self.place(tetromino)
            case GameAction.ROTATE:
                tetromino.rotate()
                if self.grid.check_valid(tetromino):
                    self.current_tetromino = tetromino
            case GameAction.HOLD:
                if self.info["can_hold"]:
                    # If no tetromino is currently being held, use the next tetromino
                    if not self.held_tetromino:
                        if len(self.next_tetrominos) == 0:
                            self.next_tetrominos.extend(
                                self.generate_tetrominos(self._tetromino_bag_size)
                            )
                        self.held_tetromino = self.next_tetrominos.popleft()
                    self.current_tetromino = self.create_tetromino(
                        self.held_tetromino, (self.width // 2, 0)
                    )
                    self.held_tetromino = tetromino.kind
                    self.info["can_hold"] = False
        # TODO:
        # - Update level
        # - How does level affect game?

        # Increment discrete time counter every transition
        self.info["time"] += 1

        return self.state()

    def terminal(self) -> bool:
        return not self.grid.check_valid(self.current_tetromino)

    def modify(self, info: dict[str, Any]) -> None:
        """Change the info dictionary of the game.

        Parameters
        ----------
        info : dict[str, Any]
            The dictionary to modify the game's internal info dictionary with

        """

        self.info |= info

    def generate_tetrominos(self, k: int) -> str | list[str]:
        tetrominos = self.rng.choices(population=list(self.shapes), k=k)
        return tetrominos if k > 1 else tetrominos[0]

    def create_tetromino(
        self, kind: str, position: tuple[int, int], rotation: int = 0
    ) -> Tetromino:
        return Tetromino(kind, position, rotation, self.stoi[kind], self.shapes[kind])

    def place(self, tetromino: Tetromino):
        self.grid.place(tetromino)
        lines = self.grid.clear_lines()
        self.info["lines"] += lines
        self.info["score"] += lines * self._score_multipliers[lines]
        if len(self.next_tetrominos) >= 1:
            self.current_tetromino = self.create_tetromino(
                self.next_tetrominos.popleft(), (self.width // 2, 0)
            )
        # Generate new tetrominos if all the next tetrominos have been used
        if len(self.next_tetrominos) == 0:
            self.next_tetrominos.extend(
                self.generate_tetrominos(self._tetromino_bag_size)
            )

        # Clear hold state if tetromino was placed
        self.info["can_hold"] = True

    def render(self) -> None:
        grid = self.grid.copy()
        grid.place(self.current_tetromino)

        print(
            f"curr: {self.current_tetromino.kind} | next: {self.next_tetrominos[0]} | held: {self.held_tetromino} || info: {self.info}"
        )
        grid.render()

    def seed(self, root: int) -> None:
        self.rng.seed(root)

    def load(self, path: str) -> None:
        state = load_json(path)

        self.grid.load(state["grid"])
        self.current_tetromino = self.create_tetromino(**state["current_tetromino"])
        self.next_tetrominos = deque([self.itos[s] for s in state["next_tetrominos"]])
        self.held_tetromino = self.itos[state["held_tetromino"]]
        self.info = state["info"]
        if state.get("rng"):
            self.rng.setstate(
                tuple(
                    tuple(rinfo) if isinstance(rinfo, list) else rinfo
                    for rinfo in state["rng"]
                )
            )

    def save(self, path: str, include_rng: bool = True) -> None:
        # Change numpy arrays to list before saving
        state = self.state()
        state["grid"] = state["grid"].tolist()
        state["next_tetrominos"] = state["next_tetrominos"].tolist()

        if include_rng:
            state["rng"] = self.rng.getstate()

        save_json(path, state)

    def state(self) -> dict[str, Any]:
        grid = self.grid.copy()
        grid.place(self.current_tetromino)

        return {
            "grid": grid.state(),
            "current_tetromino": self.current_tetromino.state(),
            "next_tetrominos": np.array([self.stoi[s] for s in self.next_tetrominos]),
            "held_tetromino": self.stoi[self.held_tetromino],
            "info": self.info,
        }
