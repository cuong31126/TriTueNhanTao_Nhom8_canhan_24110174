from collections import deque
import heapq
import random

from constants import GREEN, YELLOW
from puzzle import apply_move, is_solvable, is_valid_state, manhattan_distance, ordered_moves, valid_moves


class SpecialModesMixin:
    """Popup/special mode planning and replay behavior."""

    def _special_mode_name(self):
        """Ten ngan gon cua cac mode popup de hien trong status."""
        if self.mode == 14:
            return "Hidden Tiles Mode"
        if self.mode == 15:
            return "Blind Mode"
        if self.mode == 16:
            return "No Start/Goal Mode"
        if self.mode == 17:
            return "Simulated Local Search Mode"
        if self.mode == 18:
            return "AC-3 Mode"
        if self.mode == 19:
            return "Min-Conflicts Mode"
        if self.mode == 20:
            return "AND-OR Search"
        if self.mode == 21:
            return "Backtracking Search"
        if self.mode == 22:
            return "Forward Checking"
        return "Special Mode"

    def _prepare_plan_execution(self, label, request_auto=False, planner="astar"):
        """Lap duong di noi bo roi cho UI phat lai tung nuoc di.

        Hidden/Blind/No Start-Goal dung full state ben trong de giai, con UI co
        the che bot tile hoac an START/GOAL tuy theo mode.
        """
        if planner == "best_first":
            path = self._best_first_solve()
            planner_text = "greedy best-first"
        elif planner == "ac3":
            path = self._ac3_solve()
            planner_text = "AC-3 constraint plan"
        elif planner == "min_conflicts":
            path = self._min_conflicts_solve()
            planner_text = "Min-Conflicts local search plan"
        elif planner == "and_or":
            path = self._and_or_solve()
            planner_text = "AND-OR conditional search plan"
        elif planner == "backtracking":
            path = self._backtracking_solve()
            planner_text = "backtracking depth-first plan"
        elif planner == "forward_checking":
            path = self._forward_checking_solve()
            planner_text = "forward-checking CSP plan"
        else:
            path = self._astar_solve()
            planner_text = "internal A*"
        self.precomputed_index = 0
        self.precomputed_path = list(path) if path is not None else None
        if self.precomputed_path is None:
            self.ready = False
            self.failed = True
            self.status = label + ": " + planner_text + " could not find a solution."
            self._store_result()
            return

        self.queue = deque([(self.start, [])])
        self.reached = {self.start}
        self.frontier_count = 1
        self.status = (
            label
            + ": "
            + planner_text
            + " plan ready with "
            + str(len(self.precomputed_path))
            + " moves. Use Next/Auto to replay tile movement."
        )
        self.auto_start_requested = request_auto and len(self.precomputed_path) > 0
        if len(self.precomputed_path) == 0:
            self.solution_path = []
            self.found = True
            self.status = label + ": generated state is already solved."
            self._store_result()

    def _step_plan_execution(self):
        """Chay mot buoc trong duong di da lap san cho cac popup mode 14-17."""
        label = self._special_mode_name()
        if self.precomputed_path is None:
            self.failed = True
            self.status = label + ": no internal plan is available."
            self._store_result()
            return

        if self.precomputed_index >= len(self.precomputed_path):
            self.solution_path = list(self.precomputed_path)
            self.found = True
            self.status = label + ": replay completed."
            self._store_result()
            return

        action = self.precomputed_path[self.precomputed_index]
        old_state = self.current_state
        new_state = apply_move(old_state, action)
        old_h = manhattan_distance(old_state, self.goal, self.goal_pos)
        new_h = manhattan_distance(new_state, self.goal, self.goal_pos)

        self.precomputed_index += 1
        self.step += 1
        self.expanded += 1
        self.generated += 1
        self.current_state = new_state
        self.current_path = list(self.current_path) + [action]
        self.current_action = action
        self.tree_root_state = old_state
        self.tree_root_path = list(self.current_path[:-1])
        self.tree_focus_path = list(self.current_path)
        self.children_info = [{
            "state": new_state,
            "path": list(self.current_path),
            "action": action,
            "result": "MOVE " + str(self.precomputed_index) + "/" + str(len(self.precomputed_path))
                      + " h=" + str(int(new_h)),
            "color": GREEN if new_h <= old_h else YELLOW,
        }]
        self.queue = deque([(new_state, list(self.current_path))])
        self.frontier_count = 1
        self.reached.add(new_state)

        if new_state == self.goal:
            self.solution_path = list(self.current_path)
            self.found = True
            self.queue.clear()
            self.frontier_count = 0
            self.status = label + ": goal reached during replay."
            self._store_result()
            return

        self.status = (
            label
            + ": executed move "
            + str(self.precomputed_index)
            + "/"
            + str(len(self.precomputed_path))
            + "."
        )

    # --- Special mode helpers ---

    def _init_hidden_mode(self):
        """Hidden Tiles: an mot vai o tren UI, nhung solver van dung state day du."""
        choices = [i for i, value in enumerate(self.start) if value != 0]
        k = min(3, max(1, len(choices)))
        self.hidden_indices = set(random.sample(choices, k))

    def _generate_random_start_goal(self):
        """No Start/Goal: sinh START/GOAL hop le ben trong roi chuan bi replay."""
        attempts = 0
        while True:
            start = tuple(random.sample(range(9), 9))
            goal = tuple(random.sample(range(9), 9))
            attempts += 1
            if is_valid_state(start) and is_valid_state(goal) and is_solvable(start, goal):
                break
            if attempts > 1000:
                # Fallback to main preset if random generation fails.
                start, goal = self.start, self.goal
                break

        self.start = tuple(start)
        self.goal = tuple(goal)
        self.goal_pos = {value: index for index, value in enumerate(self.goal)}
        self.results = self._empty_results()
        self.reset_current_mode(request_auto=True)
        if self.ready and not self.failed:
            self.status = (
                "No Start/Goal Mode: random internal START/GOAL generated. "
                + "Plan length="
                + str(len(self.precomputed_path or []))
                + "."
            )

    def _astar_solve(self):
        """Run a simple A* to completion (no UI impact) and return the solution path or None."""
        import heapq
        start = self.start
        goal = self.goal
        frontier = []
        heapq.heappush(frontier, (manhattan_distance(start, goal, self.goal_pos), 0, start, []))
        reached = {start: 0}
        limit = 200000
        steps = 0
        while frontier and steps < limit:
            _, g, state, path = heapq.heappop(frontier)
            if state == goal:
                return path
            for action in ordered_moves(state, goal, self.goal_pos):
                child = apply_move(state, action)
                new_g = g + 1
                if child in reached and reached[child] <= new_g:
                    continue
                reached[child] = new_g
                h = manhattan_distance(child, goal, self.goal_pos)
                heapq.heappush(frontier, (new_g + h, new_g, child, path + [action]))
            steps += 1
        return None

    def _ac3_solve(self):
        """Apply AC-3 consistency propagation on a simple 8-puzzle CSP then solve by A*."""
        if self.start == self.goal:
            return []

        domains = {pos: set(range(9)) for pos in range(9)}
        for pos in range(9):
            if self.start[pos] == self.goal[pos]:
                domains[pos] = {self.start[pos]}

        self._ac3_enforce(domains)
        return self._astar_solve()

    def _ac3_enforce(self, domains):
        """Enforce arc consistency for a simple all-different CSP over board positions."""
        queue = [(xi, xj) for xi in domains for xj in domains if xi != xj]
        while queue:
            xi, xj = queue.pop(0)
            if self._revise(xi, xj, domains):
                if not domains[xi]:
                    return False
                for xk in domains:
                    if xk != xi and xk != xj:
                        queue.append((xk, xi))
        return True

    def _revise(self, xi, xj, domains):
        """Revise domains[xi] with respect to xi != xj."""
        revised = False
        if len(domains[xj]) == 1:
            value = next(iter(domains[xj]))
            if value in domains[xi]:
                domains[xi].remove(value)
                revised = True
        return revised

    def _min_conflicts_solve(self):
        """Solve by a min-conflicts style local-search on the 8-puzzle state."""
        if self.start == self.goal:
            return []

        start_state = self.start
        best_path = None
        best_score = float("inf")
        max_restarts = 6
        max_steps = 1200

        for restart in range(max_restarts):
            state = start_state if restart == 0 else self._random_restart_state(start_state)
            path = []
            current_score = self._conflict_score(state)
            if current_score < best_score:
                best_score = current_score
                best_path = list(path)

            for step in range(max_steps):
                if state == self.goal:
                    return path

                neighbors = []
                for action in valid_moves(state):
                    child = apply_move(state, action)
                    score = self._conflict_score(child)
                    neighbors.append((score, action, child))

                if not neighbors:
                    break

                neighbors.sort(key=lambda item: item[0])
                best_score_neighbor = neighbors[0][0]
                best_moves = [(action, child) for score, action, child in neighbors if score == best_score_neighbor]
                action, child = random.choice(best_moves)

                if best_score_neighbor <= current_score or random.random() < 0.25:
                    state = child
                    current_score = best_score_neighbor
                    path.append(action)
                else:
                    action, child = random.choice([(action, child) for _, action, child in neighbors])
                    state = child
                    current_score = self._conflict_score(state)
                    path.append(action)

                if current_score < best_score:
                    best_score = current_score
                    best_path = list(path)

                if len(path) > 500:
                    break

            if state == self.goal:
                return path

        return self._best_first_solve()

    def _random_restart_state(self, state):
        """Create a reachable state by taking a few random valid moves from the current state."""
        new_state = state
        for _ in range(12):
            action = random.choice(valid_moves(new_state))
            new_state = apply_move(new_state, action)
        return new_state

    def _conflict_score(self, state):
        """Compute a simple conflict score for the board: Manhattan distance plus misplaced tiles."""
        misplaced = sum(1 for index, value in enumerate(state) if value != 0 and value != self.goal[index])
        return manhattan_distance(state, self.goal, self.goal_pos) + misplaced

    def _best_first_solve(self):
        """Greedy best-first solve dung h=Manhattan de tao duong replay cho mode 17."""
        start = self.start
        goal = self.goal
        frontier = []
        tie = 0
        start_h = manhattan_distance(start, goal, self.goal_pos)
        heapq.heappush(frontier, (start_h, 0, tie, start, []))
        reached = {start}
        limit = 200000
        steps = 0

        while frontier and steps < limit:
            _h, depth, _tie, state, path = heapq.heappop(frontier)
            if state == goal:
                return path

            for action in ordered_moves(state, goal, self.goal_pos):
                child = apply_move(state, action)
                if child in reached:
                    continue
                reached.add(child)
                child_path = path + [action]
                child_h = manhattan_distance(child, goal, self.goal_pos)
                tie += 1
                heapq.heappush(frontier, (child_h, depth + 1, tie, child, child_path))

            steps += 1
        return None

    def _and_or_solve(self):
        """Build a simple conditional AND-OR plan for deterministic 8-puzzle transitions.

        OR nodes choose a move. AND outcomes represent the intended transition plus
        a conservative wait/no-change outcome. Because the normal 8-puzzle is
        deterministic, the executable replay follows the intended branch.
        """
        if self.start == self.goal:
            return []

        max_depth = 36
        memo = set()

        def or_search(state, depth, path, branch):
            if state == self.goal:
                return list(path)
            if depth >= max_depth:
                return None
            key = (state, depth)
            if key in memo:
                return None
            memo.add(key)

            for action in ordered_moves(state, self.goal, self.goal_pos):
                child = apply_move(state, action)
                if child in branch:
                    continue

                # AND node: all modeled outcomes must be acceptable. The no-change
                # outcome is acceptable because the next replay tick can retry.
                outcomes = [child, state]
                if all(outcome == state or outcome not in branch for outcome in outcomes):
                    result = or_search(child, depth + 1, path + [action], branch | {child})
                    if result is not None:
                        self.status = "AND-OR Search: conditional branch selected."
                        return result
            return None

        return or_search(self.start, 0, [], {self.start}) or self._astar_solve()

    def _backtracking_solve(self):
        """Solve the puzzle by recursive backtracking with depth deepening."""
        if self.start == self.goal:
            return []

        for depth_limit in range(manhattan_distance(self.start, self.goal, self.goal_pos), 40):
            result = self._backtrack_limited(self.start, depth_limit, [], {self.start}, forward_check=False)
            if result is not None:
                return result
        return self._astar_solve()

    def _forward_checking_solve(self):
        """Backtracking plus look-ahead pruning by Manhattan lower bound."""
        if self.start == self.goal:
            return []

        for depth_limit in range(manhattan_distance(self.start, self.goal, self.goal_pos), 40):
            result = self._backtrack_limited(self.start, depth_limit, [], {self.start}, forward_check=True)
            if result is not None:
                return result
        return self._astar_solve()

    def _backtrack_limited(self, state, depth_left, path, seen, forward_check=False):
        if state == self.goal:
            return list(path)
        if depth_left <= 0:
            return None

        h_cost = manhattan_distance(state, self.goal, self.goal_pos)
        if h_cost > depth_left:
            return None

        for action in ordered_moves(state, self.goal, self.goal_pos):
            child = apply_move(state, action)
            if child in seen:
                continue

            if forward_check:
                child_h = manhattan_distance(child, self.goal, self.goal_pos)
                if child_h > depth_left - 1:
                    continue
                if not is_solvable(child, self.goal):
                    continue

            result = self._backtrack_limited(
                child,
                depth_left - 1,
                path + [action],
                seen | {child},
                forward_check=forward_check,
            )
            if result is not None:
                return result
        return None

    # Tinh priority cho A*/Greedy dua tren g_cost va Manhattan h_cost.
