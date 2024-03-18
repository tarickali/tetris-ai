from typing import Any
import os
import json

__all__ = ["save_json", "load_json", "load_config"]

ROOT_PATH = os.path.dirname(__file__) + "/.."


def save_json(path: str, state: dict[str, Any]) -> None:
    with open(path, "w") as f:
        json.dump(state, f)


def load_json(path: str) -> dict[str, Any]:
    with open(path, "r") as f:
        state = json.load(f)
    return state


def load_config(filename: str) -> dict[str, Any]:
    path = ROOT_PATH + f"/configs/{filename}.json"
    return load_json(path)
