import pygame
import random
import sys
import time
import io

# Sửa lỗi mã hóa hiển thị tiếng Việt trên Terminal của Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- CẤU HÌNH GIAO DIỆN ---
WINDOW_WIDTH = 700  # Mở rộng màn hình sang phải để làm bảng phân tích
WINDOW_HEIGHT = 450
GRID_SIZE = 3
TILE_SIZE = 400 // GRID_SIZE
FPS = 30

# Màu sắc (Bảng màu tối giản, hiện đại)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (180, 180, 180)
BLUE = (52, 152, 219)
GREEN = (46, 204, 113)
ORANGE = (230, 126, 34)
TEXT_COLOR = (240, 240, 240)

# Trạng thái đích
GOAL = [1, 2, 3, 4, 5, 6, 7, 8, 0]

# --- HÀM LOGIC TOÁN HỌC & CSP ---

def get_conflicts(state):
    """Hàm Heuristic đếm số ô sai vị trí (Xung đột trạng thái đích)"""
    return sum(1 for i in range(len(state)) if state[i] != 0 and state[i] != GOAL[i])

def ac3_filter_moves(state):
    """
    Mô phỏng thuật toán AC-3 (Ràng buộc cung): 
    Lọc và chỉ giữ lại các cung (trạng thái kề) thỏa mãn ràng buộc di chuyển hợp lệ của ô trống.
    """
    valid_neighbors = []
    blank_idx = state.index(0)
    row, col = blank_idx // GRID_SIZE, blank_idx % GRID_SIZE
    
    # Ràng buộc vị trí hình học (Lên, Xuống, Trái, Phải)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        # Kiểm tra tính nhất quán của cung (Arc Consistency) với biên của bàn cờ
        if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
            new_idx = new_row * GRID_SIZE + new_col
            neighbor = list(state)
            neighbor[blank_idx], neighbor[new_idx] = neighbor[new_idx], neighbor[blank_idx]
            valid_neighbors.append(neighbor)
            
    return valid_neighbors

def min_conflicts_solver(state):
    """Thuật toán Min-Conflicts: Chọn nút có số lượng xung đột nhỏ nhất"""
    neighbors = ac3_filter_moves(state)
    if not neighbors:
        return state, neighbors
    
    min_c = min(get_conflicts(n) for n in neighbors)
    best_neighbors = [n for n in neighbors if get_conflicts(n) == min_c]
    
    # Trả về nút được chọn ngẫu nhiên trong nhóm tốt nhất và toàn bộ tập nút kề để phân tích
    return random.choice(best_neighbors), neighbors

def is_solvable(state):
    inversions = sum(1 for i in range(len(state)) for j in range(i + 1, len(state)) 
                     if state[i] != 0 and state[j] != 0 and state[i] > state[j])
    return inversions % 2 == 0

def generate_board():
    while True:
        state = list(GOAL)
        random.shuffle(state)
        if is_solvable(state) and state != GOAL:
            return state

# --- THÀNH PHẦN ĐỒ HỌA UI ---

class Button:
    def __init__(self, x, y, w, h, text, color, active_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.active_color = active_color
        self.is_active = False

    def draw(self, screen):
        cur_color = self.active_color if self.is_active else self.color
        pygame.draw.rect(screen, cur_color, self.rect, border_radius=6)
        font = pygame.font.SysFont("Segoe UI", 16, bold=True)
        txt = font.render(self.text, True, WHITE)
        screen.blit(txt, txt.get_rect(center=self.rect.center))

    def check_click(self, pos):
        return self.rect.collidepoint(pos)

def draw_sidebar(screen, mode, steps, conflicts, checked_nodes, current_state):
    """Vẽ bảng điều khiển và phân tích trạng thái ở bên phải screen"""
    sidebar_rect = pygame.Rect(410, 0, 290, WINDOW_HEIGHT)
    pygame.draw.rect(screen, DARK_GRAY, sidebar_rect)
    
    font_title = pygame.font.SysFont("Segoe UI", 18, bold=True)
    font_text = pygame.font.SysFont("Segoe UI", 14)
    font_code = pygame.font.SysFont("Consolas", 13)
    
    # 1. Thông tin thuật toán đang chạy
    screen.blit(font_title.render("THÔNG TIN GIẢI", True, ORANGE), (425, 20))
    screen.blit(font_text.render(f"Chế độ thuật toán: {mode}", True, TEXT_COLOR), (425, 50))
    screen.blit(font_text.render(f"Số bước đã đi: {steps}", True, TEXT_COLOR), (425, 75))
    screen.blit(font_text.render(f"Số xung đột hiện tại: {conflicts}", True, TEXT_COLOR), (425, 100))
    
    # 2. Phân tích Node (Cấu trúc dữ liệu trạng thái kề)
    screen.blit(font_title.render("PHÂN TÍCH NODE KỀ (CSP)", True, BLUE), (425, 140))
    screen.blit(font_text.render(f"Tổng số Node kề hợp lệ: {len(checked_nodes)}", True, TEXT_COLOR), (425, 170))
    
    y_offset = 200
    for idx, node in enumerate(checked_nodes[:4]): # Hiển thị tối đa 4 node kề để tránh tràn màn hình
        c_val = get_conflicts(node)
        node_str = "".join(str(x) for x in node).replace('0', '_')
        txt = f"Node {idx+1}: [{node_str}] -> Conflicts: {c_val}"
        screen.blit(font_code.render(txt, True, LIGHT_GRAY), (425, y_offset))
        y_offset += 22
        
    # 3. Trạng thái mảng hiện tại
    screen.blit(font_title.render("TRẠNG THÁI MẢNG LƯU TRỮ", True, GREEN), (425, 310))
    state_str = "State Array: " + str(current_state)
    screen.blit(font_code.render(state_str, True, LIGHT_GRAY), (425, 340))

def draw_board(screen, state):
    for i, tile in enumerate(state):
        if tile != 0:
            row, col = i // GRID_SIZE, i % GRID_SIZE
            rect = pygame.Rect(col * TILE_SIZE + 8, row * TILE_SIZE + 8, TILE_SIZE - 16, TILE_SIZE - 16)
            color = GREEN if tile == GOAL[i] else BLUE
            pygame.draw.rect(screen, color, rect, border_radius=10)
            
            font = pygame.font.SysFont("Arial", 36, bold=True)
            text_surface = font.render(str(tile), True, WHITE)
            screen.blit(text_surface, text_surface.get_rect(center=rect.center))

# --- HÀM CHÍNH ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("8-Puzzle CSP Analyzer (Min-Conflicts & AC-3)")
    clock = pygame.time.Clock()

    # Khởi tạo các nút chức năng
    btn_minconflict = Button(425, 380, 120, 40, "Min-Conflicts", DARK_GRAY, ORANGE)
    btn_ac3 = Button(555, 380, 120, 40, "AC-3 + MC", DARK_GRAY, GREEN)
    btn_minconflict.is_active = True  # Mặc định bật chế độ 1
    
    current_state = generate_board()
    neighbors_list = ac3_filter_moves(current_state)
    
    mode = "Min-Conflicts"
    ai_running = False
    step_count = 0
    max_steps = 400

    while True:
        pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_minconflict.check_click(pos):
                    btn_minconflict.is_active = True
                    btn_ac3.is_active = False
                    mode = "Min-Conflicts"
                    
                if btn_ac3.check_click(pos):
                    btn_minconflict.is_active = False
                    btn_ac3.is_active = True
                    mode = "AC-3 + Min-Conflicts"
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Bấm Space để chạy/dừng AI
                    ai_running = not ai_running
                if event.key == pygame.K_r:      # Bấm R để làm mới cấu hình mảng
                    current_state = generate_board()
                    neighbors_list = ac3_filter_moves(current_state)
                    step_count = 0
                    ai_running = False

        # Vòng lặp giải bài toán của AI
        if ai_running and current_state != GOAL and step_count < max_steps:
            if mode == "Min-Conflicts":
                # Bản chất sinh node kề thông thường
                current_state, neighbors_list = min_conflicts_solver(current_state)
            else:
                # Chế độ kết hợp: Dùng tư duy cấu trúc AC-3 để kiểm tra lọc thô các cung hợp lệ trước
                neighbors_list = ac3_filter_moves(current_state)
                current_state, _ = min_conflicts_solver(current_state)
                
            step_count += 1
            time.sleep(0.15)  # Trễ nhẹ để quan sát biến động Node trên bảng phân tích
            
            if current_state == GOAL:
                ai_running = False

        # --- VẼ GIAO DIỆN ---
        screen.fill(BLACK)
        draw_board(screen, current_state)
        
        # Vẽ bảng phân tích dữ liệu động bên tay phải
        draw_sidebar(screen, mode, step_count, get_conflicts(current_state), neighbors_list, current_state)
        
        # Vẽ các nút chuyển chế độ
        btn_minconflict.draw(screen)
        btn_ac3.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()