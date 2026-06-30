from config import BOARD_N

MOVE = {
    "UP": -3,
    "DOWN": 3,
    "LEFT": -1,
    "RIGHT": 1
}

def valid_moves(state):
    z = state.index(0)
    r, c = divmod(z, 3)

    moves = []
    if r > 0: moves.append("UP")
    if r < 2: moves.append("DOWN")
    if c > 0: moves.append("LEFT")
    if c < 2: moves.append("RIGHT")
    return moves


def apply_move(state, m):
    z = state.index(0)
    t = z + MOVE[m]

    s = list(state)
    s[z], s[t] = s[t], s[z]
    return tuple(s)


def manhattan(state, goal):
    pos = {v:i for i,v in enumerate(goal)}
    d = 0

    for i,v in enumerate(state):
        if v == 0:
            continue
        j = pos[v]
        d += abs(i//3 - j//3) + abs(i%3 - j%3)

    return d