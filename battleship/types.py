from __future__ import annotations

from enum import Enum
from typing import Tuple

Coord = Tuple[int, int]  # (x, y) where 0<=x,y<size


class ShotResult(str, Enum):
    MISS = "miss"
    HIT = "hit"
    SUNK = "sunk"
    ALREADY_SHOT = "already_shot"


class CellState(str, Enum):
    WATER = "water"
    SHIP = "ship"
    HIT = "hit"
    MISS = "miss"
    SUNK = "sunk"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
