from __future__ import annotations
from typing import Any
from collections import deque
from enum import Enum
from random import Random

from utils.file_utils import save_json, load_json, load_config
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
    def __init__(self, config: str | dict[str, Any]) -> None:
        # Load config is given config filename
        if isinstance(config, str):
            config = load_config(config)

        # Bind grid, tetrominos, and systems configs
        self.grid: Grid = Grid(config["grid"])
        self.tetrominos: dict[str, list[list[list[int]]]] = config["tetrominos"]
        self.systems: dict[str, Any] = config["systems"]

        # Mappings between tetromino names (kind) and values (num) [used for render]
        self.stoi = {s: i + 1 for i, s in enumerate(sorted(self.tetrominos))} | {"": 0}
        self.itos = {i + 1: s for i, s in enumerate(sorted(self.tetrominos))} | {0: ""}

        # Declare the internal state
        self.current_tetromino: Tetromino = None
        self.next_tetrominos: deque[str] = deque()
        self.held_tetromino: str = ""
        self.info = {}
        # Additional managed state to ease tetromino generation
        self.bagged_tetrominos: list[str] = []

        # Setup systems based on config
        self._scoring_system = {}
        self._transition_system = {}
        self._generation_system = {}
        self._setup_systems()

        # Setup the random number generator for the game
        self.rng = Random()

    def start(self) -> dict[str, Any]:
        # Ensure that the grid is empty at the start
        self.grid.empty()

        # Populate next and bagged tetrominos based on generation system
        self._populate_tetrominos()
        # Create the current tetromino from the next pile and place at grid center
        self.current_tetromino = self._create_tetromino(
            self.next_tetrominos.popleft(), (self.grid.width // 2, 0)
        )
        # Repopulate the next and bagged tetrominos, if necessary
        self._populate_tetrominos()
        # Initialize held tetromino to nothing
        self.held_tetromino = ""

        # Initialize the starting game info, split into main and extra
        self.info = {
            "main": {
                "score": 0,
                "lines": 0,
                "time": 0,
                "can_hold": True,
            },
            "extra": {
                "last_valid": True,
                "total_valid": 0,
                "last_placed": False,
                "total_placed": 0,
                "score_diff": 0,
            },
        }

        return self.state

    def transition(self, action: int = None) -> dict[str, Any]:
        # Convert action input into a GameAction
        # If no action is given, the default is GameAction.DOWN
        action = GameAction(action) if action is not None else GameAction.DOWN

        # Initialize objects needed for state update
        lines = 0
        valid = False
        placed = False

        # Apply the appropriate transition based on the action
        match action:
            case GameAction.RIGHT:
                valid = self._move_tetromino((1, 0))
            case GameAction.LEFT:
                valid = self._move_tetromino((-1, 0))
            case GameAction.DOWN:
                valid = self._move_tetromino((0, 1))
                if not valid:
                    lines = self._place()
                    placed = True
            case GameAction.DROP:
                while self._move_tetromino((0, 1)):
                    pass
                lines = self._place()
                valid = True
                placed = True
            case GameAction.ROTATE:
                tetromino = self.current_tetromino.copy()
                tetromino.rotate()
                valid = self.grid.check_valid(tetromino)
                if valid:
                    self.current_tetromino = tetromino
            case GameAction.HOLD:
                # The HOLD action can be applied only if it is valid in the current state
                if self.info["main"]["can_hold"]:
                    # Populate the held tetromino with the next tetromino if necessary
                    # NOTE: this should only happens once, when the first HOLD is requested
                    if not self.held_tetromino:
                        self.held_tetromino = self.next_tetrominos.popleft()
                        self._populate_tetrominos()

                    # Swap the current and held tetromino
                    current_kind = self.current_tetromino.kind
                    self.current_tetromino = self._create_tetromino(
                        self.held_tetromino, (self.grid.width // 2, 0)
                    )
                    self.held_tetromino = current_kind

                    # Set HOLD action to be invalid
                    self.info["main"]["can_hold"] = False

                    valid = True

        # Apply transition system's enforce-down
        if (
            not placed  # Rule: enforce-down only applies if the current tetromino was not placed
            and self._transition_system["enforce-down"]["active"]
            and action in self._transition_system["enforce-down"]["actions"]
        ):
            valid = self._move_tetromino((0, 1))
            if not valid:
                lines = self._place()
                placed = True

        # Update info
        if placed:
            self.current_tetromino = self._create_tetromino(
                self.next_tetrominos.popleft(), (self.grid.width // 2, 0)
            )
            self._populate_tetrominos()

            # Clear hold state if tetromino was placed
            self.info["main"]["can_hold"] = True

        # Increment discrete time counter every transition
        prev_score = self.info["main"]["score"]

        self.info["main"]["time"] += 1
        self.info["main"]["lines"] += lines
        lines = min(lines, len(self._scoring_system["scores"]))
        self.info["main"]["score"] += self._scoring_system["scores"][lines]

        self.info["extra"]["last_valid"] = valid
        self.info["extra"]["total_valid"] += valid
        self.info["extra"]["last_placed"] = placed
        self.info["extra"]["total_placed"] += placed
        self.info["extra"]["score_diff"] = self.info["main"]["score"] - prev_score

        return self.state

    def terminal(self) -> bool:
        # The game is terminal if the current tetromino is not valid
        # NOTE: this method should only be called after a transition,
        # it does not make sense otherwise.
        return not self.grid.check_valid(self.current_tetromino)

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
        self.current_tetromino = self._create_tetromino(**state["current_tetromino"])
        self.next_tetrominos = deque(state["next_tetrominos"])
        self.held_tetromino = state["held_tetromino"]
        self.info = state["info"]

        self.bagged_tetrominos = state["bagged_tetrominos"]

        if state.get("rng"):
            self.rng.setstate(
                tuple(
                    tuple(rinfo) if isinstance(rinfo, list) else rinfo
                    for rinfo in state["rng"]
                )
            )

    def save(self, path: str, include_rng: bool = True) -> None:
        # Change numpy arrays to list before saving
        state = {
            "grid": {"board": self.grid.state["board"].tolist()},
            "current_tetromino": self.current_tetromino.state,
            "next_tetrominos": list(self.next_tetrominos),
            "held_tetromino": self.held_tetromino,
            "info": self.info,
            "bagged_tetrominos": self.bagged_tetrominos,
        }

        if include_rng:
            state["rng"] = self.rng.getstate()

        save_json(path, state)

    @property
    def state(self) -> dict[str, Any]:
        return {
            "grid": self.grid.state,
            "current_tetromino": self.current_tetromino.state,
            "next_tetrominos": list(self.next_tetrominos),
            "held_tetromino": self.held_tetromino,
            "info": self.info,
        }

    ############################################################################
    # Private Methods
    ############################################################################
    def _setup_systems(self) -> None:
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
        self._generation_system["distribution"] = [0] * len(self.tetrominos)
        if generation.get("distribution"):
            if generation["distribution"]["type"] == "uniform":
                self._generation_system["distribution"] = [
                    1 / len(self.tetrominos)
                ] * len(self.tetrominos)
            if generation["distribution"]["type"] == "custom":
                for kind, weight in generation["distribution"]["weights"].items():
                    self._generation_system["distribution"][
                        self.stoi[kind] - 1
                    ] = weight

    def _generate_tetrominos(self) -> str | list[str]:
        # Get the amount of tetrominos to generate and their distributions from the generation system
        k = self._generation_system["bag-size"]
        weights = self._generation_system["distribution"]

        # Get a list of choices of the tetromino kinds
        # NOTE: we must sort the tetrominos since the distribution is a list, not a dictionary
        tetrominos = self.rng.choices(
            population=sorted(self.tetrominos), weights=weights, k=k
        )

        # Return a single or a list of strings
        return tetrominos if k > 1 else tetrominos[0]

    def _create_tetromino(
        self, kind: str, position: tuple[int, int], rotation: int = 0
    ) -> Tetromino:
        return Tetromino(
            kind, position, rotation, self.stoi[kind], self.tetrominos[kind]
        )

    def _populate_tetrominos(self) -> None:
        # Populate next tetrominos only when they are less than the required size
        if len(self.next_tetrominos) < self._generation_system["next-size"]:
            # Calculate the gap between the expected and actual amounts of the next tetrominos
            gap = self._generation_system["next-size"] - len(self.next_tetrominos)
            # If the bag does not have enough tetrominos, then generate and extend according to generation system
            if gap > len(self.bagged_tetrominos):
                self.bagged_tetrominos.extend(self._generate_tetrominos())
            # Populate the next tetrominos from the bag until the gap is filled
            for _ in range(gap):
                self.next_tetrominos.extend(self.bagged_tetrominos.pop())

    def _move_tetromino(self, direction: tuple[int, int]) -> bool:
        # Make a temporary copy of the current tetromino to validate the move
        tetromino = self.current_tetromino.copy()
        tetromino.position = (
            tetromino.position[0] + direction[0],
            tetromino.position[1] + direction[1],
        )

        # Check if the move is valid in the grid, and modify the current tetromino if it is
        if self.grid.check_valid(tetromino):
            self.current_tetromino = tetromino
            return True
        else:
            return False

    def _place(self, tetromino: Tetromino = None) -> int:
        # If no tetromino is given, set it to the current tetromino
        if tetromino is None:
            tetromino = self.current_tetromino

        # Place the tetromino onto the grid
        self.grid.place(tetromino)

        # Clear the filled lines of the grid
        lines = self.grid.clear_lines()

        return lines
