from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .ship import Ship
from .types import CellState, Coord, ShotResult


def iter_neighbors(coord: Coord, size: int, *, include_diagonals: bool = True) -> Iterable[Coord]:
    x, y = coord
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            if not include_diagonals and abs(dx) + abs(dy) != 1:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size:
                yield (nx, ny)


@dataclass
class Board:
    size: int = 10
    ships: List[Ship] = field(default_factory=list)
    _occupied: Set[Coord] = field(default_factory=set)
    _shots: Dict[Coord, ShotResult] = field(default_factory=dict)

    def reset(self) -> None:
        self.ships.clear()
        self._occupied.clear()
        self._shots.clear()

    @property
    def shots(self) -> Dict[Coord, ShotResult]:
        return self._shots

    def ship_at(self, coord: Coord) -> Optional[Ship]:
        for ship in self.ships:
            if ship.contains(coord):
                return ship
        return None

    def in_bounds(self, coord: Coord) -> bool:
        x, y = coord
        return 0 <= x < self.size and 0 <= y < self.size

    def cells_for_ship(self, start: Coord, length: int, horizontal: bool) -> Tuple[Coord, ...]:
        x0, y0 = start
        if horizontal:
            return tuple((x0 + i, y0) for i in range(length))
        return tuple((x0, y0 + i) for i in range(length))

    def can_place_cells(self, cells: Sequence[Coord]) -> bool:
        for c in cells:
            if not self.in_bounds(c):
                return False
            if c in self._occupied:
                return False
            for n in iter_neighbors(c, self.size, include_diagonals=True):
                if n in self._occupied:
                    return False
        return True

    def place_ship(self, start: Coord, length: int, horizontal: bool) -> bool:
        cells = self.cells_for_ship(start, length, horizontal)
        if not self.can_place_cells(cells):
            return False

        ship = Ship(length=length, cells=cells)
        self.ships.append(ship)
        self._occupied.update(cells)
        return True

    def pop_last_ship(self) -> Optional[Ship]:
        if not self.ships:
            return None
        ship = self.ships.pop()
        for c in ship.cells:
            self._occupied.discard(c)
        for c in ship.cells:
            self._shots.pop(c, None)
        return ship

    def place_ships_randomly(self, ship_lengths: Sequence[int], *, rng: Optional[Random] = None) -> None:
        rng = rng or Random()
        self.reset()

        for length in ship_lengths:
            placed = False
            for _ in range(10_000):
                horizontal = rng.choice([True, False])
                x_max = self.size - (length if horizontal else 1)
                y_max = self.size - (1 if horizontal else length)
                x = rng.randint(0, x_max)
                y = rng.randint(0, y_max)
                if self.place_ship((x, y), length, horizontal):
                    placed = True
                    break
            if not placed:
                raise RuntimeError("Failed to place ships randomly; try increasing attempts")

    def receive_shot(self, coord: Coord) -> tuple[ShotResult, Optional[Ship]]:
        if not self.in_bounds(coord):
            raise ValueError("Shot out of bounds")

        if coord in self._shots:
            return ShotResult.ALREADY_SHOT, None

        if coord in self._occupied:
            ship = self.ship_at(coord)
            if ship is None:
                raise RuntimeError("Board is inconsistent: occupied cell without ship")
            ship.register_hit(coord)
            self._shots[coord] = ShotResult.HIT
            if ship.sunk:
                return ShotResult.SUNK, ship
            return ShotResult.HIT, ship

        self._shots[coord] = ShotResult.MISS
        return ShotResult.MISS, None

    def all_ships_sunk(self) -> bool:
        return all(s.sunk for s in self.ships) and len(self.ships) > 0

    def cell_state(self, coord: Coord, *, reveal_ships: bool) -> CellState:
        if coord in self._shots:
            if self._shots[coord] == ShotResult.MISS:
                return CellState.MISS
            ship = self.ship_at(coord)
            if ship and ship.sunk:
                return CellState.SUNK
            return CellState.HIT

        if reveal_ships and coord in self._occupied:
            return CellState.SHIP

        return CellState.WATER

    def available_shots(self) -> List[Coord]:
        return [(x, y) for y in range(self.size) for x in range(self.size) if (x, y) not in self._shots]
