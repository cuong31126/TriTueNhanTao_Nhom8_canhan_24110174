"""Buttons, popup controls, and related UI helpers."""

import pygame

from constants import BLUE, GRID, PANEL, PANEL_2, TEXT, WHITE, WIDTH
from .primitives import draw_text

class Button:
    def __init__(self, x, y, w, h, text, action, kind="button"):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.kind = kind

    def draw(self, surface, font, active=False, enabled=True, mouse_pos=None, offset_x=0):
        mouse = mouse_pos if mouse_pos is not None else pygame.mouse.get_pos()
        draw_rect = self.rect.move(-offset_x, 0)
        hover = draw_rect.collidepoint(mouse)
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

        pygame.draw.rect(surface, bg, draw_rect, border_radius=radius)
        pygame.draw.rect(surface, border, draw_rect, 1, border_radius=radius)
        img = font.render(self.text, True, fg)
        surface.blit(img, img.get_rect(center=draw_rect.center))
        if self.kind == "tab" and active:
            pygame.draw.line(surface, WHITE,
                             (draw_rect.x + 14, draw_rect.bottom - 4),
                             (draw_rect.right - 14, draw_rect.bottom - 4), 3)

    def clicked(self, pos, offset_x=0):
        return self.rect.move(-offset_x, 0).collidepoint(pos)

def create_buttons(max_width=WIDTH, mode=1):
    buttons = []

    tab_labels = [
        ("BFS", "tab_bfs", 132),
        ("DFS", "tab_dfs", 118),
        ("DFS L", "tab_dfsl", 156),
        ("A*", "tab_astar", 76),
        ("Greedy", "tab_greedy", 112),
        ("Manhattan", "tab_manhattan", 136),
        ("AC-3", "tab_ac3", 124),
        ("Min-Conflicts", "tab_minconflict", 152),
        ("AND-OR", "tab_andor", 112),
        ("Backtracking", "tab_backtracking", 144),
        ("Forward Check", "tab_forward", 154),
        ("IDS", "tab_ids", 82),
        ("Leo nui doc", "tab_hill", 124),
        ("Doc ngan nhat", "tab_steepest", 142),
        ("Stochastic", "tab_stochastic", 128),
        ("Random Restart", "tab_restart", 162),
        ("Local Beam", "tab_beam", 126),
    ]
    x = 20
    y = 16
    for text, action, width in tab_labels:
        buttons.append(Button(x, y, width, 38, text, action, kind="tab"))
        x += width + 8
    tab_bottom = max(button.rect.bottom for button in buttons)

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
    y = tab_bottom + 14
    row_h = 46
    right_limit = max(360, max_width - 18)
    for text, action, width in labels:
        buttons.append(Button(x, y, width, 36, text, action))
        x += width + 9
    return buttons

def create_modes_button(view_w):
    """Tao nut Modes co dinh o goc phai tren giao dien."""
    return Button(view_w - 112, 16, 92, 38, "Modes", "open_popup")



def create_modes_popup(view_w, view_h):
    """Return popup rect and list of Buttons for the special popup modes."""
    popup_w = 420
    popup_h = 220
    x = (view_w - popup_w) // 2
    y = (view_h - popup_h) // 2
    popup_rect = pygame.Rect(x, y, popup_w, popup_h)

    btns = []
    bw = 180
    bh = 44
    left_x = x + 30
    right_x = x + popup_w - bw - 30
    top_y = y + 48

    btns.append(Button(left_x, top_y, bw, bh, "Hidden Tiles", "popup_hidden"))
    btns.append(Button(right_x, top_y, bw, bh, "Blind Mode", "popup_blind"))
    btns.append(Button(left_x, top_y + bh + 16, bw, bh, "No Start/Goal", "popup_nogenerate"))
    btns.append(Button(right_x, top_y + bh + 16, bw, bh, "Local Search Sim", "popup_localsearch"))
    return popup_rect, btns


def draw_modes_popup(surface, popup_rect, popup_buttons, fonts):
    """Draw the overlay popup and its buttons."""
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((8, 10, 12, 160))
    surface.blit(overlay, (0, 0))

    pygame.draw.rect(surface, PANEL, popup_rect, border_radius=8)
    pygame.draw.rect(surface, GRID, popup_rect, 2, border_radius=8)
    title_x = popup_rect.x + 20
    title_y = popup_rect.y + 10
    draw_text(surface, "SPECIAL MODES", title_x, title_y, fonts["small_bold"], TEXT)

    for btn in popup_buttons:
        btn.draw(surface, fonts["button"])
