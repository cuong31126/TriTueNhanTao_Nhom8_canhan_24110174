from collections import deque
from copy import deepcopy

from constants import GREEN, RED, YELLOW
from puzzle import apply_move, is_solvable, is_valid_state, ordered_moves, valid_moves


class SearchVisualizer:
    """Quan ly BFS, DFS va DFS gioi han chieu sau cho 8-puzzle."""
    HISTORY_LIMIT = 300
    DEFAULT_DFS_DEPTH = 20
    DFS_STEP_LIMIT = 200000
    FRONTIER_PREVIEW_LIMIT = 80

    def __init__(self, start, goal, mode=1):
        self.start = tuple(start)
        self.goal = tuple(goal)
        self.goal_pos = {value: index for index, value in enumerate(self.goal)}
        self.mode = mode
        self.bfs_mode = mode if mode in (1, 2) else 1
        self.depth_limit = self.DEFAULT_DFS_DEPTH
        self.results = {1: None, 2: None, 3: None, 4: None}
        self.history = []
        self.reset_run(keep_results=True)

    def update_puzzle(self, start, goal):
        self.start = tuple(start)
        self.goal = tuple(goal)
        self.goal_pos = {value: index for index, value in enumerate(self.goal)}
        self.results = {1: None, 2: None, 3: None, 4: None}
        self.reset_run(keep_results=True)

    def set_mode(self, mode):
        self.mode = mode
        if mode in (1, 2):
            self.bfs_mode = mode
        self.reset_run(keep_results=True)

    def reset_run(self, keep_results=True):
        if not keep_results:
            self.results = {1: None, 2: None, 3: None, 4: None}

        self.history = []
        self.queue = deque()
        self.frontier_count = None
        self.reached = set()
        self.children_info = []
        self.step = 0
        self.expanded = 0
        self.generated = 0
        self.current_state = self.start
        self.current_path = []
        self.current_action = "START"
        self.solution_path = None
        self.found = False
        self.failed = False
        self.ready = True
        self.tree_root_state = self.start
        self.tree_root_path = []
        self.tree_focus_path = []

        if not is_valid_state(self.start) or not is_valid_state(self.goal):
            self.ready = False
            self.failed = True
            self.status = "Invalid board: Start and Goal must contain 0..8 exactly once."
            return

        if not is_solvable(self.start, self.goal):
            self.ready = False
            self.failed = True
            self.status = "Unsolvable: relative inversion parity does not match this goal."
            return

        self.queue.append((self.start, []))
        self.reached.add(self.start)
        self.status = "Ready. Press Next Step, Auto Run, or Solve Full."

        if self.start == self.goal:
            self.found = True
            self.solution_path = []
            self.status = "Start is already the goal. Solution length = 0."
            self._store_result()

    def _goal_method(self):
        if self.mode == 1:
            return "child generation"
        if self.mode == 2:
            return "dequeue"
        if self.mode == 3:
            return "stack pop"
        return "depth-limited stack pop"

    def _make_snapshot(self):
        return {
            "queue": deque((state, list(path)) for state, path in self.queue),
            "frontier_count": self.frontier_count,
            "reached": set(self.reached),
            "children_info": deepcopy(self.children_info),
            "step": self.step,
            "expanded": self.expanded,
            "generated": self.generated,
            "current_state": self.current_state,
            "current_path": list(self.current_path),
            "current_action": self.current_action,
            "solution_path": list(self.solution_path) if self.solution_path is not None else None,
            "found": self.found,
            "failed": self.failed,
            "ready": self.ready,
            "status": self.status,
            "results": deepcopy(self.results),
            "tree_root_state": self.tree_root_state,
            "tree_root_path": list(self.tree_root_path),
            "tree_focus_path": list(self.tree_focus_path),
        }

    def _restore_snapshot(self, snapshot):
        self.queue = deque((state, list(path)) for state, path in snapshot["queue"])
        self.frontier_count = snapshot.get("frontier_count")
        self.reached = set(snapshot["reached"])
        self.children_info = deepcopy(snapshot["children_info"])
        self.step = snapshot["step"]
        self.expanded = snapshot["expanded"]
        self.generated = snapshot["generated"]
        self.current_state = snapshot["current_state"]
        self.current_path = list(snapshot["current_path"])
        self.current_action = snapshot["current_action"]
        self.solution_path = (
            list(snapshot["solution_path"]) if snapshot["solution_path"] is not None else None
        )
        self.found = snapshot["found"]
        self.failed = snapshot["failed"]
        self.ready = snapshot["ready"]
        self.status = snapshot["status"]
        self.results = deepcopy(snapshot["results"])
        self.tree_root_state = snapshot["tree_root_state"]
        self.tree_root_path = list(snapshot["tree_root_path"])
        self.tree_focus_path = list(snapshot["tree_focus_path"])

    def _push_history(self):
        self.history.append(self._make_snapshot())
        if len(self.history) > self.HISTORY_LIMIT:
            self.history.pop(0)

    def can_go_back(self):
        return len(self.history) > 0

    def frontier_size(self):
        if self.frontier_count is not None:
            return self.frontier_count
        return len(self.queue)

    def previous_step(self):
        if not self.history:
            return

        self._restore_snapshot(self.history.pop())
        self.status = "Went back one step. " + self.status

    def _store_result(self):
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

    def next_step(self, record_history=True):
        """Chay mot buoc thi thuc cua thuat toan duoc chon."""
        if not self.ready or self.found or self.failed:
            return

        if self.mode in (3, 4) and self.expanded >= self.DFS_STEP_LIMIT:
            self.failed = True
            self.status = (
                "Stopped: DFS step limit reached. No solution reported within "
                + str(self.DFS_STEP_LIMIT)
                + " expanded nodes."
            )
            self._store_result()
            return

        if record_history:
            self._push_history()

        if not self.queue:
            self.failed = True
            if self.mode == 4:
                self.status = "No solution found within depth limit " + str(self.depth_limit) + "."
            else:
                self.status = "No solution: frontier is empty."
            self._store_result()
            return

        if self.mode == 1:
            self._step_mode_1()
        elif self.mode == 2:
            self._step_mode_2()
        elif self.mode == 3:
            self._step_mode_3()
        else:
            self._step_mode_4()

    def _step_mode_1(self):
        state, path = self.queue.popleft()
        self.current_state = state
        self.current_path = path
        self.current_action = path[-1] if path else "START"
        self.tree_root_state = state
        self.tree_root_path = list(path)
        self.tree_focus_path = list(path)
        self.children_info = []
        self.step += 1
        self.expanded += 1

        for action in valid_moves(state):
            child = apply_move(state, action)
            child_path = path + [action]
            self.generated += 1

            if child == self.goal:
                self.children_info.append({
                    "state": child,
                    "path": child_path,
                    "action": action,
                    "result": "GOAL - RETURN",
                    "color": GREEN,
                })
                self.current_state = child
                self.current_path = child_path
                self.current_action = action
                self.tree_focus_path = list(child_path)
                self.solution_path = child_path
                self.found = True
                self.status = "Goal found while generating child. Return immediately."
                self._store_result()
                return

            if child in self.reached:
                self.children_info.append({
                    "state": child,
                    "path": child_path,
                    "action": action,
                    "result": "SKIP - REACHED",
                    "color": RED,
                })
            else:
                self.reached.add(child)
                self.queue.append((child, child_path))
                self.children_info.append({
                    "state": child,
                    "path": child_path,
                    "action": action,
                    "result": "ADD TO QUEUE",
                    "color": YELLOW,
                })

        self.status = "Expanded one parent. Mode 1 checks each child before enqueue."

    def _step_mode_2(self):
        state, path = self.queue.popleft()
        self.current_state = state
        self.current_path = path
        self.current_action = path[-1] if path else "START"
        self.tree_root_state = state
        self.tree_root_path = list(path)
        self.tree_focus_path = list(path)
        self.children_info = []
        self.step += 1
        self.expanded += 1

        if state == self.goal:
            self.solution_path = path
            self.found = True
            self.status = "Goal found after dequeue."
            self._store_result()
            return

        for action in valid_moves(state):
            child = apply_move(state, action)
            child_path = path + [action]
            self.generated += 1

            if child in self.reached:
                color = GREEN if child == self.goal else RED
                result = "SKIP GOAL - REACHED" if child == self.goal else "SKIP - REACHED"
                self.children_info.append({
                    "state": child,
                    "path": child_path,
                    "action": action,
                    "result": result,
                    "color": color,
                })
            else:
                self.reached.add(child)
                self.queue.append((child, child_path))
                if child == self.goal:
                    result = "GOAL -> QUEUE"
                    color = GREEN
                    self.status = "Goal generated but Mode 2 waits until it is dequeued."
                    self.tree_focus_path = list(child_path)
                else:
                    result = "ADD TO QUEUE"
                    color = YELLOW
                self.children_info.append({
                    "state": child,
                    "path": child_path,
                    "action": action,
                    "result": result,
                    "color": color,
                })

        if not self.children_info:
            self.status = "Expanded one parent. No valid children."
        elif "Goal generated" not in self.status:
            self.status = "Expanded one parent. Mode 2 checks goal only after dequeue."

    def _step_mode_3(self):
        state, path = self.queue.pop()
        self.current_state = state
        self.current_path = path
        self.current_action = path[-1] if path else "START"
        self.tree_root_state = state
        self.tree_root_path = list(path)
        self.tree_focus_path = list(path)
        self.children_info = []
        self.step += 1
        self.expanded += 1

        if state == self.goal:
            self.solution_path = path
            self.found = True
            self.status = "Goal found when popping from stack."
            self._store_result()
            return

        for action in reversed(ordered_moves(state, self.goal, self.goal_pos)):
            child = apply_move(state, action)
            child_path = path + [action]
            self.generated += 1

            if child == self.goal:
                self.children_info.append({
                    "state": child,
                    "path": child_path,
                    "action": action,
                    "result": "GOAL - RETURN",
                    "color": GREEN,
                })
                self.current_state = child
                self.current_path = child_path
                self.current_action = action
                self.tree_focus_path = list(child_path)
                self.solution_path = child_path
                self.found = True
                self.status = "Goal found while generating child in DFS."
                self._store_result()
                return

            if child in self.reached:
                self.children_info.append({
                    "state": child,
                    "path": child_path,
                    "action": action,
                    "result": "SKIP - REACHED",
                    "color": RED,
                })
            else:
                self.reached.add(child)
                self.queue.append((child, child_path))
                self.children_info.append({
                    "state": child,
                    "path": child_path,
                    "action": action,
                    "result": "PUSH TO STACK",
                    "color": YELLOW,
                })

        self.status = "Expanded one node. DFS pushes children onto stack."

    def _step_mode_4(self):
        state, path = self.queue.pop()
        self.current_state = state
        self.current_path = path
        self.current_action = path[-1] if path else "START"
        self.tree_root_state = state
        self.tree_root_path = list(path)
        self.tree_focus_path = list(path)
        self.children_info = []
        self.step += 1
        self.expanded += 1

        if state == self.goal:
            self.solution_path = path
            self.found = True
            self.status = "Goal found when popping from stack."
            self._store_result()
            return

        if len(path) >= self.depth_limit:
            self.status = f"Depth limit reached ({self.depth_limit}) for this branch."
            return

        for action in reversed(ordered_moves(state, self.goal, self.goal_pos)):
            child = apply_move(state, action)
            child_path = path + [action]
            self.generated += 1

            if child == self.goal:
                self.children_info.append({
                    "state": child,
                    "path": child_path,
                    "action": action,
                    "result": "GOAL - RETURN",
                    "color": GREEN,
                })
                self.current_state = child
                self.current_path = child_path
                self.current_action = action
                self.tree_focus_path = list(child_path)
                self.solution_path = child_path
                self.found = True
                self.status = "Goal found while generating child in depth-limited DFS."
                self._store_result()
                return

            if child in self.reached:
                self.children_info.append({
                    "state": child,
                    "path": child_path,
                    "action": action,
                    "result": "SKIP - REACHED",
                    "color": RED,
                })
            else:
                self.reached.add(child)
                self.queue.append((child, child_path))
                self.children_info.append({
                    "state": child,
                    "path": child_path,
                    "action": action,
                    "result": "PUSH TO STACK",
                    "color": YELLOW,
                })

        self.status = "Expanded one node. Depth-limited DFS pushes children onto stack."

    def solve_full(self, limit=200000):
        """Chay thuat toan hien tai den khi tim thay loi giai hoac dung lai."""
        if self.ready and not self.found and not self.failed:
            self._push_history()

        if self.mode in (3, 4):
            self._solve_dfs_fast(min(limit, self.DFS_STEP_LIMIT))
            return

        count = 0
        while self.ready and not self.found and not self.failed and count < limit:
            self.next_step(record_history=False)
            count += 1

        if count >= limit and not self.found:
            self.failed = True
            self.status = "Stopped: step limit reached."
            self._store_result()

    def _path_from_parent(self, parent, state):
        path = []
        while state in parent and parent[state][0] is not None:
            previous, action = parent[state]
            path.append(action)
            state = previous
        path.reverse()
        return path

    def _frontier_preview(self, stack, parent):
        preview_states = stack[-self.FRONTIER_PREVIEW_LIMIT:]
        return deque((state, self._path_from_parent(parent, state)) for state in preview_states)

    def _solve_dfs_fast(self, limit):
        if not self.ready or self.found or self.failed:
            return

        depth_limit = self.depth_limit if self.mode == 4 else None
        parent = {self.start: (None, None)}
        depth = {self.start: 0}
        stack = []
        for state, path in self.queue:
            stack.append(state)
            cursor = self.start
            for action in path:
                child = apply_move(cursor, action)
                if child not in parent:
                    parent[child] = (cursor, action)
                    depth[child] = depth[cursor] + 1
                cursor = child
            depth[state] = len(path)

        reached = set(self.reached) if self.reached else {self.start}
        expanded = 0
        generated = 0
        last_state = self.current_state
        last_children = []

        while stack and expanded < limit:
            state = stack.pop()
            last_state = state
            current_depth = depth[state]
            expanded += 1

            if state == self.goal:
                self.current_state = state
                self.current_path = self._path_from_parent(parent, state)
                self.current_action = self.current_path[-1] if self.current_path else "START"
                self.solution_path = list(self.current_path)
                self.found = True
                self.status = "Goal found by fast DFS solve."
                break

            last_children = []
            if depth_limit is not None and current_depth >= depth_limit:
                continue

            candidates = []
            for action in ordered_moves(state, self.goal, self.goal_pos):
                child = apply_move(state, action)
                generated += 1

                if child in reached:
                    last_children.append({
                        "state": child,
                        "parent": state,
                        "action": action,
                        "result": "SKIP - REACHED",
                        "color": RED,
                    })
                    continue

                reached.add(child)
                parent[child] = (state, action)
                depth[child] = current_depth + 1
                candidates.append((action, child))
                last_children.append({
                    "state": child,
                    "parent": state,
                    "action": action,
                    "result": "PUSH TO STACK",
                    "color": YELLOW,
                })

            for action, child in reversed(candidates):
                stack.append(child)

        self.step += expanded
        self.expanded += expanded
        self.generated += generated
        self.reached = reached
        self.children_info = []
        for item in last_children[:4]:
            parent_state = item.pop("parent")
            item["path"] = self._path_from_parent(parent, parent_state) + [item["action"]]
            self.children_info.append(item)
        self.queue = self._frontier_preview(stack, parent)
        self.frontier_count = len(stack)

        if not self.found:
            self.current_state = last_state
            self.current_path = self._path_from_parent(parent, last_state)
            self.current_action = self.current_path[-1] if self.current_path else "START"
            self.failed = True
            if expanded >= limit:
                self.status = (
                    "Stopped: DFS step limit reached. No solution reported within "
                    + str(limit)
                    + " expanded nodes."
                )
            elif self.mode == 4:
                self.status = "No solution found within depth limit " + str(self.depth_limit) + "."
            else:
                self.status = "No solution: frontier is empty."

        self.tree_root_state = self.current_state
        self.tree_root_path = list(self.current_path)
        self.tree_focus_path = list(self.solution_path or self.current_path)
        self._store_result()
