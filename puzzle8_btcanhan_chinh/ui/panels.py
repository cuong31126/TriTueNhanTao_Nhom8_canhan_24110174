"""Information and result panels for the UI."""

import pygame

from constants import BLUE, GREEN, GRID, MUTED, PANEL, RED, TEXT
from puzzle import compact_path, path_text
from .primitives import draw_text

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
    elif vis.mode == 4:
        mode_name = "DFS L: depth-limited DFS"
    elif vis.mode == 5:
        mode_name = "A* Search (Manhattan distance)"
    elif vis.mode == 6:
        mode_name = "Greedy Best-First Search (h = Manhattan)"
    elif vis.mode == 7:
        mode_name = "Manhattan A*: f(n)=g(n)+h(n)"
    elif vis.mode == 8:
        mode_name = "IDS: iterative deepening search"
    elif vis.mode == 9:
        mode_name = "Hill Climbing: first better neighbor"
    elif vis.mode == 10:
        mode_name = "Steepest Hill Climbing: smallest h neighbor"
    elif vis.mode == 11:
        mode_name = "Stochastic Hill Climbing: random better neighbor"
    elif vis.mode == 12:
        mode_name = "Random-Restart Hill Climbing"
    elif vis.mode == 14:
        mode_name = "Hidden Tiles Mode"
    elif vis.mode == 15:
        mode_name = "Blind Mode"
    elif vis.mode == 16:
        mode_name = "Generated Start/Goal Mode"
    elif vis.mode == 17:
        mode_name = "Simulated Local Search: greedy best-first replay"
    elif vis.mode == 18:
        mode_name = "AC-3 Mode: constraint propagation replay"
    elif vis.mode == 19:
        mode_name = "Min-Conflicts: local-search replay"
    elif vis.mode == 20:
        mode_name = "AND-OR Search: conditional plan replay"
    elif vis.mode == 21:
        mode_name = "Backtracking Search: recursive DFS replay"
    elif vis.mode == 22:
        mode_name = "Forward Checking: CSP pruning replay"
    else:
        mode_name = "Local Beam Search"

    frontier_label = "Queue size" if vis.mode in (1, 2) else "Stack size" if vis.mode in (3, 4, 8) else "Beam size" if vis.mode == 13 else "Replay states" if vis.mode in (14, 15, 16, 17, 18, 19, 20, 21, 22) else "Next states" if vis.mode in (9, 10, 11, 12) else "PQ size"
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
    elif vis.mode == 8:
        y += 2
        draw_text(surface, "IDS limit:", x, y, fonts["tiny_bold"], MUTED)
        draw_text(surface, str(vis.ids_depth_limit) + " / " + str(vis.ids_max_depth),
                  x + 118, y, fonts["tiny"], TEXT)
        y += 18
    elif vis.mode == 12:
        y += 2
        draw_text(surface, "Restarts:", x, y, fonts["tiny_bold"], MUTED)
        draw_text(surface, str(vis.restart_count) + " / " + str(vis.RANDOM_RESTART_LIMIT),
                  x + 118, y, fonts["tiny"], TEXT)
        y += 18
    elif vis.mode == 13:
        y += 2
        draw_text(surface, "Beam width:", x, y, fonts["tiny_bold"], MUTED)
        draw_text(surface, str(vis.beam_width), x + 118, y, fonts["tiny"], TEXT)
        y += 18
    elif vis.mode in (14, 15, 16, 17, 18, 19, 20, 21, 22):
        y += 2
        draw_text(surface, "Replay:", x, y, fonts["tiny_bold"], MUTED)
        total = len(getattr(vis, "precomputed_path", []) or [])
        done = getattr(vis, "precomputed_index", 0)
        draw_text(surface, str(done) + " / " + str(total), x + 118, y, fonts["tiny"], TEXT)
        y += 18
        if vis.mode == 14:
            draw_text(surface, "Hidden tiles:", x, y, fonts["tiny_bold"], MUTED)
            draw_text(surface, str(len(getattr(vis, "hidden_indices", set()))),
                      x + 118, y, fonts["tiny"], TEXT)
            y += 18

    if vis.solution_path is not None:
        y += 6
        draw_text(surface, "Solution", x, y, fonts["small_bold"], GREEN)
        y += 22
        y = draw_text(surface, compact_path(vis.solution_path, 12), x, y, fonts["tiny"], TEXT, max_width=w)
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
        return compact_path(value, 12)
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
