from typing import Any
import os
import json

__all__ = ["load_configs"]


def load_config(name: str) -> dict[str, Any]:
    path = os.path.dirname(__file__) + "/configs.json"
    with open(path, "r") as file:
        configs = json.load(file)

    return configs[name.lower()]
