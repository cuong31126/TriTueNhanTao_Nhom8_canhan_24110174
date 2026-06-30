from constants import GREEN, RED, YELLOW
from puzzle import apply_move, valid_moves


class BfsSearchMixin:
    """BFS mode implementations."""

    def _step_mode_1(self):
        """BFS Mode 1: kiem tra goal ngay khi sinh child, truoc khi enqueue."""
        # Lay node dau queue ra de mo rong.
        state, path = self.queue.popleft()

        # Cap nhat state hien tai de UI ve board, action va cay tim kiem.
        self.current_state = state
        self.current_path = path
        self.current_action = path[-1] if path else "START"
        self.tree_root_state = state
        self.tree_root_path = list(path)
        self.tree_focus_path = list(path)
        self.children_info = []
        self.step += 1
        self.expanded += 1

        # Sinh tat ca nuoc di hop le tu state hien tai.
        for action in valid_moves(state):
            child = apply_move(state, action)
            child_path = path + [action]
            self.generated += 1

            # Mode 1 gap goal khi sinh child la tra ve ngay, khong can dua vao queue.
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

            # Neu child da tung dat toi thi bo qua de tranh lap lai state.
            if child in self.reached:
                self.children_info.append({
                    "state": child,
                    "path": child_path,
                    "action": action,
                    "result": "SKIP - REACHED",
                    "color": RED,
                })
            else:
                # Child moi duoc dua vao queue de BFS xu ly sau.
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

    # Chay mot buoc BFS Mode 2: kiem tra goal khi dequeue.

    def _step_mode_2(self):
        """BFS Mode 2: chi kiem tra goal khi node duoc lay ra khoi queue."""
        # Lay node dau queue ra de mo rong.
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

        # Khac Mode 1: o day node vua dequeue moi duoc so sanh voi goal.
        if state == self.goal:
            self.solution_path = path
            self.found = True
            self.status = "Goal found after dequeue."
            self._store_result()
            return

        # Sinh child va dua vao queue neu chua reached.
        for action in valid_moves(state):
            child = apply_move(state, action)
            child_path = path + [action]
            self.generated += 1

            if child in self.reached:
                # Neu goal da reached truoc do thi van khong tra ve, vi Mode 2 doi den luc dequeue.
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
                    # Goal duoc sinh ra nhung chi duoc bao la se xu ly khi dequeue.
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

    # Chay mot buoc DFS thuong bang stack.
