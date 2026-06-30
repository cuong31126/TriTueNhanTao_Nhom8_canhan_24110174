"""Input helpers for board editing."""

import pygame

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
