from puzzle import valid_moves, apply_move

class AndOr:
    def __init__(self, start, goal):
        self.state = start
        self.goal = goal

    def step(self):
        moves = valid_moves(self.state)
        self.state = apply_move(self.state, moves[-1])