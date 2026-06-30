"""Layout and scrollbar helpers for the UI."""

import pygame

from constants import CONTENT_HEIGHT, GRID

def get_layout(buttons):
    toolbar_bottom = 58
    if buttons:
        toolbar_bottom = max(button.rect.bottom for button in buttons) + 18

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

def toolbar_content_width(buttons):
    if not buttons:
        return 0
    return max(button.rect.right for button in buttons) + 20

def toolbar_scroll_limits(buttons, view_width):
    return max(0, toolbar_content_width(buttons) - view_width)

def toolbar_scrollbar_geometry(buttons, view_width, toolbar_scroll_x):
    max_scroll = toolbar_scroll_limits(buttons, view_width)
    if max_scroll <= 0:
        return None, None

    toolbar_bottom = max(button.rect.bottom for button in buttons)
    track = pygame.Rect(20, toolbar_bottom + 8, max(40, view_width - 40), 8)
    content_width = toolbar_content_width(buttons)
    ratio = min(1.0, view_width / max(1, content_width))
    thumb_w = max(56, int(track.width * ratio))
    thumb_x = track.x + int((track.width - thumb_w) * (toolbar_scroll_x / max_scroll))
    thumb = pygame.Rect(thumb_x, track.y, thumb_w, track.height)
    return track, thumb

def draw_toolbar_scrollbar(surface, buttons, toolbar_scroll_x):
    view_width, _ = surface.get_size()
    track, thumb = toolbar_scrollbar_geometry(buttons, view_width, toolbar_scroll_x)
    if track is None:
        return

    pygame.draw.rect(surface, (40, 45, 54), track, border_radius=6)
    pygame.draw.rect(surface, GRID, track, 1, border_radius=6)
    pygame.draw.rect(surface, (115, 126, 145), thumb, border_radius=6)

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
