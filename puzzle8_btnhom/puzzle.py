from constants import BOARD_N, TILES, MOVE_DELTAS


MOVE_LABELS = {
    "UP": "Len",
    "DOWN": "Xuong",
    "LEFT": "Trai",
    "RIGHT": "Phai",
}


def print_board(state):
    """In ban co ra console, huu ich khi can debug nhanh."""
    for r in range(BOARD_N):
        row = state[r * BOARD_N:(r + 1) * BOARD_N]
        print(row)
    print()


def is_valid_state(state):
    return len(state) == 9 and tuple(sorted(state)) == TILES


def valid_moves(state):
    """Tra ve cac huong ma o trong so 0 co the di chuyen."""
    zero = state.index(0)
    row, col = divmod(zero, BOARD_N)

    moves = []
    if row > 0:
        moves.append("UP")
    if row < BOARD_N - 1:
        moves.append("DOWN")
    if col > 0:
        moves.append("LEFT")
    if col < BOARD_N - 1:
        moves.append("RIGHT")
    return moves


def apply_move(state, action):
    """Tao state moi sau khi di chuyen o trong theo action."""
    zero = state.index(0)
    target = zero + MOVE_DELTAS[action]
    data = list(state)
    data[zero], data[target] = data[target], data[zero]
    return tuple(data)


def manhattan_distance(state, goal, goal_pos=None):
    """Tinh tong khoang cach Manhattan giua state va goal."""
    if goal_pos is None:
        goal_pos = {value: index for index, value in enumerate(goal)}
    distance = 0
    for index, value in enumerate(state):
        if value == 0:
            continue
        target = goal_pos[value]
        row, col = divmod(index, BOARD_N)
        target_row, target_col = divmod(target, BOARD_N)
        distance += abs(row - target_row) + abs(col - target_col)
    return distance


def ordered_moves(state, goal, goal_pos=None):
    """Sap xep nuoc di de DFS uu tien trang thai gan goal hon."""
    if goal_pos is None:
        goal_pos = {value: index for index, value in enumerate(goal)}
    return sorted(
        valid_moves(state),
        key=lambda action: (manhattan_distance(apply_move(state, action), goal, goal_pos), action),
    )


def relative_inversion_count(start, goal):
    """
    Dem inversion cua start theo thu tu xuat hien trong goal.
    Bo qua o trong 0. Cach nay dung duoc khi goal khong phai goal chuan.
    """
    order = {}
    rank = 0
    for tile in goal:
        if tile != 0:
            order[tile] = rank
            rank += 1

    seq = [order[tile] for tile in start if tile != 0]
    inv = 0
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            if seq[i] > seq[j]:
                inv += 1
    return inv


def is_solvable(start, goal):
    """
    Kiem tra giai duoc cho 8-puzzle 3x3 bang parity inversion tuong doi.
    Voi kich thuoc le 3x3, start giai duoc den goal khi inversion tuong doi la chan.
    """
    if not is_valid_state(start) or not is_valid_state(goal):
        return False
    return relative_inversion_count(start, goal) % 2 == 0


def compact_path(path, max_items=10):
    if not path:
        return "[]"
    if len(path) <= max_items:
        return " -> ".join(path)
    head = " -> ".join(path[:max_items])
    return head + " -> ... (+" + str(len(path) - max_items) + ")"


def path_text(path, translate=True):
    if path is None:
        return "-"
    if not path:
        return "[]"
    if translate:
        return " -> ".join(MOVE_LABELS.get(action, action) for action in path)
    return " -> ".join(path)


def tiny_path(path, max_items=6):
    if not path:
        return "[]"
    chunks = [item[0] for item in path[:max_items]]
    text = " ".join(chunks)
    if len(path) > max_items:
        text += " ..."
    return text


def edit_board_value(board, index, value):
    """Gan so vao o dang chon; neu so da ton tai thi doi cho hai o."""
    data = list(board)
    old = data[index]
    other = data.index(value)
    data[index] = value
    if other != index:
        data[other] = old
    return tuple(data)
