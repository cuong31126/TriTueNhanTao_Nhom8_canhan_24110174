"""UI package for the 8-puzzle visualizer."""

import pygame

from constants import BLUE, BOARD_N, DARK_TILE, GRID, MUTED, MOVE_DELTAS, ORANGE, PANEL_2, TEXT, TILE, TILE_TEXT, WHITE

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
               font=None, title_font=None, selected_index=None, hidden_indices=None):
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
            if hidden_indices and i in hidden_indices:
                pygame.draw.rect(surface, MUTED, rect.inflate(-6, -6), border_radius=4)
            else:
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
