"""Tree and frontier rendering helpers for the UI."""

import heapq

import pygame

from constants import BLUE, GRID, MUTED, PANEL, TEXT, YELLOW, RED
from puzzle import apply_move, manhattan_distance, valid_moves, tiny_path
from .primitives import action_letter, draw_board, draw_text, draw_tree_node, tree_path_label

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

    if vis.mode in (1, 2):
        frontier_name = "FRONTIER / QUEUE"
    elif vis.mode in (5, 6, 7):
        frontier_name = "FRONTIER / PRIORITY QUEUE"
    elif vis.mode in (9, 10, 11, 12):
        frontier_name = "HILL CLIMBING NEXT STATE"
    elif vis.mode == 13:
        frontier_name = "LOCAL BEAM STATES"
    elif vis.mode in (14, 15, 16, 17, 18, 19, 20, 21, 22):
        frontier_name = "REPLAY PLAN STATES"
    else:
        frontier_name = "FRONTIER / STACK"
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
        elif vis.mode in (5, 6, 7):
            import heapq
            smallest = heapq.nsmallest(min(max_show, q_len), vis.queue)
            for priority, _tie, g_cost, state, path in smallest:
                label = "h=" if vis.mode == 6 else "f="
                shown.append((state, path, label + str(int(priority)) + " g=" + str(g_cost)))
        elif vis.mode in (9, 10, 11, 12):
            for i in range(min(max_show, q_len)):
                state, path = vis.queue[i]
                shown.append((state, path, "next"))
        elif vis.mode == 13:
            for i in range(min(max_show, q_len)):
                state, path = vis.queue[i]
                h_cost = manhattan_distance(state, vis.goal, vis.goal_pos)
                shown.append((state, path, "h=" + str(int(h_cost))))
        elif vis.mode in (14, 15, 16, 17, 18, 19, 20, 21, 22):
            for i in range(min(max_show, q_len)):
                state, path = vis.queue[i]
                shown.append((state, path, "replay"))
        else:
            for i in range(min(max_show, q_len)):
                shown.append(vis.queue[q_len - 1 - i])

    if not shown:
        if vis.mode in (1, 2):
            empty_text = "Queue is empty"
        elif vis.mode in (5, 6, 7):
            empty_text = "Priority Queue is empty"
        elif vis.mode in (9, 10, 11, 12):
            empty_text = "No next state"
        elif vis.mode == 13:
            empty_text = "Beam is empty"
        elif vis.mode in (14, 15, 16, 17, 18, 19, 20, 21, 22):
            empty_text = "Replay plan is empty"
        else:
            empty_text = "Stack is empty"
        draw_text(surface, empty_text, x0, y0 + 35, fonts["small"], MUTED)
        return

    def draw_frontier_item(i, state, path, extra_text=None):
        row, col = divmod(i, columns)
        x = x0 + col * (board_size + gap_x)
        y = y0 + row * row_gap
        draw_board(surface, state, x, y, cell, border_color=GRID, font=tiny_font)
        draw_text(surface, "#" + str(i + 1) + " len=" + str(len(path)),
                  x, y + board_size + 4, tiny_font, MUTED)
        draw_text(surface, tiny_path(path), x, y + board_size + 21, tiny_font, TEXT, max_width=board_size)
        if extra_text:
            draw_text(surface, extra_text, x, y + board_size + 38, tiny_font, YELLOW, max_width=board_size)

    for i, item in enumerate(shown):
        if vis.mode in (5, 6, 7):
            draw_frontier_item(i, item[0], item[1], extra_text=item[2])
        elif vis.mode in (9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22):
            draw_frontier_item(i, item[0], item[1], extra_text=item[2])
        else:
            draw_frontier_item(i, item[0], item[1])

    rest = vis.frontier_size() - len(shown)
    if rest > 0:
        rows = (len(shown) + columns - 1) // columns
        draw_text(surface, "... and " + str(rest) + " more",
                  x0, y0 + rows * row_gap + 4, fonts["small"], MUTED)
