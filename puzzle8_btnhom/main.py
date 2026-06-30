import pygame

# Import cac hang so cau hinh chung cua chuong trinh.
from constants import BG, CONTENT_HEIGHT, EASY_GOAL, EASY_START, FPS, HEIGHT, MAIN_GOAL, MAIN_START, WIDTH

# Ham dung khi nguoi dung sua truc tiep gia tri tren bang START/GOAL.
from puzzle import edit_board_value

# Cac ham ve giao dien va tinh toan vi tri trong giao dien.
from ui import (
    board_cell_at, clamp_scroll, create_buttons, create_modes_button, draw_scrollbar, draw_ui,
    get_layout, number_from_key, scrollbar_geometry, toolbar_scroll_limits,
    toolbar_scrollbar_geometry,
)
from ui import create_modes_popup

# Lop quan ly toan bo thuat toan tim kiem va trang thai hien tai.
from visualizer import SearchVisualizer


# Tao cac font chu dung chung trong giao dien.
def create_fonts():
    """Tao va gom cac font Pygame theo ten de cac file UI dung lai de dang."""
    return {
        "tiny": pygame.font.SysFont("arial", 14),
        "tiny_bold": pygame.font.SysFont("arial", 14, bold=True),
        "small": pygame.font.SysFont("arial", 17),
        "small_bold": pygame.font.SysFont("arial", 17, bold=True),
        "button": pygame.font.SysFont("arial", 16, bold=True),
        "medium": pygame.font.SysFont("arial", 28, bold=True),
        "big": pygame.font.SysFont("arial", 48, bold=True),
    }


# Xu ly action cua nut bam va goi ham tuong ung tren SearchVisualizer.
def handle_button(action, vis):
    """Xu ly nut bam va tra ve True neu can tat auto-run."""
    # Mac dinh moi nut bam se dung auto-run, tru nut Auto Run.
    stop_auto = True

    # Cac tab thuat toan: doi mode trong SearchVisualizer.
    if action == "tab_bfs":
        vis.set_mode(vis.bfs_mode)
    elif action == "tab_dfs":
        vis.set_mode(3)
    elif action == "tab_dfsl":
        vis.set_mode(4)
    elif action == "tab_astar":
        vis.set_mode(5)
    elif action == "tab_greedy":
        vis.set_mode(6)
    elif action == "tab_manhattan":
        vis.set_mode(7)
    elif action == "tab_ids":
        vis.set_mode(8)
    elif action == "tab_hill":
        vis.set_mode(9)
    elif action == "tab_steepest":
        vis.set_mode(10)
    elif action == "tab_stochastic":
        vis.set_mode(11)
    elif action == "tab_restart":
        vis.set_mode(12)
    elif action == "tab_beam":
        vis.set_mode(13)
    elif action == "tab_ac3":
        vis.set_mode(18)
    elif action == "tab_minconflict":
        vis.set_mode(19)

    # Cac nut mode rieng cua BFS/DFS.
    elif action == "mode1":
        vis.set_mode(1)
    elif action == "mode2":
        vis.set_mode(2)
    elif action == "mode3":
        vis.set_mode(3)
    elif action == "mode4":
        vis.set_mode(4)


    # Modes popup toggle
    elif action == "open_popup":
        vis.popup_visible = not getattr(vis, "popup_visible", False)
    elif action == "popup_hidden":
        vis.set_mode(14)
        vis.popup_visible = False
    elif action == "popup_blind":
        vis.set_mode(15)
        vis.popup_visible = False
    elif action == "popup_nogenerate":
        vis.set_mode(16)
        vis.popup_visible = False
    elif action == "popup_localsearch":
        vis.set_mode(17)
        vis.popup_visible = False
    

    # Cac nut dieu khien qua trinh chay thuat toan.
    elif action == "next":
        vis.next_step()
    elif action == "prev":
        vis.previous_step()
    elif action == "auto":
        # Nut Auto chi bat co auto_run o vong lap main, khong chay truc tiep tai day.
        stop_auto = False
    elif action == "pause":
        # Pause khong can lam gi them vi main da tat auto_run truoc do.
        pass
    elif action == "reset":
        vis.reset_current_mode(keep_results=True)
    elif action == "solve":
        vis.solve_full()

    # Cac bo test co san.
    elif action == "easy":
        vis.update_puzzle(EASY_START, EASY_GOAL)
    elif action == "main":
        vis.update_puzzle(MAIN_START, MAIN_GOAL)

    return stop_auto


# Ham chinh dieu phoi vong lap Pygame, event, thuat toan va render.
def main():
    """Diem vao chinh: khoi tao Pygame, xu ly event, cap nhat thuat toan va ve UI."""
    pygame.init()
    pygame.display.set_caption("8-Puzzle Search Visualizer")

    # Lay kich thuoc man hinh that de mo cua so vua phai voi may dang chay.
    display_info = pygame.display.Info()
    initial_w = min(WIDTH, max(900, display_info.current_w - 80))
    initial_h = min(HEIGHT, max(620, display_info.current_h - 120))

    # screen la cua so that; content la surface lon hon de co the cuon.
    screen = pygame.display.set_mode((initial_w, initial_h), pygame.RESIZABLE)
    content = pygame.Surface((WIDTH, CONTENT_HEIGHT))
    clock = pygame.time.Clock()

    # Tao font, khoi tao thuat toan mac dinh va danh sach nut theo mode hien tai.
    fonts = create_fonts()
    vis = SearchVisualizer(MAIN_START, MAIN_GOAL, mode=1)
    buttons = create_buttons(screen.get_width(), vis.mode)

    # Cac bien trang thai cua giao dien, khong nam trong SearchVisualizer.
    auto_run = False
    last_auto_tick = 0
    scroll_y = 0
    toolbar_scroll_x = 0
    dragging_scrollbar = False
    scrollbar_drag_offset = 0
    dragging_toolbar_scrollbar = False
    toolbar_scroll_drag_offset = 0
    selected_board = None
    selected_index = None

    running = True
    while running:
        # now dung de tinh khoang thoi gian giua cac buoc auto-run.
        now = pygame.time.get_ticks()
        view_w, view_h = screen.get_size()
        scroll_y = clamp_scroll(scroll_y, view_h)
        toolbar_scroll_x = max(0, min(toolbar_scroll_x, toolbar_scroll_limits(buttons, view_w)))

        # Doc toan bo event nguoi dung: dong cua so, resize, chuot, phim.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                # Khi resize, tao lai cua so va tao lai nut de can theo chieu rong moi.
                new_w = max(760, event.w)
                new_h = max(560, event.h)
                screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
                buttons = create_buttons(new_w, vis.mode)
                scroll_y = clamp_scroll(scroll_y, new_h)

            elif event.type == pygame.MOUSEWHEEL:
                # Lanh chuot de cuon noi dung doc.
                scroll_y = clamp_scroll(scroll_y - event.y * 45, screen.get_height())

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Xu ly click vao scrollbar truoc, vi scrollbar nam tren screen that.
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

                toolbar_track, toolbar_thumb = toolbar_scrollbar_geometry(buttons, screen.get_width(), toolbar_scroll_x)
                content_pos = (event.pos[0], event.pos[1] + scroll_y)
                if toolbar_thumb is not None and toolbar_thumb.collidepoint(content_pos):
                    dragging_toolbar_scrollbar = True
                    toolbar_scroll_drag_offset = content_pos[0] - toolbar_thumb.x
                    continue
                if toolbar_track is not None and toolbar_track.collidepoint(content_pos):
                    target_ratio = (content_pos[0] - toolbar_track.x) / max(1, toolbar_track.width)
                    max_toolbar_scroll = toolbar_scroll_limits(buttons, screen.get_width())
                    toolbar_scroll_x = max(0, min(int(target_ratio * max_toolbar_scroll), max_toolbar_scroll))
                    continue

                modes_button = create_modes_button(screen.get_width())
                if modes_button.clicked(content_pos):
                    clicked_button = "open_popup"
                else:
                    clicked_button = None

                # Doi toa do chuot tu cua so hien thi sang toa do cua content da cuon.
                pos = content_pos
                # Neu popup dang mo thi uu tien nut trong popup truoc cac nut ben duoi.
                if getattr(vis, "popup_visible", False):
                    popup_rect, popup_buttons = create_modes_popup(screen.get_width(), screen.get_height())
                    popup_rect.y += scroll_y
                    for pbtn in popup_buttons:
                        pbtn.rect.y += scroll_y
                        if pbtn.clicked(pos):
                            clicked_button = pbtn.action
                            break
                if clicked_button is None:
                    for button in buttons:
                        if button.clicked(pos, offset_x=toolbar_scroll_x):
                            clicked_button = button.action
                            break

                if clicked_button is not None:
                    if clicked_button == "auto":
                        # Chi cho auto-run khi bai toan san sang va chua ket thuc.
                        if vis.ready and not vis.found and not vis.failed:
                            auto_run = True
                            last_auto_tick = 0
                    else:
                        # Nut khac Auto se duoc xu ly trong handle_button.
                        old_mode = vis.mode
                        auto_run = False if handle_button(clicked_button, vis) else auto_run
                        # Neu doi mode/tab thi tao lai nut de hien dung trang thai active.
                        if clicked_button.startswith("tab_") or clicked_button.startswith("mode") or vis.mode != old_mode:
                            buttons = create_buttons(screen.get_width(), vis.mode)
                            scroll_y = clamp_scroll(scroll_y, screen.get_height())
                        if getattr(vis, "auto_start_requested", False):
                            auto_run = vis.ready and not vis.found and not vis.failed
                            vis.auto_start_requested = False
                            last_auto_tick = 0
                        # Khi nap lai test, bo chon o cu de tranh sua nham bang moi.
                        if clicked_button in ("easy", "main"):
                            selected_board = None
                            selected_index = None
                else:
                    # Neu khong bam nut, kiem tra xem co bam vao o tren START/GOAL khong.
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
                # Tha chuot thi ket thuc keo scrollbar.
                dragging_scrollbar = False
                dragging_toolbar_scrollbar = False

            elif event.type == pygame.MOUSEMOTION and dragging_scrollbar:
                # Cap nhat scroll_y theo vi tri thumb khi dang keo scrollbar.
                track, thumb = scrollbar_geometry(screen.get_width(), screen.get_height(), scroll_y)
                if track is not None and thumb is not None:
                    thumb_y = event.pos[1] - scrollbar_drag_offset
                    usable = max(1, track.height - thumb.height)
                    ratio = (thumb_y - track.y) / usable
                    scroll_y = clamp_scroll(int(ratio * (CONTENT_HEIGHT - screen.get_height())), screen.get_height())
            elif event.type == pygame.MOUSEMOTION and dragging_toolbar_scrollbar:
                toolbar_track, toolbar_thumb = toolbar_scrollbar_geometry(buttons, screen.get_width(), toolbar_scroll_x)
                if toolbar_track is not None and toolbar_thumb is not None:
                    thumb_x = event.pos[0] - toolbar_scroll_drag_offset
                    usable = max(1, toolbar_track.width - toolbar_thumb.width)
                    ratio = (thumb_x - toolbar_track.x) / usable
                    max_toolbar_scroll = toolbar_scroll_limits(buttons, screen.get_width())
                    toolbar_scroll_x = max(0, min(int(ratio * max_toolbar_scroll), max_toolbar_scroll))

            elif event.type == pygame.KEYDOWN:
                # Neu dang chon mot o trong START/GOAL va bam 0..8 thi sua bang.
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
                    # Space la phim tat cho Next Step.
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

        # Auto-run: chay tu tu tung buoc mot de de quan sat moi lan mo rong node.
        auto_delay = 500
        auto_steps = 1
        if auto_run and now - last_auto_tick >= auto_delay:
            for _ in range(auto_steps):
                vis.next_step(record_history=vis.mode in (1, 2))
                if vis.found or vis.failed:
                    break
            last_auto_tick = now
            if vis.found or vis.failed:
                auto_run = False

        # Ve lai toan bo giao dien len content, sau do cat phan dang xem len screen.
        mouse_x, mouse_y = pygame.mouse.get_pos()
        draw_ui(content, vis, buttons, fonts, selected_board, selected_index, auto_run,
                mouse_pos=(mouse_x, mouse_y + scroll_y),
                viewport_size=screen.get_size(), scroll_y=scroll_y,
                toolbar_scroll_x=toolbar_scroll_x)
        screen.fill(BG)
        screen.blit(content, (0, -scroll_y))
        draw_scrollbar(screen, scroll_y)
        pygame.display.flip()
        clock.tick(FPS)

    # Thoat khoi Pygame khi vong lap ket thuc.
    pygame.quit()


if __name__ == "__main__":
    main()
