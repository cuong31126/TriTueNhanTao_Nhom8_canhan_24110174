import pygame

from constants import (
    BG, BLUE, BOARD_N, CONTENT_HEIGHT, DARK_TILE, GREEN, GRID, MOVE_DELTAS,
    MUTED, ORANGE, PANEL, PANEL_2, RED, TEXT, TILE, TILE_TEXT, WHITE, WIDTH,
    YELLOW,
)
from puzzle import apply_move, compact_path, is_solvable, path_text, tiny_path, valid_moves


def draw_text(surface, text, x, y, font, color=TEXT, max_width=None, center=False, right=False):
    """Ve chu co ho tro xuong dong don gian theo max_width."""
    lines = []
    for raw_line in str(text).split("\n"):
        if max_width is None:
            lines.append(raw_line)
            continue

        words = raw_line.split(" ")
        current = ""
        for word in words:
            test = word if current == "" else current + " " + word
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        lines.append(current)

    yy = y
    for line in lines:
        img = font.render(line, True, color)
        rect = img.get_rect()
        if center:
            rect.centerx = x
            rect.y = yy
        elif right:
            rect.right = x
            rect.y = yy
        else:
            rect.x = x
            rect.y = yy
        surface.blit(img, rect)
        yy += font.get_linesize()
    return yy


def draw_board(surface, state, x, y, cell_size, title=None, border_color=None,
               font=None, title_font=None, selected_index=None):
    """Ve ban co 3x3. O 0 duoc ve mau toi de the hien o trong."""
    if title and title_font:
        draw_text(surface, title, x, y - title_font.get_linesize() - 4, title_font, TEXT)

    board_size = cell_size * BOARD_N
    outer = pygame.Rect(x - 3, y - 3, board_size + 6, board_size + 6)
    pygame.draw.rect(surface, border_color or GRID, outer, 3, border_radius=6)

    for i, value in enumerate(state):
        row, col = divmod(i, BOARD_N)
        rect = pygame.Rect(x + col * cell_size, y + row * cell_size, cell_size, cell_size)
        color = DARK_TILE if value == 0 else TILE
        pygame.draw.rect(surface, color, rect, border_radius=4)
        pygame.draw.rect(surface, GRID, rect, 1)

        if value != 0 and font:
            label = font.render(str(value), True, TILE_TEXT)
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)

        if selected_index == i:
            pygame.draw.rect(surface, BLUE, rect.inflate(-4, -4), 4, border_radius=4)


def draw_action_arrow(surface, action, center_x, center_y, length=72):
    """Ve mui ten minh hoa huong di chuyen cua o trong."""
    if action not in MOVE_DELTAS:
        return

    dx, dy = 0, 0
    if action == "UP":
        dy = -length
    elif action == "DOWN":
        dy = length
    elif action == "LEFT":
        dx = -length
    elif action == "RIGHT":
        dx = length

    start = (center_x, center_y)
    end = (center_x + dx, center_y + dy)
    pygame.draw.line(surface, ORANGE, start, end, 8)

    if action == "UP":
        points = [(end[0], end[1] - 16), (end[0] - 14, end[1] + 10), (end[0] + 14, end[1] + 10)]
    elif action == "DOWN":
        points = [(end[0], end[1] + 16), (end[0] - 14, end[1] - 10), (end[0] + 14, end[1] - 10)]
    elif action == "LEFT":
        points = [(end[0] - 16, end[1]), (end[0] + 10, end[1] - 14), (end[0] + 10, end[1] + 14)]
    else:
        points = [(end[0] + 16, end[1]), (end[0] - 10, end[1] - 14), (end[0] - 10, end[1] + 14)]
    pygame.draw.polygon(surface, ORANGE, points)


def action_letter(action):
    return action[0] if action else "?"


def tree_path_label(path, max_letters=3):
    if not path:
        return "S"
    label = "".join(action_letter(action) for action in path)
    if len(label) > max_letters:
        return label[-max_letters:]
    return label


def is_prefix_path(prefix, path):
    return len(prefix) <= len(path) and list(prefix) == list(path[:len(prefix)])


def draw_tree_node(surface, fonts, x, y, label, path, focus_path, border_color=GRID, radius=18):
    if list(path) == list(focus_path):
        fill = (78, 58, 35)
        border = ORANGE
        width = 4
        text_color = WHITE
    elif is_prefix_path(path, focus_path):
        fill = (45, 58, 78)
        border = BLUE
        width = 3
        text_color = WHITE
    else:
        fill = PANEL_2
        border = border_color
        width = 2
        text_color = TEXT

    pygame.draw.circle(surface, fill, (x, y), radius)
    pygame.draw.circle(surface, border, (x, y), radius, width)
    text_img = fonts["tiny_bold"].render(label, True, text_color)
    surface.blit(text_img, text_img.get_rect(center=(x, y)))


def tree_child_items(vis):
    root_state = getattr(vis, "tree_root_state", vis.current_state)
    root_path = list(getattr(vis, "tree_root_path", vis.current_path))

    if vis.children_info:
        return [dict(item) for item in vis.children_info[:4]]

    if not vis.ready or vis.failed or vis.found:
        return []

    items = []
    for action in valid_moves(root_state)[:4]:
        child = apply_move(root_state, action)
        child_path = root_path + [action]
        items.append({
            "state": child,
            "path": child_path,
            "action": action,
            "result": "PREVIEW",
            "color": GRID,
        })
    return items


def draw_search_tree(surface, vis, fonts, rect):
    pygame.draw.rect(surface, PANEL, rect, border_radius=8)
    pygame.draw.rect(surface, GRID, rect, 1, border_radius=8)

    title_x = rect.x + 14
    title_y = rect.y + 10
    draw_text(surface, "SEARCH TREE", title_x, title_y, fonts["small_bold"], TEXT)

    root_path = list(getattr(vis, "tree_root_path", vis.current_path))
    focus_path = list(getattr(vis, "tree_focus_path", vis.current_path))
    children = tree_child_items(vis)

    root_x = rect.centerx
    root_y = rect.y + 50
    child_y = rect.y + 108
    grand_y = rect.y + 158
    radius = 17

    draw_tree_node(surface, fonts, root_x, root_y, tree_path_label(root_path),
                   root_path, focus_path, border_color=BLUE, radius=radius)
    draw_text(surface, "current", root_x, root_y + 20, fonts["tiny"], MUTED, center=True)

    if not children:
        message = "No children yet" if not vis.found else "Goal node selected"
        draw_text(surface, message, rect.centerx, child_y - 8, fonts["small"], MUTED, center=True)
        return

    span = rect.w - 72
    child_count = len(children)
    for i, item in enumerate(children):
        if child_count == 1:
            child_x = root_x
        else:
            child_x = rect.x + 36 + int(i * span / (child_count - 1))

        child_path = list(item["path"])
        line_color = item["color"]
        pygame.draw.line(surface, line_color, (root_x, root_y + radius),
                         (child_x, child_y - radius), 3)

        label_x = (root_x + child_x) // 2
        label_y = (root_y + child_y) // 2 - 8
        draw_text(surface, action_letter(item["action"]), label_x, label_y,
                  fonts["tiny_bold"], line_color, center=True)

        draw_tree_node(surface, fonts, child_x, child_y, tree_path_label(child_path),
                       child_path, focus_path, border_color=line_color, radius=radius)
        draw_text(surface, item["result"], child_x, child_y + 20, fonts["tiny"],
                  line_color, max_width=82, center=True)

        grand_actions = valid_moves(item["state"])[:3]
        grand_count = len(grand_actions)
        for j, grand_action in enumerate(grand_actions):
            offset = int((j - (grand_count - 1) / 2) * 26)
            grand_x = child_x + offset
            grand_path = child_path + [grand_action]
            pygame.draw.line(surface, GRID, (child_x, child_y + radius),
                             (grand_x, grand_y - 11), 1)
            draw_tree_node(surface, fonts, grand_x, grand_y,
                           tree_path_label(grand_path, max_letters=2), grand_path, focus_path,
                           border_color=GRID, radius=11)


class Button:
    def __init__(self, x, y, w, h, text, action, kind="button"):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.kind = kind

    def draw(self, surface, font, active=False, enabled=True, mouse_pos=None):
        mouse = mouse_pos if mouse_pos is not None else pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mouse)
        radius = 7 if self.kind == "tab" else 6

        if not enabled:
            bg = (58, 62, 70)
            fg = (130, 135, 145)
            border = (75, 80, 90)
        elif active:
            bg = BLUE
            fg = WHITE
            border = (135, 185, 255)
        elif hover:
            bg = (66, 75, 90)
            fg = TEXT
            border = (105, 115, 130)
        elif self.kind == "tab":
            bg = PANEL
            fg = TEXT
            border = GRID
        else:
            bg = PANEL_2
            fg = TEXT
            border = GRID

        pygame.draw.rect(surface, bg, self.rect, border_radius=radius)
        pygame.draw.rect(surface, border, self.rect, 1, border_radius=radius)
        img = font.render(self.text, True, fg)
        surface.blit(img, img.get_rect(center=self.rect.center))
        if self.kind == "tab" and active:
            pygame.draw.line(surface, WHITE,
                             (self.rect.x + 14, self.rect.bottom - 4),
                             (self.rect.right - 14, self.rect.bottom - 4), 3)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


def draw_children(surface, vis, fonts, x0, y0):
    title_font = fonts["small_bold"]
    tiny_font = fonts["tiny"]
    small_font = fonts["small"]

    draw_text(surface, "CHILDREN GENERATED", x0, y0 - 28, title_font, TEXT)

    if not vis.children_info:
        draw_text(surface, "No children yet", x0, y0 + 36, small_font, MUTED)
        return

    cell = 28
    gap = 10
    board_size = cell * 3
    for i, item in enumerate(vis.children_info[:4]):
        x = x0 + i * (board_size + gap)
        y = y0
        draw_text(surface, item["action"], x + board_size // 2, y - 20, small_font, TEXT, center=True)
        draw_board(surface, item["state"], x, y, cell, border_color=item["color"], font=tiny_font)
        draw_text(surface, item["result"], x + board_size // 2, y + board_size + 7,
                  tiny_font, item["color"], max_width=board_size + 8, center=True)


def draw_frontier(surface, vis, fonts, x0, y0):
    title_font = fonts["small_bold"]
    tiny_font = fonts["tiny"]

    frontier_name = "FRONTIER / QUEUE" if vis.mode in (1, 2) else "FRONTIER / STACK"
    draw_text(surface, frontier_name, x0, y0 - 28, title_font, TEXT)

    cell = 22
    board_size = cell * 3
    gap_x = 12
    row_gap = 118
    columns = 10
    max_show = 30
    shown = []
    q_len = len(vis.queue)
    if q_len > 0:
        if vis.mode in (1, 2):
            for i in range(min(max_show, q_len)):
                shown.append(vis.queue[i])
        else:
            for i in range(min(max_show, q_len)):
                shown.append(vis.queue[q_len - 1 - i])

    if not shown:
        empty_text = "Queue is empty" if vis.mode in (1, 2) else "Stack is empty"
        draw_text(surface, empty_text, x0, y0 + 35, fonts["small"], MUTED)
        return

    for i, (state, path) in enumerate(shown):
        row, col = divmod(i, columns)
        x = x0 + col * (board_size + gap_x)
        y = y0 + row * row_gap
        draw_board(surface, state, x, y, cell, border_color=GRID, font=tiny_font)
        draw_text(surface, "#" + str(i + 1) + " len=" + str(len(path)),
                  x, y + board_size + 4, tiny_font, MUTED)
        draw_text(surface, tiny_path(path), x, y + board_size + 21, tiny_font, TEXT, max_width=board_size)

    rest = vis.frontier_size() - len(shown)
    if rest > 0:
        rows = (len(shown) + columns - 1) // columns
        draw_text(surface, "... and " + str(rest) + " more",
                  x0, y0 + rows * row_gap + 4, fonts["small"], MUTED)


def draw_info_panel(surface, vis, fonts, panel_rect):
    pygame.draw.rect(surface, PANEL, panel_rect, border_radius=8)
    pygame.draw.rect(surface, GRID, panel_rect, 1, border_radius=8)

    x = panel_rect.x + 16
    y = panel_rect.y + 14
    w = panel_rect.w - 32

    draw_text(surface, "ALGORITHM INFORMATION", x, y, fonts["small_bold"], TEXT)
    y += 34

    if vis.mode == 1:
        mode_name = "BFS Mode 1: check child before enqueue"
    elif vis.mode == 2:
        mode_name = "BFS Mode 2: check goal when dequeue"
    elif vis.mode == 3:
        mode_name = "DFS: stack-based depth-first search"
    else:
        mode_name = "DFS L: depth-limited DFS"

    frontier_label = "Queue size" if vis.mode in (1, 2) else "Stack size"
    rows = [
        ("Mode", mode_name),
        ("Step", str(vis.step)),
        ("Current action", vis.current_action),
        ("Current path", compact_path(vis.current_path, 7)),
        (frontier_label, str(vis.frontier_size())),
        ("Reached size", str(len(vis.reached))),
        ("Nodes expanded", str(vis.expanded)),
        ("Nodes generated", str(vis.generated)),
        ("Status", vis.status),
    ]

    for label, value in rows:
        draw_text(surface, label + ":", x, y, fonts["tiny_bold"], MUTED)
        y = draw_text(surface, value, x + 118, y, fonts["tiny"], TEXT, max_width=w - 118)
        y += 5

    if vis.mode == 4:
        y += 2
        draw_text(surface, "Depth limit:", x, y, fonts["tiny_bold"], MUTED)
        draw_text(surface, str(vis.depth_limit), x + 118, y, fonts["tiny"], TEXT)
        y += 18

    if vis.solution_path is not None:
        y += 6
        draw_text(surface, "Solution", x, y, fonts["small_bold"], GREEN)
        y += 22
        y = draw_text(surface, path_text(vis.solution_path), x, y, fonts["tiny"], TEXT, max_width=w)
        y += 4
        draw_text(surface, "Length: " + str(len(vis.solution_path)), x, y, fonts["tiny_bold"], GREEN)
        y += 22

    comparison_y = max(y + 20, panel_rect.y + 405)
    draw_result_summary(surface, vis, fonts, x, comparison_y, w)


def result_value(result, key):
    if result is None:
        return "-"
    value = result.get(key)
    if value is None:
        return "-"
    if key == "path":
        return path_text(value)
    return str(value)


def draw_result_summary(surface, vis, fonts, x, y, w):
    pygame.draw.line(surface, GRID, (x, y - 12), (x + w, y - 12), 1)
    if vis.mode in (1, 2):
        draw_text(surface, "COMPARISON", x, y, fonts["small_bold"], TEXT)
        y += 28

        r1 = vis.results.get(1)
        r2 = vis.results.get(2)

        col0 = x
        col1 = x + 125
        col2 = x + 225
        draw_text(surface, "Metric", col0, y, fonts["tiny_bold"], MUTED)
        draw_text(surface, "Mode 1", col1, y, fonts["tiny_bold"], BLUE)
        draw_text(surface, "Mode 2", col2, y, fonts["tiny_bold"], BLUE)
        y += 20

        rows = [
            ("Length", "length"),
            ("Expanded", "expanded"),
            ("Generated", "generated"),
            ("Queue left", "queue"),
            ("Reached", "reached"),
        ]

        for label, key in rows:
            draw_text(surface, label, col0, y, fonts["tiny"], MUTED)
            draw_text(surface, result_value(r1, key), col1, y, fonts["tiny"], TEXT)
            draw_text(surface, result_value(r2, key), col2, y, fonts["tiny"], TEXT)
            y += 18

        y += 2
        draw_text(surface, "Goal check", col0, y, fonts["tiny"], MUTED)
        draw_text(surface, "child", col1, y, fonts["tiny"], TEXT)
        draw_text(surface, "dequeue", col2, y, fonts["tiny"], TEXT)
        y += 22

        y = draw_text(surface, "Path M1: " + result_value(r1, "path"), x, y, fonts["tiny"], TEXT, max_width=w)
        y += 10
        draw_text(surface, "Path M2: " + result_value(r2, "path"), x, y, fonts["tiny"], TEXT, max_width=w)
    else:
        draw_text(surface, "RESULT SUMMARY", x, y, fonts["small_bold"], TEXT)
        y += 28

        result = vis.results.get(vis.mode)
        rows = [
            ("Length", "length"),
            ("Expanded", "expanded"),
            ("Generated", "generated"),
            ("Frontier", "queue"),
            ("Reached", "reached"),
            ("Status", None),
        ]
        for label, key in rows:
            draw_text(surface, label + ":", x, y, fonts["tiny_bold"], MUTED)
            if key is None:
                value = vis.status
            else:
                value = result_value(result, key)
            y = draw_text(surface, value, x + 110, y, fonts["tiny"], TEXT, max_width=w - 110)
            y += 18

        y += 6
        draw_text(surface, "Path:", x, y, fonts["tiny_bold"], MUTED)
        y = draw_text(surface, result_value(result, "path"), x + 110, y, fonts["tiny"], TEXT, max_width=w - 110)


def board_cell_at(pos, x, y, cell_size):
    px, py = pos
    board_size = cell_size * 3
    if x <= px < x + board_size and y <= py < y + board_size:
        col = (px - x) // cell_size
        row = (py - y) // cell_size
        return int(row * 3 + col)
    return None


def number_from_key(event):
    if pygame.K_0 <= event.key <= pygame.K_8:
        return event.key - pygame.K_0
    if pygame.K_KP0 <= event.key <= pygame.K_KP8:
        return event.key - pygame.K_KP0
    return None


def create_buttons(max_width=WIDTH, mode=1):
    buttons = []

    tab_labels = [
        ("BFS", "tab_bfs", 132),
        ("DFS", "tab_dfs", 118),
        ("DFS L", "tab_dfsl", 156),
    ]
    x = 20
    y = 16
    for text, action, width in tab_labels:
        buttons.append(Button(x, y, width, 38, text, action, kind="tab"))
        x += width + 8

    labels = []
    if mode in (1, 2):
        labels.extend([
            ("BFS M1", "mode1", 86),
            ("BFS M2", "mode2", 86),
        ])

    labels.extend([
        ("Next Step", "next", 102),
        ("Prev Step", "prev", 96),
        ("Auto Run", "auto", 96),
        ("Pause", "pause", 76),
        ("Reset", "reset", 76),
        ("Solve Full", "solve", 102),
        ("Easy Test", "easy", 98),
        ("Main Test", "main", 98),
    ])

    x = 20
    y = 68
    row_h = 46
    right_limit = max(360, max_width - 18)
    for text, action, width in labels:
        if x + width > right_limit and x > 20:
            x = 20
            y += row_h
        buttons.append(Button(x, y, width, 36, text, action))
        x += width + 9
    return buttons


def get_layout(buttons):
    toolbar_bottom = 58
    if buttons:
        toolbar_bottom = max(button.rect.bottom for button in buttons)

    edit_cell = 45
    edit_y = toolbar_bottom + 44
    edit_status_y = edit_y + edit_cell * 3 + 18
    current_y = edit_status_y + 66

    return {
        "edit_cell": edit_cell,
        "start_pos": (20, edit_y),
        "goal_pos": (190, edit_y),
        "edit_status_y": edit_status_y,
        "current": (20, current_y, 86),
        "children": (435, current_y),
        "tree": pygame.Rect(360, current_y + 170, 460, 190),
        "frontier": (20, current_y + 430),
        "info_panel": pygame.Rect(842, toolbar_bottom + 18, 338, CONTENT_HEIGHT - toolbar_bottom - 40),
    }


def scroll_limits(view_height):
    return max(0, CONTENT_HEIGHT - view_height)


def clamp_scroll(scroll_y, view_height):
    return max(0, min(scroll_y, scroll_limits(view_height)))


def scrollbar_geometry(view_width, view_height, scroll_y):
    max_scroll = scroll_limits(view_height)
    if max_scroll <= 0:
        return None, None

    track = pygame.Rect(view_width - 13, 10, 8, view_height - 20)
    ratio = view_height / CONTENT_HEIGHT
    thumb_h = max(44, int(track.height * ratio))
    thumb_y = track.y + int((track.height - thumb_h) * (scroll_y / max_scroll))
    thumb = pygame.Rect(track.x, thumb_y, track.width, thumb_h)
    return track, thumb


def draw_scrollbar(surface, scroll_y, content_height=CONTENT_HEIGHT):
    view_width, view_height = surface.get_size()
    track, thumb = scrollbar_geometry(view_width, view_height, scroll_y)
    if track is None:
        return

    pygame.draw.rect(surface, (40, 45, 54), track, border_radius=6)
    pygame.draw.rect(surface, GRID, track, 1, border_radius=6)
    pygame.draw.rect(surface, (115, 126, 145), thumb, border_radius=6)


def draw_ui(surface, vis, buttons, fonts, selected_board, selected_index, auto_run, mouse_pos=None):
    surface.fill(BG)

    for btn in buttons:
        active = (
            (btn.action == "tab_bfs" and vis.mode in (1, 2))
            or (btn.action == "tab_dfs" and vis.mode == 3)
            or (btn.action == "tab_dfsl" and vis.mode == 4)
            or (btn.action == "mode1" and vis.mode == 1)
            or (btn.action == "mode2" and vis.mode == 2)
            or (btn.action == "mode3" and vis.mode == 3)
            or (btn.action == "mode4" and vis.mode == 4)
        )
        if btn.action == "auto" and auto_run:
            active = True
        enabled = btn.action != "prev" or vis.can_go_back()
        btn.draw(surface, fonts["button"], active=active, enabled=enabled, mouse_pos=mouse_pos)

    layout = get_layout(buttons)
    edit_cell = layout["edit_cell"]
    sx, sy = layout["start_pos"]
    gx, gy = layout["goal_pos"]
    start_selected = selected_index if selected_board == "start" else None
    goal_selected = selected_index if selected_board == "goal" else None
    draw_board(surface, vis.start, sx, sy, edit_cell, title="START",
               border_color=BLUE if selected_board == "start" else GRID,
               font=fonts["medium"], title_font=fonts["small_bold"], selected_index=start_selected)
    draw_board(surface, vis.goal, gx, gy, edit_cell, title="GOAL",
               border_color=BLUE if selected_board == "goal" else GRID,
               font=fonts["medium"], title_font=fonts["small_bold"], selected_index=goal_selected)

    selected_text = "Selected: none"
    if selected_board is not None:
        selected_text = "Selected: " + selected_board.upper() + "[" + str(selected_index) + "]"
    edit_status_y = layout["edit_status_y"]
    draw_text(surface, selected_text, 20, edit_status_y, fonts["tiny"], MUTED)

    parity = "solvable" if is_solvable(vis.start, vis.goal) else "unsolvable"
    parity_color = GREEN if parity == "solvable" else RED
    draw_text(surface, "Parity: " + parity, 190, edit_status_y, fonts["tiny_bold"], parity_color)

    current_x, current_y, current_cell = layout["current"]
    draw_text(surface, "CURRENT BOARD", current_x, current_y - 34, fonts["small_bold"], TEXT)
    draw_board(surface, vis.current_state, current_x, current_y, current_cell,
               border_color=GREEN if vis.found else GRID, font=fonts["big"])
    if vis.current_action in MOVE_DELTAS:
        draw_action_arrow(surface, vis.current_action,
                          current_x + current_cell * 3 + 48,
                          current_y + current_cell * 3 // 2)
    draw_text(surface, "Action: " + vis.current_action, current_x, current_y + current_cell * 3 + 16,
              fonts["small_bold"], ORANGE if vis.current_action in MOVE_DELTAS else MUTED)

    children_x, children_y = layout["children"]
    frontier_x, frontier_y = layout["frontier"]
    draw_children(surface, vis, fonts, children_x, children_y)
    draw_search_tree(surface, vis, fonts, layout["tree"])
    draw_info_panel(surface, vis, fonts, layout["info_panel"])
    draw_frontier(surface, vis, fonts, frontier_x, frontier_y)
