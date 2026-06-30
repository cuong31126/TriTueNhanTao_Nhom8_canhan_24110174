from constants import BOARD_N, TILES, MOVE_DELTAS # lấy các hằng số từ constant.py 


MOVE_LABELS = {
    "UP": "Len",
    "DOWN": "Xuong",
    "LEFT": "Trai",
    "RIGHT": "Phai",
}


def print_board(state):
    """In ban co ra console, huu ich khi can debug nhanh."""
    for r in range(BOARD_N):   # lặp qua dòng 0 ,1, 2 
        row = state[r * BOARD_N:(r + 1) * BOARD_N]  # cắt tuple 1 chiều thành từng hàng 
        print(row)
    print()

# hàm kt 1 board có hợp lệ ko 
def is_valid_state(state):
    return len(state) == 9 and tuple(sorted(state)) == TILES # có đúng 9 ô và sau khi sắp xếp đúng 0 1 2 3 4 5 6 7 8  

# trả về ds hướng đi hợp lệ của ô trống 
def valid_moves(state):
    """Tra ve cac huong ma o trong so 0 co the di chuyen."""
    zero = state.index(0) # tìm vt index ô trống 
    row, col = divmod(zero, BOARD_N) # đổi 1 chiều thành tọa độ hàng cột  vd 1 : 3  = 0 dư 1  vị trí 0 ,1 

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
# hàm tạo bỏad mới sau khi move ô trống theo action 
def apply_move(state, action):
    """Tao state moi sau khi di chuyen o trong theo action."""
    zero = state.index(0)  # tìm vị trí của ô trống 
    target = zero + MOVE_DELTAS[action] # tính vt sẽ đổi chỗ vs ô chống   move_deltas sẽ + 1 hoặc -1 hoặc +3 hoặc -3 tùy hướng đi 
    data = list(state) # chuyển tuple thành list để có thể sửa đổi
    data[zero], data[target] = data[target], data[zero] # đổi chỗ ô trống với ô mục tiêu
    return tuple(data)

# tính tổng khoảng cách mahatan từ state đến goal 
def manhattan_distance(state, goal, goal_pos=None):
    """Tinh tong khoang cach Manhattan giua state va goal."""
    if goal_pos is None:
        goal_pos = {value: index for index, value in enumerate(goal)}
    distance = 0 
    for index, value in enumerate(state):
        if value == 0:  # bỏ qua ô trống 0 
            continue
        target = goal_pos[value] # lấy tri dich 
        row, col = divmod(index, BOARD_N) # lay vi tri dich o hien tai 
        target_row, target_col = divmod(target, BOARD_N) # doi vi tri sang hang cot 
        distance += abs(row - target_row) + abs(col - target_col) # tinh kc 
    return distance

# trả về ds nc di dc sx theo muc do gan goal 
def ordered_moves(state, goal, goal_pos=None):
    """Sap xep nuoc di de DFS uu tien trang thai gan goal hon."""
    if goal_pos is None:
        goal_pos = {value: index for index, value in enumerate(goal)}
    return sorted(
        valid_moves(state),
        key=lambda action: (manhattan_distance(apply_move(state, action), goal, goal_pos), action),
    )

# đếm số inversion count giữa start và goal để kiểm tra tính giải được của bài toán 8-puzzle
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

# kt từ start có đi tới goal đc ko 
def is_solvable(start, goal):
    """
    Kiem tra giai duoc cho 8-puzzle 3x3 bang parity inversion tuong doi.
    Voi kich thuoc le 3x3, start giai duoc den goal khi inversion tuong doi la chan.
    """
    if not is_valid_state(start) or not is_valid_state(goal):
        return False
    return relative_inversion_count(start, goal) % 2 == 0


# rút gọn đg đi hiển thị 
def compact_path(path, max_items=10):
    if not path:
        return "[]"
    if len(path) <= max_items:
        return " -> ".join(path) # nếu các path ko quá dài , nối các action bằng --> 
    head = " -> ".join(path[:max_items])
    return head + " -> ... (+" + str(len(path) - max_items) + ")"


# chuyển path thành chuỗi hiển thị 
def path_text(path, translate=True):
    if path is None:
        return "-"
    if not path:
        return "[]"
    if translate:
        return " -> ".join(MOVE_LABELS.get(action, action) for action in path)
    return " -> ".join(path)

# tạo phiên bản rất ngắn của path , thường để vẽ trong UI nhỏ 
def tiny_path(path, max_items=6):
    if not path:
        return "[]"
    chunks = [item[0] for item in path[:max_items]]
    text = " ".join(chunks)
    if len(path) > max_items:
        text += " ..."
    return text

# chuyển board từ tuple sang list để chỉnh sửa 
def edit_board_value(board, index, value):
    """Gan so vao o dang chon; neu so da ton tai thi doi cho hai o."""
    data = list(board)
    old = data[index]
    other = data.index(value)
    data[index] = value
    if other != index:
        data[other] = old
    return tuple(data)
