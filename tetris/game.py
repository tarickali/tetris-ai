from __future__ import annotations
from typing import Any
from collections import deque
from enum import Enum
from random import Random
import math

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
        self.width: int = config["width"]
        self.height: int = config["height"]
        self.shapes: dict[str, list[list[list[int]]]] = config["shapes"]
        self.colors: dict[str, list[list[int]]] = config["colors"]
        self.systems: dict[str, Any] = config["systems"]

        self.stoi = {s: i + 1 for i, s in enumerate(sorted(self.shapes))} | {"": 0}
        self.itos = {i + 1: s for i, s in enumerate(sorted(self.shapes))} | {0: ""}

        self.grid: Grid = Grid(self.width, self.height)
        self.current_tetromino: Tetromino = None
        self.next_tetrominos: deque[str] = deque()
        self.held_tetromino: str = ""
        self.info = {}

        self._bag: list[str] = []

        self._scoring_system = {}
        self._transition_system = {}
        self._generation_system = {}
        self.setup_systems()

        self.rng = Random()

    def setup_systems(self) -> None:
        # Setup the scoring system
        # NOTE: if the maximum number of lines in a game is larger than the length
        # of scoring_system, then score adjustments will use the largest value.
        scoring = self.systems["scoring"]
        if scoring["type"] == "lines":
            self._scoring_system["scores"] = [int(line) for line in scoring["lines"]]
        elif scoring["type"] == "multipliers":
            self._scoring_system["scores"] = [
                int(scoring["base"] * multiplier)
                for multiplier in scoring["multipliers"]
            ]

        # Setup the transition system
        transition = self.systems["transition"]
        if transition.get("enforce-down") and transition["enforce-down"]["active"]:
            actions = set()
            if transition["enforce-down"]["actions"] == "all":
                actions = {action for action in GameAction}
            else:
                for action in transition["enforce-down"]["actions"]:
                    match action:
                        case "left":
                            action = GameAction.LEFT
                        case "right":
                            action = GameAction.RIGHT
                        case "down":
                            action = GameAction.DOWN
                        case "drop":
                            action = GameAction.DROP
                        case "rotate":
                            action = GameAction.ROTATE
                        case "hold":
                            action = GameAction.HOLD
                        case _:
                            pass
                    actions.add(action)
            self._transition_system["enforce-down"] = {
                "active": True,
                "actions": actions,
            }
        else:
            self._transition_system["enforce-down"] = {"active": False}

        # Setup the generation system
        generation = self.systems["generation"]
        self._generation_system["bag-size"] = generation["bag-size"]
        self._generation_system["next-size"] = generation["next-size"]
        self._generation_system["distribution"] = [0] * len(self.shapes)
        if generation.get("distribution"):
            if generation["distribution"]["type"] == "uniform":
                self._generation_system["distribution"] = [1 / len(self.shapes)] * len(
                    self.shapes
                )
            if generation["distribution"]["type"] == "custom":
                for kind, weight in generation["distribution"]["weights"].items():
                    self._generation_system["distribution"][
                        self.stoi[kind] - 1
                    ] = weight

    def start(self) -> None:
        self.grid.empty()
        # Generate bag_size + 1 tetrominos with the last being used for the current tetromino
        # self._bag = self.generate_tetrominos(self._generation_system["bag-size"])
        self.next_tetrominos.extend(
            self.generate_tetrominos(self._generation_system["bag-size"] + 1)
        )
        self.current_tetromino = self.create_tetromino(
            self.next_tetrominos.popleft(), (self.width // 2, 0)
        )
        self.held_tetromino = ""

        self.info = {"score": 0, "lines": 0, "level": 1, "time": 0, "can_hold": True}

    def transition(self, action: GameAction = None) -> None:
        tetromino = self.current_tetromino.copy()
        placed = False
        match action:
            case GameAction.RIGHT:
                valid = self.move_tetromino((1, 0))
            case GameAction.LEFT:
                valid = self.move_tetromino((-1, 0))
            case GameAction.DOWN:
                valid = self.move_tetromino((0, 1))
                if not valid:
                    self.place()
                    placed = True
            case GameAction.DROP:
                while self.move_tetromino((0, 1)):
                    pass
                self.place()
                placed = True
            case GameAction.ROTATE:
                tetromino = self.current_tetromino.copy()
                tetromino.rotate()
                if self.grid.check_valid(tetromino):
                    self.current_tetromino = tetromino
            case GameAction.HOLD:
                if self.info["can_hold"]:
                    # If no tetromino is currently being held, use the next tetromino
                    if not self.held_tetromino:
                        if len(self.next_tetrominos) == 0:
                            self.next_tetrominos.extend(
                                self.generate_tetrominos(
                                    self._generation_system["bag-size"]
                                )
                            )
                        self.held_tetromino = self.next_tetrominos.popleft()
                    self.current_tetromino = self.create_tetromino(
                        self.held_tetromino, (self.width // 2, 0)
                    )
                    self.held_tetromino = tetromino.kind
                    self.info["can_hold"] = False

        # Apply additional functionality according to transition system
        # Apply enforce-down
        if (
            not placed  # Rule: enforce-down only applies if the current tetromino was not placed
            and self._transition_system["enforce-down"]["active"]
            and action in self._transition_system["enforce-down"]["actions"]
        ):
            valid = self.move_tetromino((0, 1))
            if not valid:
                self.place()
                placed = True

        # Increment discrete time counter every transition
        self.info["time"] += 1

        return self.state()

    def terminal(self) -> bool:
        return not self.grid.check_valid(self.current_tetromino)

    def generate_tetrominos(self, k: int) -> str | list[str]:
        # Calculate the gap between number of next tetrominos and fixed minimum
        # gap = max(len(self.next_tetrominos), self._generation_system["next-size"])
        # Generate
        # k = math.ceil(self._generation_system["bag-size"] / gap)

        weights = self._generation_system["distribution"]
        tetrominos = self.rng.choices(
            population=sorted(self.shapes), weights=weights, k=k
        )
        return tetrominos if k > 1 else tetrominos[0]

    def create_tetromino(
        self, kind: str, position: tuple[int, int], rotation: int = 0
    ) -> Tetromino:
        return Tetromino(kind, position, rotation, self.stoi[kind], self.shapes[kind])

    def move_tetromino(self, direction: tuple[int, int]) -> bool:
        tetromino = self.current_tetromino.copy()
        tetromino.position = (
            tetromino.position[0] + direction[0],
            tetromino.position[1] + direction[1],
        )

        if self.grid.check_valid(tetromino):
            self.current_tetromino = tetromino
            return True
        else:
            return False

    def place(self, tetromino: Tetromino = None) -> None:
        if tetromino is None:
            tetromino = self.current_tetromino
        self.grid.place(tetromino)

        lines = self.grid.clear_lines()
        self.info["lines"] += lines

        if lines != 0:
            lines = min(lines, len(self._scoring_system["scores"]))
            self.info["score"] += self._scoring_system["scores"][lines]

        if len(self.next_tetrominos) >= 1:
            self.current_tetromino = self.create_tetromino(
                self.next_tetrominos.popleft(), (self.width // 2, 0)
            )
        # Generate new tetrominos if all the next tetrominos have been used
        if len(self.next_tetrominos) == 0:
            self.next_tetrominos.extend(
                self.generate_tetrominos(self._generation_system["bag-size"])
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

    def seed(self, root: int = None) -> None:
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
