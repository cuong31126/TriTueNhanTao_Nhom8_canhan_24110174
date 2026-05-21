import random
import sys
from dataclasses import dataclass

import pygame


# 8-puzzle state: 0 is the blank tile.
GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 0)
BOARD_SIZE = 3
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640
FPS = 60

BOARD_LEFT = 32
BOARD_TOP = 104
TILE_SIZE = 112
BOARD_PIXELS = TILE_SIZE * BOARD_SIZE

PANEL_LEFT = 400
PANEL_TOP = 78
PANEL_WIDTH = 528
PANEL_HEIGHT = 400
PATH_TOP = 490

BG = (241, 239, 230)
INK = (36, 39, 46)
MUTED = (94, 101, 111)
BOARD_BG = (48, 55, 64)
BLANK = (218, 214, 202)
WHITE = (255, 255, 255)
OK = (52, 145, 108)
WARN = (222, 127, 78)
ACCENT = (31, 122, 140)
ACCENT_DARK = (24, 91, 105)
DISABLED = (169, 173, 176)
PANEL = (250, 248, 240)
LINE = (205, 202, 191)

TILE_COLORS = [
    (238, 169, 91),
    (92, 154, 170),
    (115, 169, 123),
    (217, 120, 91),
    (128, 114, 164),
    (228, 196, 105),
    (84, 138, 121),
    (196, 105, 125),
]

MOVE_NAMES = {
    "U": "Len",
    "D": "Xuong",
    "L": "Trai",
    "R": "Phai",
}


def swap_positions(state, a, b):
    data = list(state)
    data[a], data[b] = data[b], data[a]
    return tuple(data)


def state_to_grid_pos(index):
    return divmod(index, BOARD_SIZE)


def grid_pos_to_index(row, col):
    return row * BOARD_SIZE + col


def get_neighbors(state):
    """Return states that can be reached by moving the blank tile."""
    blank_index = state.index(0)
    row, col = state_to_grid_pos(blank_index)
    moves = [
        (-1, 0, "U"),
        (0, -1, "L"),
        (1, 0, "D"),
        (0, 1, "R"),
    ]

    result = []
    for dr, dc, move_name in moves:
        nr, nc = row + dr, col + dc
        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
            next_index = grid_pos_to_index(nr, nc)
            result.append((swap_positions(state, blank_index, next_index), move_name))
    return result


def create_scrambled_state(steps):
    state = GOAL_STATE
    previous_state = None
    for _ in range(steps):
        choices = get_neighbors(state)
        if previous_state is not None and len(choices) > 1:
            choices = [item for item in choices if item[0] != previous_state]
        previous_state = state
        state, _ = random.choice(choices)
    return state


class DFSSearcher:
    """Depth-limited DFS with parent links so the path can be visualized."""

    def __init__(self, start_state, max_depth):
        self.start_state = start_state
        self.max_depth = max_depth
        self.stack = [(start_state, 0)]
        self.parent = {start_state: (None, "START")}
        self.best_depth = {start_state: 0}
        self.current_state = start_state
        self.current_depth = 0
        self.explored = 0
        self.max_stack_size = 1
        self.done = False
        self.found = False
        self.solution_path = []
        self.solution_moves = []

    def step(self):
        if self.done:
            return

        while self.stack:
            state, depth = self.stack.pop()

            # A better route to this state was discovered after this item was
            # pushed. Skip the old copy so DFS does not waste time.
            if self.best_depth.get(state) != depth:
                continue

            self.current_state = state
            self.current_depth = depth
            self.explored += 1

            if state == GOAL_STATE:
                self.done = True
                self.found = True
                self.solution_path, self.solution_moves = self._build_path(state)
                return

            if depth < self.max_depth:
                # Reverse before pushing because the stack is LIFO.
                for next_state, move_name in reversed(get_neighbors(state)):
                    next_depth = depth + 1
                    old_depth = self.best_depth.get(next_state)
                    if old_depth is None or next_depth < old_depth:
                        self.best_depth[next_state] = next_depth
                        self.parent[next_state] = (state, move_name)
                        self.stack.append((next_state, next_depth))

            self.max_stack_size = max(self.max_stack_size, len(self.stack))
            return

        self.done = True
        self.found = False

    def _build_path(self, end_state):
        states = []
        moves = []
        state = end_state

        while state is not None:
            states.append(state)
            previous_state, move_name = self.parent[state]
            if previous_state is not None:
                moves.append(move_name)
            state = previous_state

        states.reverse()
        moves.reverse()
        return states, moves

    def current_branch(self, limit=10):
        if self.current_state not in self.parent:
            return [self.current_state]

        branch = []
        state = self.current_state
        while state is not None and len(branch) < limit:
            branch.append(state)
            state = self.parent[state][0]
        branch.reverse()
        return branch


@dataclass
class Button:
    rect: pygame.Rect
    text: str
    action: str
    enabled: bool = True

    def draw(self, surface, font, mouse_pos):
        if not self.enabled:
            fill = DISABLED
        elif self.rect.collidepoint(mouse_pos):
            fill = ACCENT_DARK
        else:
            fill = ACCENT

        pygame.draw.rect(surface, fill, self.rect, border_radius=8)
        label = font.render(self.text, True, WHITE)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)


class PuzzleDFSGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("8-Puzzle DFS Pygame")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.SysFont("segoe ui", 34, bold=True)
        self.big_font = pygame.font.SysFont("segoe ui", 58, bold=True)
        self.font = pygame.font.SysFont("segoe ui", 22)
        self.small_font = pygame.font.SysFont("segoe ui", 18)
        self.tiny_font = pygame.font.SysFont("segoe ui", 14)

        self.board_state = create_scrambled_state(12)
        self.manual_moves = 0
        self.depth_limit = 28
        self.scramble_steps = 12
        self.speed_index = 3
        self.speed_values = [1, 5, 20, 80, 220, 600]

        self.searcher = None
        self.search_paused = False
        self.solution_path = []
        self.solution_moves = []
        self.solution_index = 0
        self.solution_playing = False
        self.play_timer = 0.0
        self.message = "Bam DFS de tim duong di"

        self.buttons = []
        self._create_buttons()

    def _create_buttons(self):
        x = PANEL_LEFT + 18
        y = PANEL_TOP + 132
        w = 112
        h = 38
        gap = 9

        rows = [
            [("DFS", "dfs"), ("Tam dung", "pause"), ("Xao", "shuffle"), ("Reset", "reset")],
            [("< Buoc", "prev"), ("Chay", "play"), ("Buoc >", "next"), ("Ve dau", "path_start")],
            [("Depth -", "depth_down"), ("Depth +", "depth_up"), ("Toc -", "speed_down"), ("Toc +", "speed_up")],
            [("Tron -", "scramble_down"), ("Tron +", "scramble_up")],
        ]

        self.buttons.clear()
        for row_index, row in enumerate(rows):
            for col_index, (text, action) in enumerate(row):
                rect = pygame.Rect(x + col_index * (w + gap), y + row_index * (h + 12), w, h)
                self.buttons.append(Button(rect, text, action))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)

            self._update(dt)
            self._draw(mouse_pos)

        pygame.quit()
        sys.exit()

    def _handle_click(self, pos):
        for button in self.buttons:
            if button.enabled and button.rect.collidepoint(pos):
                self._handle_action(button.action)
                return

        if self._pos_inside_board(pos):
            self._handle_board_click(pos)

    def _handle_action(self, action):
        if action == "dfs":
            self._start_dfs()
        elif action == "pause":
            if self.searcher and not self.searcher.done:
                self.search_paused = not self.search_paused
                self.message = "DFS dang tam dung" if self.search_paused else "DFS dang chay"
            elif self.solution_path:
                self.solution_playing = False
                self.message = "Da tam dung duong di"
        elif action == "shuffle":
            self._shuffle()
        elif action == "reset":
            self._reset()
        elif action == "prev":
            self._step_solution(-1)
        elif action == "next":
            self._step_solution(1)
        elif action == "play":
            if self.solution_path:
                self.solution_playing = not self.solution_playing
                self.message = "Dang chay duong di" if self.solution_playing else "Da tam dung duong di"
        elif action == "path_start":
            if self.solution_path:
                self.solution_index = 0
                self.solution_playing = False
        elif action == "depth_down":
            self.depth_limit = max(1, self.depth_limit - 1)
            self._clear_search()
        elif action == "depth_up":
            self.depth_limit = min(80, self.depth_limit + 1)
            self._clear_search()
        elif action == "speed_down":
            self.speed_index = max(0, self.speed_index - 1)
        elif action == "speed_up":
            self.speed_index = min(len(self.speed_values) - 1, self.speed_index + 1)
        elif action == "scramble_down":
            self.scramble_steps = max(2, self.scramble_steps - 1)
        elif action == "scramble_up":
            self.scramble_steps = min(40, self.scramble_steps + 1)

    def _handle_key(self, key):
        if key == pygame.K_d:
            self._start_dfs()
        elif key == pygame.K_s:
            self._shuffle()
        elif key == pygame.K_r:
            self._reset()
        elif key == pygame.K_SPACE:
            self._handle_action("play")
        elif key == pygame.K_LEFT:
            if self.solution_path:
                self._step_solution(-1)
            else:
                self._move_blank(0, -1)
        elif key == pygame.K_RIGHT:
            if self.solution_path:
                self._step_solution(1)
            else:
                self._move_blank(0, 1)
        elif key == pygame.K_UP:
            self._move_blank(-1, 0)
        elif key == pygame.K_DOWN:
            self._move_blank(1, 0)

    def _start_dfs(self):
        start_state = self._display_state()
        self.board_state = start_state
        self.searcher = DFSSearcher(start_state, self.depth_limit)
        self.search_paused = False
        self.solution_path = []
        self.solution_moves = []
        self.solution_index = 0
        self.solution_playing = False
        self.message = "DFS dang tim..."

    def _shuffle(self):
        self.board_state = create_scrambled_state(self.scramble_steps)
        self.manual_moves = 0
        self._clear_search()
        self.message = f"Da xao {self.scramble_steps} buoc"

    def _reset(self):
        self.board_state = GOAL_STATE
        self.manual_moves = 0
        self._clear_search()
        self.message = "Da dua ve dich"

    def _clear_search(self):
        self.searcher = None
        self.search_paused = False
        self.solution_path = []
        self.solution_moves = []
        self.solution_index = 0
        self.solution_playing = False

    def _handle_board_click(self, pos):
        if self.searcher and not self.searcher.done:
            return

        state = self._display_state()
        col = (pos[0] - BOARD_LEFT) // TILE_SIZE
        row = (pos[1] - BOARD_TOP) // TILE_SIZE
        clicked_index = grid_pos_to_index(row, col)
        blank_index = state.index(0)
        clicked_row, clicked_col = state_to_grid_pos(clicked_index)
        blank_row, blank_col = state_to_grid_pos(blank_index)

        if abs(clicked_row - blank_row) + abs(clicked_col - blank_col) == 1:
            self.board_state = swap_positions(state, clicked_index, blank_index)
            self.manual_moves += 1
            self._clear_search()
            self.message = "Dung roi!" if self.board_state == GOAL_STATE else "Da di chuyen"

    def _move_blank(self, dr, dc):
        if self.searcher and not self.searcher.done:
            return

        state = self._display_state()
        blank_index = state.index(0)
        row, col = state_to_grid_pos(blank_index)
        nr, nc = row + dr, col + dc
        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
            next_index = grid_pos_to_index(nr, nc)
            self.board_state = swap_positions(state, blank_index, next_index)
            self.manual_moves += 1
            self._clear_search()
            self.message = "Dung roi!" if self.board_state == GOAL_STATE else "Da di chuyen"

    def _step_solution(self, direction):
        if not self.solution_path:
            return
        self.solution_playing = False
        self.solution_index = max(0, min(len(self.solution_path) - 1, self.solution_index + direction))
        self.message = f"Buoc {self.solution_index}/{len(self.solution_path) - 1}"

    def _update(self, dt):
        if self.searcher and not self.searcher.done and not self.search_paused:
            steps_per_frame = self.speed_values[self.speed_index]
            for _ in range(steps_per_frame):
                self.searcher.step()
                if self.searcher.done:
                    break

            if self.searcher.done:
                if self.searcher.found:
                    self.solution_path = self.searcher.solution_path
                    self.solution_moves = self.searcher.solution_moves
                    self.solution_index = 0
                    self.solution_playing = True
                    self.message = f"Tim thay loi giai {len(self.solution_path) - 1} buoc"
                else:
                    self.message = "Khong thay trong gioi han depth"

        if self.solution_path and self.solution_playing:
            self.play_timer += dt
            interval = max(0.08, 0.68 - self.speed_index * 0.1)
            if self.play_timer >= interval:
                self.play_timer = 0.0
                if self.solution_index < len(self.solution_path) - 1:
                    self.solution_index += 1
                else:
                    self.solution_playing = False
                    self.board_state = self.solution_path[-1]
                    self.message = "Da toi dich"

    def _display_state(self):
        if self.solution_path:
            return self.solution_path[self.solution_index]
        if self.searcher and not self.searcher.done:
            return self.searcher.current_state
        return self.board_state

    def _pos_inside_board(self, pos):
        x, y = pos
        return (
            BOARD_LEFT <= x < BOARD_LEFT + BOARD_PIXELS
            and BOARD_TOP <= y < BOARD_TOP + BOARD_PIXELS
        )

    def _draw(self, mouse_pos):
        self.screen.fill(BG)
        self._draw_title()
        self._draw_board(self._display_state())
        self._draw_panel(mouse_pos)
        self._draw_path_strip()
        pygame.display.flip()

    def _draw_title(self):
        title = self.title_font.render("8-PUZZLE DFS", True, INK)
        self.screen.blit(title, (32, 28))
        subtitle = self.font.render("Tim duong di bang Depth First Search", True, MUTED)
        self.screen.blit(subtitle, (34, 66))

    def _draw_board(self, state):
        board_rect = pygame.Rect(BOARD_LEFT - 10, BOARD_TOP - 10, BOARD_PIXELS + 20, BOARD_PIXELS + 20)
        pygame.draw.rect(self.screen, BOARD_BG, board_rect, border_radius=12)

        for index, value in enumerate(state):
            row, col = state_to_grid_pos(index)
            x = BOARD_LEFT + col * TILE_SIZE
            y = BOARD_TOP + row * TILE_SIZE
            rect = pygame.Rect(x + 5, y + 5, TILE_SIZE - 10, TILE_SIZE - 10)

            if value == 0:
                pygame.draw.rect(self.screen, BLANK, rect, border_radius=8)
                pygame.draw.rect(self.screen, (185, 180, 168), rect, 2, border_radius=8)
                continue

            fill = TILE_COLORS[value - 1]
            pygame.draw.rect(self.screen, fill, rect, border_radius=8)
            goal_index = GOAL_STATE.index(value)
            border = OK if goal_index == index else WARN
            pygame.draw.rect(self.screen, border, rect, 4, border_radius=8)

            label = self.big_font.render(str(value), True, WHITE)
            label_rect = label.get_rect(center=rect.center)
            self.screen.blit(label, label_rect)

    def _draw_panel(self, mouse_pos):
        rect = pygame.Rect(PANEL_LEFT, PANEL_TOP, PANEL_WIDTH, PANEL_HEIGHT)
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=8)
        pygame.draw.rect(self.screen, LINE, rect, 2, border_radius=8)

        content_x = PANEL_LEFT + 18
        status = self._status_text()
        self._draw_text(status, content_x, PANEL_TOP + 18, self.font, INK, bold=False)
        self._draw_text(self.message, content_x, PANEL_TOP + 48, self.small_font, MUTED, bold=False)
        self._draw_text("Trang thai hien tai", PANEL_LEFT + 380, PANEL_TOP + 18, self.tiny_font, MUTED)
        self._draw_state_matrix(self._display_state(), PANEL_LEFT + 392, PANEL_TOP + 42)

        for button in self.buttons:
            if button.action == "pause":
                button.text = "Chay tiep" if self.search_paused else "Tam dung"
            elif button.action == "play":
                button.text = "Dung" if self.solution_playing else "Chay"
            elif button.action in {"prev", "next", "path_start"}:
                button.enabled = bool(self.solution_path)
            else:
                button.enabled = True
            button.draw(self.screen, self.small_font, mouse_pos)

        info_y = PANEL_TOP + 332
        self._draw_text(f"Depth limit: {self.depth_limit}", content_x, info_y, self.small_font, INK)
        self._draw_text(f"Toc do DFS: {self.speed_values[self.speed_index]} state/frame", content_x, info_y + 24, self.small_font, INK)
        self._draw_text(f"So buoc tron: {self.scramble_steps}", content_x, info_y + 48, self.small_font, INK)

        if self.searcher:
            right_x = PANEL_LEFT + 300
            self._draw_text(f"Da mo: {self.searcher.explored}", right_x, info_y, self.small_font, INK)
            self._draw_text(f"Stack: {len(self.searcher.stack)}", right_x, info_y + 26, self.small_font, INK)
            self._draw_text(f"Depth hien tai: {self.searcher.current_depth}", right_x, info_y + 52, self.small_font, INK)
        else:
            self._draw_text(f"So nuoc tu choi: {self.manual_moves}", PANEL_LEFT + 300, info_y, self.small_font, INK)

    def _status_text(self):
        if self.searcher and not self.searcher.done:
            return "Trang thai: DFS dang tim"
        if self.solution_path:
            return f"Trang thai: co duong di ({len(self.solution_path) - 1} buoc)"
        if self.board_state == GOAL_STATE:
            return "Trang thai: dang o dich"
        return "Trang thai: choi tay hoac chay DFS"

    def _draw_state_matrix(self, state, x, y):
        cell = 29
        for index, value in enumerate(state):
            row, col = state_to_grid_pos(index)
            rect = pygame.Rect(x + col * cell, y + row * cell, cell - 4, cell - 4)
            fill = BLANK if value == 0 else (231, 229, 219)
            pygame.draw.rect(self.screen, fill, rect, border_radius=5)
            pygame.draw.rect(self.screen, LINE, rect, 1, border_radius=5)
            if value != 0:
                label = self.tiny_font.render(str(value), True, INK)
                self.screen.blit(label, label.get_rect(center=rect.center))

    def _draw_path_strip(self):
        rect = pygame.Rect(32, PATH_TOP - 10, WINDOW_WIDTH - 64, 148)
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=8)
        pygame.draw.rect(self.screen, LINE, rect, 2, border_radius=8)

        if self.solution_path:
            title = f"Duong di DFS: buoc {self.solution_index}/{len(self.solution_path) - 1}"
            if 0 < self.solution_index <= len(self.solution_moves):
                move = self._move_name(self.solution_moves[self.solution_index - 1])
                title += f" | buoc hien tai: {move}"
            move_line = "Cac buoc: " + self._moves_as_text(self.solution_moves)
            states = self._windowed_states(self.solution_path, self.solution_index, 12)
            active_state = self.solution_path[self.solution_index]
        elif self.searcher and not self.searcher.done:
            title = "Nhanh DFS dang tham"
            move_line = "DFS dang mo tung trang thai. Ket qua se hien Trai/Phai/Len/Xuong sau khi tim thay."
            states = self.searcher.current_branch(12)
            active_state = self.searcher.current_state
        else:
            title = "Duong di se hien o day sau khi chay DFS"
            move_line = "Bam DFS de tim loi giai, sau do xem chuoi di chuyen o day."
            states = []
            active_state = None

        self._draw_text(title, 50, PATH_TOP - 2, self.small_font, INK)
        self._draw_wrapped_text(move_line, 50, PATH_TOP + 22, self.small_font, MUTED, WINDOW_WIDTH - 100, 3)

        x = 50
        y = PATH_TOP + 96
        for state in states:
            active = state == active_state
            self._draw_mini_board(state, x, y, 42, active)
            x += 60

    def _windowed_states(self, states, active_index, count):
        half = count // 2
        start = max(0, active_index - half)
        end = min(len(states), start + count)
        start = max(0, end - count)
        return states[start:end]

    def _draw_mini_board(self, state, x, y, size, active=False):
        cell = size // BOARD_SIZE
        outline = ACCENT if active else LINE
        pygame.draw.rect(self.screen, outline, (x - 3, y - 3, size + 6, size + 6), border_radius=6)
        pygame.draw.rect(self.screen, WHITE, (x, y, size, size), border_radius=5)
        for index, value in enumerate(state):
            row, col = state_to_grid_pos(index)
            rect = pygame.Rect(x + col * cell + 1, y + row * cell + 1, cell - 2, cell - 2)
            fill = BLANK if value == 0 else (229, 229, 220)
            pygame.draw.rect(self.screen, fill, rect, border_radius=3)
            if value != 0:
                label = self.tiny_font.render(str(value), True, INK)
                self.screen.blit(label, label.get_rect(center=rect.center))

    def _move_name(self, move):
        return MOVE_NAMES.get(move, move)

    def _moves_as_text(self, moves):
        if not moves:
            return "Da o trang thai dich"
        return " -> ".join(self._move_name(move) for move in moves)

    def _draw_wrapped_text(self, text, x, y, font, color, max_width, max_lines):
        words = text.split()
        lines = []
        current = ""
        truncated = False

        for word_index, word in enumerate(words):
            test = word if not current else current + " " + word
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
                if len(lines) == max_lines:
                    truncated = word_index < len(words)
                    break

        if current and len(lines) < max_lines:
            lines.append(current)
        elif current and len(lines) == max_lines:
            truncated = True

        if truncated and lines:
            while font.size(lines[-1] + " ...")[0] > max_width and lines[-1]:
                lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else ""
            if lines[-1]:
                lines[-1] += " ..."

        for line_index, line in enumerate(lines):
            self._draw_text(line, x, y + line_index * 22, font, color)

    def _draw_text(self, text, x, y, font, color, bold=False):
        label = font.render(text, True, color)
        self.screen.blit(label, (x, y))


if __name__ == "__main__":
    PuzzleDFSGame().run()
