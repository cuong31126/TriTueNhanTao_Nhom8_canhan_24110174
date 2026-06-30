WIDTH, HEIGHT = 1200, 800 # kích thươc giao diện 
CONTENT_HEIGHT = 1220   # chiều cao tht cuẩ noi dung 
FPS = 60 # số frame mỗi giây  . 

BOARD_N = 3   
TILES = tuple(range(9))  # tạo tuple 0 1 2 3 4 5 6 7 8 

# màu sắc 
WHITE = (245, 247, 250)
BG = (24, 28, 35)
# màu nền chính ứng dụng 
PANEL = (34, 40, 50)
PANEL_2 = (43, 50, 62)
# màu nền cho khung panel trong giao diện 
GRID = (90, 100, 115)
# màu đg viền lưới bàn cờ 
TEXT = (235, 238, 244)
# màu chữ chính  
MUTED = (160, 168, 180)
# màu chữ phụ 
BLUE = (70, 145, 255)
# tab đang chọn 
GREEN = (60, 190, 115)
RED = (230, 90, 90)
YELLOW = (235, 190, 70)
ORANGE = (245, 145, 65)
DARK_TILE = (18, 22, 28)
TILE = (230, 235, 242)
TILE_TEXT = (35, 42, 52)

# màu chữ số trong ô 
# hướng di chuyển 
MOVE_DELTAS = {
    "UP": -3,
    "DOWN": 3,
    "LEFT": -1,
    "RIGHT": 1,
}

MOVE_ORDER = ["UP", "DOWN", "LEFT", "RIGHT"]

EASY_START = (1, 2, 3,
              4, 0, 6,
              7, 5, 8)
EASY_GOAL = (1, 2, 3,
             4, 5, 6,
             7, 8, 0)

MAIN_START = (1, 2, 3,
              7, 6, 8,
              5, 4, 0)
MAIN_GOAL = (1, 2, 3,
             4, 5, 6,
             7, 8, 0)
