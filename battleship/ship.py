from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set, Tuple

from .types import Coord


@dataclass
class Ship:
    length: int
    cells: Tuple[Coord, ...]
    hits: Set[Coord] = field(default_factory=set)

    def register_hit(self, coord: Coord) -> None:
        if coord in self.cells:
            self.hits.add(coord)

    @property
    def sunk(self) -> bool:
        return len(self.hits) >= self.length

    def contains(self, coord: Coord) -> bool:
        return coord in self.cells
