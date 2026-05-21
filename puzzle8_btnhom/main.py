import pygame

from constants import BG, CONTENT_HEIGHT, EASY_GOAL, EASY_START, FPS, HEIGHT, MAIN_GOAL, MAIN_START, WIDTH
from puzzle import edit_board_value
from ui import (
    board_cell_at, clamp_scroll, create_buttons, draw_scrollbar, draw_ui,
    get_layout, number_from_key, scrollbar_geometry,
)
from visualizer import SearchVisualizer


def create_fonts():
    return {
        "tiny": pygame.font.SysFont("arial", 14),
        "tiny_bold": pygame.font.SysFont("arial", 14, bold=True),
        "small": pygame.font.SysFont("arial", 17),
        "small_bold": pygame.font.SysFont("arial", 17, bold=True),
        "button": pygame.font.SysFont("arial", 16, bold=True),
        "medium": pygame.font.SysFont("arial", 28, bold=True),
        "big": pygame.font.SysFont("arial", 48, bold=True),
    }


def handle_button(action, vis):
    """Xu ly nut bam va tra ve True neu can tat auto-run."""
    stop_auto = True

    if action == "tab_bfs":
        vis.set_mode(vis.bfs_mode)
    elif action == "tab_dfs":
        vis.set_mode(3)
    elif action == "tab_dfsl":
        vis.set_mode(4)
    elif action == "mode1":
        vis.set_mode(1)
    elif action == "mode2":
        vis.set_mode(2)
    elif action == "mode3":
        vis.set_mode(3)
    elif action == "mode4":
        vis.set_mode(4)
    elif action == "next":
        vis.next_step()
    elif action == "prev":
        vis.previous_step()
    elif action == "auto":
        stop_auto = False
    elif action == "pause":
        pass
    elif action == "reset":
        vis.reset_run(keep_results=True)
    elif action == "solve":
        vis.solve_full()
    elif action == "easy":
        vis.update_puzzle(EASY_START, EASY_GOAL)
    elif action == "main":
        vis.update_puzzle(MAIN_START, MAIN_GOAL)

    return stop_auto


def main():
    pygame.init()
    pygame.display.set_caption("8-Puzzle Search Visualizer")

    display_info = pygame.display.Info()
    initial_w = min(WIDTH, max(900, display_info.current_w - 80))
    initial_h = min(HEIGHT, max(620, display_info.current_h - 120))
    screen = pygame.display.set_mode((initial_w, initial_h), pygame.RESIZABLE)
    content = pygame.Surface((WIDTH, CONTENT_HEIGHT))
    clock = pygame.time.Clock()

    fonts = create_fonts()
    vis = SearchVisualizer(MAIN_START, MAIN_GOAL, mode=1)
    buttons = create_buttons(screen.get_width(), vis.mode)

    auto_run = False
    last_auto_tick = 0
    scroll_y = 0
    dragging_scrollbar = False
    scrollbar_drag_offset = 0
    selected_board = None
    selected_index = None

    running = True
    while running:
        now = pygame.time.get_ticks()
        view_w, view_h = screen.get_size()
        scroll_y = clamp_scroll(scroll_y, view_h)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                new_w = max(760, event.w)
                new_h = max(560, event.h)
                screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
                buttons = create_buttons(new_w, vis.mode)
                scroll_y = clamp_scroll(scroll_y, new_h)

            elif event.type == pygame.MOUSEWHEEL:
                scroll_y = clamp_scroll(scroll_y - event.y * 45, screen.get_height())

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                track, thumb = scrollbar_geometry(screen.get_width(), screen.get_height(), scroll_y)
                if thumb is not None and thumb.collidepoint(event.pos):
                    dragging_scrollbar = True
                    scrollbar_drag_offset = event.pos[1] - thumb.y
                    continue
                if track is not None and track.collidepoint(event.pos):
                    target_ratio = (event.pos[1] - track.y) / max(1, track.height)
                    max_scroll = CONTENT_HEIGHT - screen.get_height()
                    scroll_y = clamp_scroll(int(target_ratio * max_scroll), screen.get_height())
                    continue

                pos = (event.pos[0], event.pos[1] + scroll_y)
                clicked_button = None
                for button in buttons:
                    if button.clicked(pos):
                        clicked_button = button.action
                        break

                if clicked_button is not None:
                    if clicked_button == "auto":
                        if vis.ready and not vis.found and not vis.failed:
                            auto_run = True
                            last_auto_tick = 0
                    else:
                        old_mode = vis.mode
                        auto_run = False if handle_button(clicked_button, vis) else auto_run
                        if clicked_button.startswith("tab_") or clicked_button.startswith("mode") or vis.mode != old_mode:
                            buttons = create_buttons(screen.get_width(), vis.mode)
                            scroll_y = clamp_scroll(scroll_y, screen.get_height())
                        if clicked_button in ("easy", "main"):
                            selected_board = None
                            selected_index = None
                else:
                    layout = get_layout(buttons)
                    edit_cell = layout["edit_cell"]
                    start_pos = layout["start_pos"]
                    goal_pos = layout["goal_pos"]
                    idx = board_cell_at(pos, start_pos[0], start_pos[1], edit_cell)
                    if idx is not None:
                        selected_board = "start"
                        selected_index = idx
                    else:
                        idx = board_cell_at(pos, goal_pos[0], goal_pos[1], edit_cell)
                        if idx is not None:
                            selected_board = "goal"
                            selected_index = idx

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_scrollbar = False

            elif event.type == pygame.MOUSEMOTION and dragging_scrollbar:
                track, thumb = scrollbar_geometry(screen.get_width(), screen.get_height(), scroll_y)
                if track is not None and thumb is not None:
                    thumb_y = event.pos[1] - scrollbar_drag_offset
                    usable = max(1, track.height - thumb.height)
                    ratio = (thumb_y - track.y) / usable
                    scroll_y = clamp_scroll(int(ratio * (CONTENT_HEIGHT - screen.get_height())), screen.get_height())

            elif event.type == pygame.KEYDOWN:
                value = number_from_key(event)
                if value is not None and selected_board is not None and selected_index is not None:
                    auto_run = False
                    if selected_board == "start":
                        new_start = edit_board_value(vis.start, selected_index, value)
                        vis.update_puzzle(new_start, vis.goal)
                    else:
                        new_goal = edit_board_value(vis.goal, selected_index, value)
                        vis.update_puzzle(vis.start, new_goal)
                elif event.key == pygame.K_SPACE:
                    auto_run = False
                    vis.next_step()
                elif event.key == pygame.K_HOME:
                    scroll_y = 0
                elif event.key == pygame.K_END:
                    scroll_y = clamp_scroll(CONTENT_HEIGHT, screen.get_height())
                elif event.key == pygame.K_PAGEUP:
                    scroll_y = clamp_scroll(scroll_y - screen.get_height() + 80, screen.get_height())
                elif event.key == pygame.K_PAGEDOWN:
                    scroll_y = clamp_scroll(scroll_y + screen.get_height() - 80, screen.get_height())

        auto_delay = 25 if vis.mode in (3, 4) else 500
        auto_steps = 80 if vis.mode in (3, 4) else 1
        if auto_run and now - last_auto_tick >= auto_delay:
            for _ in range(auto_steps):
                vis.next_step(record_history=vis.mode in (1, 2))
                if vis.found or vis.failed:
                    break
            last_auto_tick = now
            if vis.found or vis.failed:
                auto_run = False

        mouse_x, mouse_y = pygame.mouse.get_pos()
        draw_ui(content, vis, buttons, fonts, selected_board, selected_index, auto_run,
                mouse_pos=(mouse_x, mouse_y + scroll_y))
        screen.fill(BG)
        screen.blit(content, (0, -scroll_y))
        draw_scrollbar(screen, scroll_y)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
