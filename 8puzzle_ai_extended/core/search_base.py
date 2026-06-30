class SearchEngine:
    def __init__(self, solver):
        self.solver = solver
        self.result = None

    def step(self):
        self.result = self.solver.step()
        return self.result