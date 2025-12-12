from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import pygame

from .board import Board
from .game import Game, GamePhase, Turn
from .types import CellState, Coord, Difficulty, ShotResult


Color = Tuple[int, int, int]


@dataclass
class Button:
    rect: pygame.Rect
    text: str
    on_click: Callable[[], None]

    def draw(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        *,
        enabled: bool = True,
        selected: bool = False,
    ) -> None:
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)

        bg: Color
        if not enabled:
            bg = (80, 80, 80)
        elif selected:
            bg = (70, 140, 90)
        elif hovered:
            bg = (70, 120, 200)
        else:
            bg = (50, 90, 160)

        pygame.draw.rect(screen, bg, self.rect, border_radius=8)
        pygame.draw.rect(screen, (20, 20, 20), self.rect, width=2, border_radius=8)

        label = font.render(self.text, True, (240, 240, 240))
        screen.blit(label, label.get_rect(center=self.rect.center))

    def handle_event(self, event: pygame.event.Event, *, enabled: bool = True) -> None:
        if not enabled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()


class BattleshipUI:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Морской бой")

        self.cell_size = 32
        self.grid_size = 10

        board_px = self.cell_size * self.grid_size
        margin = 30
        gap = 70
        panel_h = 220
        header_h = 60

        self.left_board_rect = pygame.Rect(margin, header_h, board_px, board_px)
        self.right_board_rect = pygame.Rect(margin + board_px + gap, header_h, board_px, board_px)

        width = margin * 2 + board_px * 2 + gap
        height = header_h + board_px + panel_h

        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(None, 22)
        self.font_small = pygame.font.SysFont(None, 18)
        self.font_big = pygame.font.SysFont(None, 54)

        self.game = Game()
        self._ai_next_action_ms: int = 0

        self._build_menu_buttons()
        self._build_placement_buttons()
        self._build_game_over_buttons()

    def _build_menu_buttons(self) -> None:
        center_x = self.screen.get_width() // 2
        start_y = 200
        w, h = 260, 44
        spacing = 16

        def set_easy() -> None:
            self.game.set_difficulty(Difficulty.EASY)

        def set_medium() -> None:
            self.game.set_difficulty(Difficulty.MEDIUM)

        def start_game() -> None:
            self.game.start_new_game()

        def quit_game() -> None:
            pygame.quit()
            raise SystemExit

        self.btn_easy = Button(pygame.Rect(center_x - w // 2, start_y, w, h), "Легко", set_easy)
        self.btn_medium = Button(
            pygame.Rect(center_x - w // 2, start_y + (h + spacing), w, h), "Средне", set_medium
        )
        self.btn_new = Button(
            pygame.Rect(center_x - w // 2, start_y + 2 * (h + spacing) + 10, w, h), "Новая игра", start_game
        )
        self.btn_quit = Button(
            pygame.Rect(center_x - w // 2, start_y + 3 * (h + spacing) + 10, w, h), "Выход", quit_game
        )

    def _build_placement_buttons(self) -> None:
        w, h = 150, 38
        y = self.left_board_rect.bottom + 20
        x = self.left_board_rect.left

        self.btn_begin = Button(pygame.Rect(x, y, w, h), "Начать", self.game.begin_battle)
        self.btn_auto = Button(pygame.Rect(x + w + 14, y, w, h), "Авто", self.game.auto_place_player)
        self.btn_undo = Button(pygame.Rect(x + 2 * (w + 14), y, w, h), "Отменить", self.game.undo_last_placement)

    def _build_game_over_buttons(self) -> None:
        center_x = self.screen.get_width() // 2
        y = self.left_board_rect.bottom + 20
        w, h = 190, 40
        spacing = 14

        def new_game() -> None:
            self.game.start_new_game()

        def to_menu() -> None:
            self.game.phase = GamePhase.MENU
            self.game.last_message = ""

        def quit_game() -> None:
            pygame.quit()
            raise SystemExit

        total_w = 3 * w + 2 * spacing
        start_x = center_x - total_w // 2

        self.btn_over_new = Button(pygame.Rect(start_x, y, w, h), "Новая игра", new_game)
        self.btn_over_menu = Button(pygame.Rect(start_x + w + spacing, y, w, h), "Меню", to_menu)
        self.btn_over_quit = Button(pygame.Rect(start_x + 2 * (w + spacing), y, w, h), "Выход", quit_game)

    def run(self) -> None:
        while True:
            self._handle_events()
            self._update()
            self._draw()
            pygame.display.flip()
            self.clock.tick(60)

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.game.phase == GamePhase.MENU:
                    pygame.quit()
                    raise SystemExit
                self.game.phase = GamePhase.MENU

            if self.game.phase == GamePhase.MENU:
                self.btn_easy.handle_event(event, enabled=True)
                self.btn_medium.handle_event(event, enabled=True)
                self.btn_new.handle_event(event, enabled=True)
                self.btn_quit.handle_event(event, enabled=True)

            elif self.game.phase == GamePhase.PLACEMENT:
                self._handle_placement_events(event)

            elif self.game.phase == GamePhase.PLAY:
                self._handle_play_events(event)

            elif self.game.phase == GamePhase.GAME_OVER:
                self.btn_over_new.handle_event(event)
                self.btn_over_menu.handle_event(event)
                self.btn_over_quit.handle_event(event)

    def _handle_placement_events(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.game.toggle_orientation()
            elif event.key == pygame.K_BACKSPACE:
                self.game.undo_last_placement()
            elif event.key == pygame.K_SPACE:
                self.game.auto_place_player()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
            if event.button == 3:
                self.game.toggle_orientation()
                return

            cell = self._cell_from_pos(self.left_board_rect, event.pos)
            if cell is None:
                return
            self.game.place_player_ship(cell)

        self.btn_begin.handle_event(event, enabled=self.game.placement_done)
        self.btn_auto.handle_event(event)
        self.btn_undo.handle_event(event, enabled=len(self.game.player_board.ships) > 0)

    def _handle_play_events(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.game.turn != Turn.PLAYER:
                return
            cell = self._cell_from_pos(self.right_board_rect, event.pos)
            if cell is None:
                return

            result = self.game.player_shoot(cell)
            if result != ShotResult.ALREADY_SHOT and self.game.turn == Turn.AI:
                self._ai_next_action_ms = pygame.time.get_ticks() + 550

    def _update(self) -> None:
        if self.game.phase == GamePhase.PLAY and self.game.turn == Turn.AI:
            now = pygame.time.get_ticks()
            if self._ai_next_action_ms and now >= self._ai_next_action_ms:
                self._ai_next_action_ms = 0
                self.game.ai_shoot()

    def _draw(self) -> None:
        self.screen.fill((18, 24, 38))

        if self.game.phase == GamePhase.MENU:
            self._draw_menu()
            return

        if self.game.phase == GamePhase.PLACEMENT:
            self._draw_header("Расстановка кораблей")
            self._draw_board(self.game.player_board, self.left_board_rect, reveal_ships=True, clickable=False)
            self._draw_board(self.game.ai_board, self.right_board_rect, reveal_ships=False, clickable=False, dim=True)

            self.btn_begin.draw(self.screen, self.font, enabled=self.game.placement_done)
            self.btn_auto.draw(self.screen, self.font, enabled=True)
            self.btn_undo.draw(self.screen, self.font, enabled=len(self.game.player_board.ships) > 0)

            self._draw_info_panel(self._placement_info())
            return

        if self.game.phase in (GamePhase.PLAY, GamePhase.GAME_OVER):
            header = "Бой" if self.game.phase == GamePhase.PLAY else "Игра окончена"
            self._draw_header(header)

            reveal_enemy = self.game.phase == GamePhase.GAME_OVER
            self._draw_board(self.game.player_board, self.left_board_rect, reveal_ships=True, clickable=False)
            self._draw_board(self.game.ai_board, self.right_board_rect, reveal_ships=reveal_enemy, clickable=self.game.phase == GamePhase.PLAY)

            if self.game.phase == GamePhase.GAME_OVER:
                title = "Победа" if self.game.winner == Turn.PLAYER else "Поражение"
                label = self.font_big.render(title, True, (240, 240, 240))
                self.screen.blit(label, label.get_rect(center=(self.screen.get_width() // 2, 40)))

                self.btn_over_new.draw(self.screen, self.font)
                self.btn_over_menu.draw(self.screen, self.font)
                self.btn_over_quit.draw(self.screen, self.font)

            self._draw_info_panel(self._play_info())
            return

    def _draw_menu(self) -> None:
        title = self.font_big.render("Морской бой", True, (240, 240, 240))
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width() // 2, 90)))

        info = self.font.render("Выберите сложность и начните игру", True, (210, 210, 210))
        self.screen.blit(info, info.get_rect(center=(self.screen.get_width() // 2, 145)))

        self.btn_easy.draw(self.screen, self.font, enabled=True, selected=self.game.difficulty == Difficulty.EASY)
        self.btn_medium.draw(self.screen, self.font, enabled=True, selected=self.game.difficulty == Difficulty.MEDIUM)
        self.btn_new.draw(self.screen, self.font, enabled=True)
        self.btn_quit.draw(self.screen, self.font, enabled=True)

        selected = "Легко" if self.game.difficulty == Difficulty.EASY else "Средне"
        selected_label = self.font_small.render(f"Текущая сложность: {selected}", True, (200, 200, 200))
        self.screen.blit(selected_label, selected_label.get_rect(center=(self.screen.get_width() // 2, 360)))

    def _draw_header(self, text: str) -> None:
        label = self.font.render(text, True, (235, 235, 235))
        self.screen.blit(label, (self.left_board_rect.left, 18))

        left = self.font_small.render("Ваше поле", True, (200, 200, 200))
        right = self.font_small.render("Поле противника", True, (200, 200, 200))
        self.screen.blit(left, (self.left_board_rect.left, self.left_board_rect.top - 22))
        self.screen.blit(right, (self.right_board_rect.left, self.right_board_rect.top - 22))

        if self.game.phase == GamePhase.PLAY:
            turn = "Ваш ход" if self.game.turn == Turn.PLAYER else "Ход компьютера"
            turn_label = self.font.render(turn, True, (235, 235, 235))
            self.screen.blit(turn_label, (self.right_board_rect.left, 18))

    def _draw_board(
        self,
        board: Board,
        rect: pygame.Rect,
        *,
        reveal_ships: bool,
        clickable: bool,
        dim: bool = False,
    ) -> None:
        bg = (32, 44, 70)
        if dim:
            bg = (22, 30, 48)
        pygame.draw.rect(self.screen, bg, rect, border_radius=6)

        mouse_pos = pygame.mouse.get_pos()
        hovered_cell = self._cell_from_pos(rect, mouse_pos) if clickable else None

        for y in range(board.size):
            for x in range(board.size):
                cell_rect = pygame.Rect(
                    rect.left + x * self.cell_size,
                    rect.top + y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )

                state = board.cell_state((x, y), reveal_ships=reveal_ships)
                color = self._color_for_state(state)

                if dim:
                    color = tuple(max(0, c - 25) for c in color)

                pygame.draw.rect(self.screen, color, cell_rect)

                if hovered_cell == (x, y) and (x, y) not in board.shots and not dim:
                    pygame.draw.rect(self.screen, (255, 255, 255), cell_rect, width=2)

        for i in range(board.size + 1):
            x = rect.left + i * self.cell_size
            y = rect.top + i * self.cell_size
            pygame.draw.line(self.screen, (10, 10, 10), (x, rect.top), (x, rect.bottom), 1)
            pygame.draw.line(self.screen, (10, 10, 10), (rect.left, y), (rect.right, y), 1)

    def _color_for_state(self, state: CellState) -> Color:
        if state == CellState.WATER:
            return (40, 82, 140)
        if state == CellState.SHIP:
            return (120, 130, 140)
        if state == CellState.MISS:
            return (215, 220, 230)
        if state == CellState.HIT:
            return (235, 85, 70)
        if state == CellState.SUNK:
            return (155, 30, 30)
        return (0, 0, 0)

    def _cell_from_pos(self, rect: pygame.Rect, pos: Tuple[int, int]) -> Optional[Coord]:
        if not rect.collidepoint(pos):
            return None
        x = (pos[0] - rect.left) // self.cell_size
        y = (pos[1] - rect.top) // self.cell_size
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return int(x), int(y)
        return None

    def _placement_info(self) -> str:
        lines = []
        if self.game.last_message:
            lines.append(self.game.last_message)

        if self.game.placement_done:
            lines.append("Все корабли расставлены. Нажмите 'Начать'.")
        else:
            length = self.game.current_ship_length
            orient = "горизонтально" if self.game.placement_horizontal else "вертикально"
            lines.append(f"Следующий корабль: {length} клет(ок) ({orient}).")

        lines.append("R или ПКМ — поворот. Backspace — отмена. Space — авто.")
        return "\n".join(lines)

    def _play_info(self) -> str:
        lines = []
        if self.game.last_message:
            lines.append(self.game.last_message)
        if self.game.phase == GamePhase.PLAY and self.game.turn == Turn.PLAYER:
            lines.append("Кликните по правому полю для выстрела")
        return "\n".join(lines)

    def _draw_info_panel(self, text: str) -> None:
        panel_rect = pygame.Rect(
            20,
            self.left_board_rect.bottom + 70,
            self.screen.get_width() - 40,
            self.screen.get_height() - (self.left_board_rect.bottom + 90),
        )
        pygame.draw.rect(self.screen, (24, 30, 46), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, (10, 10, 10), panel_rect, width=2, border_radius=10)

        y = panel_rect.top + 12
        for line in text.splitlines()[:6]:
            surf = self.font.render(line, True, (230, 230, 230))
            self.screen.blit(surf, (panel_rect.left + 14, y))
            y += 24


def run() -> None:
    BattleshipUI().run()
