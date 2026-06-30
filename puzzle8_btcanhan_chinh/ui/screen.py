"""Top-level UI drawing entry point."""

import pygame

from constants import BG, BLUE, GREEN, GRID, MOVE_DELTAS, MUTED, ORANGE, RED, TEXT
from puzzle import is_solvable
from .controls import create_modes_button, create_modes_popup, draw_modes_popup
from .layout import draw_toolbar_scrollbar, get_layout
from .panels import draw_info_panel
from .primitives import draw_action_arrow, draw_board, draw_text
from .tree import draw_children, draw_frontier, draw_search_tree

def draw_ui(surface, vis, buttons, fonts, selected_board, selected_index, auto_run,
            mouse_pos=None, viewport_size=None, scroll_y=0, toolbar_scroll_x=0):
    surface.fill(BG)

    for btn in buttons:
        active = (
            (btn.action == "tab_bfs" and vis.mode in (1, 2))
            or (btn.action == "tab_dfs" and vis.mode == 3)
            or (btn.action == "tab_dfsl" and vis.mode == 4)
            or (btn.action == "tab_astar" and vis.mode == 5)
            or (btn.action == "tab_greedy" and vis.mode == 6)
            or (btn.action == "tab_manhattan" and vis.mode == 7)
            or (btn.action == "tab_ids" and vis.mode == 8)
            or (btn.action == "tab_hill" and vis.mode == 9)
            or (btn.action == "tab_steepest" and vis.mode == 10)
            or (btn.action == "tab_stochastic" and vis.mode == 11)
            or (btn.action == "tab_restart" and vis.mode == 12)
            or (btn.action == "tab_beam" and vis.mode == 13)
            or (btn.action == "tab_ac3" and vis.mode == 18)
            or (btn.action == "tab_minconflict" and vis.mode == 19)
            or (btn.action == "tab_andor" and vis.mode == 20)
            or (btn.action == "tab_backtracking" and vis.mode == 21)
            or (btn.action == "tab_forward" and vis.mode == 22)
            or (btn.action == "mode1" and vis.mode == 1)
            or (btn.action == "mode2" and vis.mode == 2)
            or (btn.action == "mode3" and vis.mode == 3)
            or (btn.action == "mode4" and vis.mode == 4)
        )
        if btn.action == "auto" and auto_run:
            active = True
        enabled = btn.action != "prev" or vis.can_go_back()
        btn.draw(surface, fonts["button"], active=active, enabled=enabled, mouse_pos=mouse_pos,
                 offset_x=toolbar_scroll_x)

    modes_button = create_modes_button(viewport_size[0] if viewport_size is not None else surface.get_width())
    modes_button.draw(surface, fonts["button"], active=getattr(vis, "popup_visible", False),
                      mouse_pos=mouse_pos)

    layout = get_layout(buttons)
    edit_cell = layout["edit_cell"]
    sx, sy = layout["start_pos"]
    gx, gy = layout["goal_pos"]
    start_selected = selected_index if selected_board == "start" else None
    goal_selected = selected_index if selected_board == "goal" else None

    hidden = getattr(vis, "hidden_indices", None) if vis.mode == 14 else None
    if vis.mode == 15:
        draw_text(surface, "START: (hidden in Blind Mode)", sx, sy - fonts["small_bold"].get_linesize() - 4,
                  fonts["small_bold"], MUTED)
        draw_text(surface, "GOAL: (hidden in Blind Mode)", gx, gy - fonts["small_bold"].get_linesize() - 4,
                  fonts["small_bold"], MUTED)
    else:
        draw_board(surface, vis.start, sx, sy, edit_cell, title="START",
                   border_color=BLUE if selected_board == "start" else GRID,
                   font=fonts["medium"], title_font=fonts["small_bold"], selected_index=start_selected,
                   hidden_indices=hidden)
        draw_board(surface, vis.goal, gx, gy, edit_cell, title="GOAL",
                   border_color=BLUE if selected_board == "goal" else GRID,
                   font=fonts["medium"], title_font=fonts["small_bold"], selected_index=goal_selected,
                   hidden_indices=hidden)

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
               border_color=GREEN if vis.found else GRID, font=fonts["big"],
               hidden_indices=hidden)
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

    draw_toolbar_scrollbar(surface, buttons, toolbar_scroll_x)

    if getattr(vis, "popup_visible", False):
        view_w, view_h = viewport_size if viewport_size is not None else surface.get_size()
        popup_rect, popup_buttons = create_modes_popup(view_w, view_h)
        popup_rect.y += scroll_y
        for pbtn in popup_buttons:
            pbtn.rect.y += scroll_y
        draw_modes_popup(surface, popup_rect, popup_buttons, fonts)
