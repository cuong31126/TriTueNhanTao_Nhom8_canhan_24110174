from puzzle import valid_moves, apply_move, manhattan

class ForwardChecking:
    def __init__(self, start, goal):
        self.state = start
        self.goal = goal

    def step(self):
        moves = valid_moves(self.state)

        best = None
        best_h = 99999

        for m in moves:
            nxt = apply_move(self.state, m)
            h = manhattan(nxt, self.goal)

            if h < best_h:
                best_h = h
                best = m

        self.state = apply_move(self.state, best)