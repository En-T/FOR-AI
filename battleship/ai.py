from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from typing import List, Optional, Sequence, Set

from .board import iter_neighbors
from .types import Coord, Difficulty, ShotResult


@dataclass
class BattleshipAI:
    difficulty: Difficulty
    board_size: int = 10
    rng: Random = field(default_factory=Random)

    _shots: Set[Coord] = field(default_factory=set)
    _known_empty: Set[Coord] = field(default_factory=set)
    _target_hits: List[Coord] = field(default_factory=list)

    def reset(self) -> None:
        self._shots.clear()
        self._known_empty.clear()
        self._target_hits.clear()

    def _in_bounds(self, coord: Coord) -> bool:
        x, y = coord
        return 0 <= x < self.board_size and 0 <= y < self.board_size

    def _available(self, coord: Coord) -> bool:
        return coord not in self._shots and coord not in self._known_empty

    def choose_shot(self) -> Coord:
        if self.difficulty == Difficulty.EASY:
            return self._choose_random_shot()
        return self._choose_medium_shot()

    def _choose_random_shot(self) -> Coord:
        candidates = [
            (x, y)
            for y in range(self.board_size)
            for x in range(self.board_size)
            if (x, y) not in self._shots
        ]
        if not candidates:
            raise RuntimeError("AI has no available shots")
        return self.rng.choice(candidates)

    def _choose_medium_shot(self) -> Coord:
        if self._target_hits:
            shot = self._choose_target_mode_shot()
            if shot is not None:
                return shot
            self._target_hits.clear()

        hunt_candidates = [
            (x, y)
            for y in range(self.board_size)
            for x in range(self.board_size)
            if self._available((x, y)) and (x + y) % 2 == 0
        ]
        if hunt_candidates:
            return self.rng.choice(hunt_candidates)

        any_candidates = [
            (x, y)
            for y in range(self.board_size)
            for x in range(self.board_size)
            if self._available((x, y))
        ]
        if not any_candidates:
            any_candidates = [
                (x, y)
                for y in range(self.board_size)
                for x in range(self.board_size)
                if (x, y) not in self._shots
            ]
        if not any_candidates:
            raise RuntimeError("AI has no available shots")

        return self.rng.choice(any_candidates)

    def _choose_target_mode_shot(self) -> Optional[Coord]:
        hits = list(dict.fromkeys(self._target_hits))
        if not hits:
            return None

        if len(hits) == 1:
            base = hits[0]
            candidates = [n for n in iter_neighbors(base, self.board_size, include_diagonals=False) if self._available(n)]
            return self.rng.choice(candidates) if candidates else None

        xs = {x for x, _ in hits}
        ys = {y for _, y in hits}

        if len(xs) == 1:
            x = next(iter(xs))
            ys_sorted = sorted(ys)
            candidates: List[Coord] = []
            up = (x, ys_sorted[0] - 1)
            down = (x, ys_sorted[-1] + 1)
            if self._in_bounds(up) and self._available(up):
                candidates.append(up)
            if self._in_bounds(down) and self._available(down):
                candidates.append(down)
            return self.rng.choice(candidates) if candidates else None

        if len(ys) == 1:
            y = next(iter(ys))
            xs_sorted = sorted(xs)
            candidates = []
            left = (xs_sorted[0] - 1, y)
            right = (xs_sorted[-1] + 1, y)
            if self._in_bounds(left) and self._available(left):
                candidates.append(left)
            if self._in_bounds(right) and self._available(right):
                candidates.append(right)
            return self.rng.choice(candidates) if candidates else None

        # If somehow we have a non-linear set of hits, fallback to adjacency.
        candidates = []
        for h in hits:
            candidates.extend([n for n in iter_neighbors(h, self.board_size, include_diagonals=False) if self._available(n)])
        if candidates:
            return self.rng.choice(candidates)
        return None

    def process_result(self, coord: Coord, result: ShotResult, *, sunk_ship_cells: Optional[Sequence[Coord]] = None) -> None:
        self._shots.add(coord)

        if self.difficulty == Difficulty.EASY:
            return

        if result == ShotResult.HIT:
            self._target_hits.append(coord)
            return

        if result == ShotResult.SUNK:
            if sunk_ship_cells is None:
                # Fallback: assume only current hits belong to the ship.
                sunk_ship_cells = list(dict.fromkeys(self._target_hits + [coord]))

            for c in sunk_ship_cells:
                self._target_hits = [h for h in self._target_hits if h != c]
                for n in iter_neighbors(c, self.board_size, include_diagonals=True):
                    if n not in self._shots:
                        self._known_empty.add(n)

            self._target_hits.clear()
            return
