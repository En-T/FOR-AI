from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from random import Random
from typing import List, Optional, Tuple

from .ai import BattleshipAI
from .board import Board
from .types import Coord, Difficulty, ShotResult


DEFAULT_SHIP_SET: Tuple[int, ...] = (4, 3, 3, 2, 2, 2, 1, 1, 1, 1)


class GamePhase(str, Enum):
    MENU = "menu"
    PLACEMENT = "placement"
    PLAY = "play"
    GAME_OVER = "game_over"


class Turn(str, Enum):
    PLAYER = "player"
    AI = "ai"


def coord_to_label(coord: Coord) -> str:
    x, y = coord
    return f"{chr(ord('A') + x)}{y + 1}"


@dataclass
class Game:
    difficulty: Difficulty = Difficulty.EASY
    rng: Random = field(default_factory=Random)

    phase: GamePhase = GamePhase.MENU
    turn: Turn = Turn.PLAYER
    winner: Optional[Turn] = None

    player_board: Board = field(default_factory=Board)
    ai_board: Board = field(default_factory=Board)
    ai: BattleshipAI = field(init=False)

    ship_queue: List[int] = field(default_factory=lambda: list(DEFAULT_SHIP_SET))
    placement_horizontal: bool = True

    last_message: str = ""

    def __post_init__(self) -> None:
        self.ai = BattleshipAI(difficulty=self.difficulty, board_size=self.player_board.size, rng=self.rng)

    def set_difficulty(self, difficulty: Difficulty) -> None:
        self.difficulty = difficulty
        self.ai.difficulty = difficulty

    def start_new_game(self) -> None:
        self.winner = None
        self.turn = Turn.PLAYER
        self.phase = GamePhase.PLACEMENT
        self.last_message = "Расставьте корабли"

        self.player_board.reset()
        self.ai_board.reset()
        self.ai.reset()

        self.ship_queue = list(DEFAULT_SHIP_SET)
        self.placement_horizontal = True

        self.ai_board.place_ships_randomly(DEFAULT_SHIP_SET, rng=self.rng)

    @property
    def placement_done(self) -> bool:
        return not self.ship_queue

    @property
    def current_ship_length(self) -> Optional[int]:
        return self.ship_queue[0] if self.ship_queue else None

    def toggle_orientation(self) -> None:
        self.placement_horizontal = not self.placement_horizontal

    def undo_last_placement(self) -> None:
        ship = self.player_board.pop_last_ship()
        if ship is None:
            return
        self.ship_queue.insert(0, ship.length)
        self.last_message = "Удалён последний корабль"

    def auto_place_player(self) -> None:
        self.player_board.place_ships_randomly(DEFAULT_SHIP_SET, rng=self.rng)
        self.ship_queue.clear()
        self.last_message = "Корабли расставлены автоматически"

    def place_player_ship(self, start: Coord) -> bool:
        length = self.current_ship_length
        if length is None:
            return False

        placed = self.player_board.place_ship(start, length, self.placement_horizontal)
        if not placed:
            self.last_message = "Нельзя поставить здесь (корабли не должны соприкасаться)"
            return False

        self.ship_queue.pop(0)
        if not self.ship_queue:
            self.last_message = "Расстановка завершена. Нажмите 'Начать'"
        else:
            self.last_message = f"Поставьте корабль: {self.ship_queue[0]} клет(ок)"
        return True

    def begin_battle(self) -> None:
        if not self.placement_done:
            self.last_message = "Сначала расставьте все корабли"
            return
        self.phase = GamePhase.PLAY
        self.turn = Turn.PLAYER
        self.last_message = "Ваш ход: выберите клетку на поле противника"

    def player_shoot(self, coord: Coord) -> ShotResult:
        if self.phase != GamePhase.PLAY or self.turn != Turn.PLAYER:
            return ShotResult.ALREADY_SHOT

        result, ship = self.ai_board.receive_shot(coord)
        if result == ShotResult.ALREADY_SHOT:
            self.last_message = "Вы уже стреляли сюда"
            return result

        if result == ShotResult.MISS:
            self.last_message = f"Вы: {coord_to_label(coord)} — мимо"
        elif result == ShotResult.HIT:
            self.last_message = f"Вы: {coord_to_label(coord)} — попадание"
        elif result == ShotResult.SUNK:
            self.last_message = f"Вы: {coord_to_label(coord)} — корабль потоплен"

        if self.ai_board.all_ships_sunk():
            self.phase = GamePhase.GAME_OVER
            self.winner = Turn.PLAYER
            self.last_message += "\nПобеда!"
            return result

        self.turn = Turn.AI
        return result

    def ai_shoot(self) -> tuple[Coord, ShotResult]:
        if self.phase != GamePhase.PLAY or self.turn != Turn.AI:
            raise RuntimeError("AI shot called at wrong time")

        coord = self.ai.choose_shot()
        result, ship = self.player_board.receive_shot(coord)

        sunk_cells = ship.cells if ship and ship.sunk else None
        self.ai.process_result(coord, result, sunk_ship_cells=sunk_cells)

        if result == ShotResult.MISS:
            self.last_message = f"Компьютер: {coord_to_label(coord)} — мимо"
        elif result == ShotResult.HIT:
            self.last_message = f"Компьютер: {coord_to_label(coord)} — попадание"
        elif result == ShotResult.SUNK:
            self.last_message = f"Компьютер: {coord_to_label(coord)} — корабль потоплен"

        if self.player_board.all_ships_sunk():
            self.phase = GamePhase.GAME_OVER
            self.winner = Turn.AI
            self.last_message += "\nПоражение"
            return coord, result

        self.turn = Turn.PLAYER
        return coord, result
