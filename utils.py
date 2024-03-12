from typing import Any
import json

__all__ = ["save_json", "load_json"]


def save_json(path: str, state: dict[str, Any]) -> None:
    with open(path, "w") as f:
        json.dump(state, f)


def load_json(path: str) -> dict[str, Any]:
    with open(path, "r") as f:
        state = json.load(f)
    return state
