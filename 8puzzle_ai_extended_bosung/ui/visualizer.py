class Visualizer:
    def __init__(self, solver):
        self.solver = solver
        self.mode = "backtracking"

    def set_mode(self, mode):
        self.mode = mode

    def step(self):
        self.solver.step()

    @property
    def state(self):
        return self.solver.state