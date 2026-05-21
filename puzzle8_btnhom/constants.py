WIDTH, HEIGHT = 1200, 800
CONTENT_HEIGHT = 1220
FPS = 60

BOARD_N = 3
TILES = tuple(range(9))

WHITE = (245, 247, 250)
BG = (24, 28, 35)
PANEL = (34, 40, 50)
PANEL_2 = (43, 50, 62)
GRID = (90, 100, 115)
TEXT = (235, 238, 244)
MUTED = (160, 168, 180)
BLUE = (70, 145, 255)
GREEN = (60, 190, 115)
RED = (230, 90, 90)
YELLOW = (235, 190, 70)
ORANGE = (245, 145, 65)
DARK_TILE = (18, 22, 28)
TILE = (230, 235, 242)
TILE_TEXT = (35, 42, 52)

MOVE_DELTAS = {
    "UP": -3,
    "DOWN": 3,
    "LEFT": -1,
    "RIGHT": 1,
}

MOVE_ORDER = ["UP", "DOWN", "LEFT", "RIGHT"]

EASY_START = (1, 2, 3,
              4, 5, 6,
              7, 0, 8)
EASY_GOAL = (1, 2, 3,
             4, 5, 6,
             7, 8, 0)

MAIN_START = (1, 2, 3,
              7, 6, 8,
              5, 4, 0)
MAIN_GOAL = (1, 2, 3,
             4, 5, 6,
             7, 8, 0)
