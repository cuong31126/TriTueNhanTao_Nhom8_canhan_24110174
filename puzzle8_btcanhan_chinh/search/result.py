class ResultMixin:
    """Result metadata helpers for SearchVisualizer."""

    def _goal_method(self):
        """Mo ta cach mode hien tai kiem tra goal, dung trong bang ket qua."""
        if self.mode == 1:
            return "child generation"
        if self.mode == 2:
            return "dequeue"
        if self.mode == 3:
            return "stack pop"
        if self.mode == 4:
            return "depth-limited stack pop"
        if self.mode == 5:
            return "A* search"
        if self.mode == 6:
            return "greedy best-first search"
        if self.mode == 7:
            return "A* Manhattan heuristic"
        if self.mode == 8:
            return "iterative deepening search"
        if self.mode == 9:
            return "first-improvement hill climbing"
        if self.mode == 10:
            return "steepest-ascent hill climbing"
        if self.mode == 11:
            return "stochastic hill climbing"
        if self.mode == 12:
            return "random-restart hill climbing"
        if self.mode == 13:
            return "local beam search"
        if self.mode == 14:
            return "Hidden Tiles Mode: internal A* plan, obscured display"
        if self.mode == 15:
            return "Blind Mode: hidden start/goal, internal plan"
        if self.mode == 16:
            return "No Start/Goal Mode: generated internal boards"
        if self.mode == 17:
            return "Greedy best-first local-search simulation"
        if self.mode == 18:
            return "AC-3 mode with constraint propagation"
        if self.mode == 19:
            return "Min-Conflicts local search plan"
        if self.mode == 20:
            return "AND-OR conditional plan"
        if self.mode == 21:
            return "recursive backtracking"
        if self.mode == 22:
            return "forward checking with pruning"
        return "unknown"

    def _store_result(self):
        """Luu ket qua cua mode hien tai de UI hien thi va so sanh."""
        self.results[self.mode] = {
            "mode": self.mode,
            "path": list(self.solution_path) if self.solution_path is not None else None,
            "length": len(self.solution_path) if self.solution_path is not None else None,
            "expanded": self.expanded,
            "generated": self.generated,
            "queue": self.frontier_size(),
            "reached": len(self.reached),
            "method": self._goal_method(),
            "status": "found" if self.found else "failed",
        }

    # Chay dung mot buoc cua thuat toan dang chon.
