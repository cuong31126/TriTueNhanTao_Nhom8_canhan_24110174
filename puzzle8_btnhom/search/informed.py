import heapq

from constants import RED, YELLOW
from puzzle import apply_move, manhattan_distance, ordered_moves


class InformedSearchMixin:
    """Priority-queue based A*/Greedy search behavior."""

    def _priority_for(self, state, g_cost):
        """Tinh priority cho heapq: Greedy dung h, A* dung g+h."""
        h_cost = manhattan_distance(state, self.goal, self.goal_pos)
        if self.mode == 6:
            return h_cost, h_cost
        return g_cost + h_cost, h_cost

    # Them state vao priority queue va cap nhat reached.

    def _push_priority(self, state, path, g_cost):
        """Them state vao priority queue va cap nhat reached voi chi phi g_cost."""
        priority, h_cost = self._priority_for(state, g_cost)
        heapq.heappush(self.queue, (priority, self.tie_breaker, g_cost, state, list(path)))
        self.tie_breaker += 1
        self.reached[state] = g_cost
        return priority, h_cost

    # Tao tap state tren mot path de phat hien cycle trong nhanh.

    def _step_mode_5(self):
        """Mot buoc cua A*/Greedy/Manhattan A*: lay node co priority nho nhat tu heap."""
        priority, _tie, g_cost, state, path = heapq.heappop(self.queue)

        # Neu heap con entry cu voi g_cost te hon gia tri reached hien tai thi bo qua.
        if self.reached.get(state, g_cost) < g_cost:
            self.status = "Skipped stale priority-queue entry."
            return

        # Cap nhat node dang mo rong.
        self.current_state = state
        self.current_path = path
        self.current_action = path[-1] if path else "START"
        self.tree_root_state = state
        self.tree_root_path = list(path)
        self.tree_focus_path = list(path)
        self.children_info = []
        self.step += 1
        self.expanded += 1

        # Priority search tra ve loi giai khi node goal duoc pop ra khoi heap.
        if state == self.goal:
            self.solution_path = path
            self.found = True
            if self.mode == 6:
                self.status = f"Goal found with Greedy Best-First. Path length = {g_cost}."
            elif self.mode == 7:
                self.status = f"Goal found with Manhattan A*. Path cost (g_cost) = {g_cost}."
            else:
                self.status = f"Goal found with A*. Path cost (g_cost) = {g_cost}."
            self._store_result()
            return

        # Sinh neighbor, tinh g moi va push vao heap neu tot hon duong da biet.
        for action in ordered_moves(state, self.goal, self.goal_pos):
            child = apply_move(state, action)
            child_path = path + [action]
            self.generated += 1
            new_g_cost = g_cost + 1

            if child in self.reached and self.reached[child] <= new_g_cost:
                # Da co duong den child ngan hon hoac bang, nen khong can push lai.
                self.children_info.append({
                    "state": child,
                    "path": child_path,
                    "action": action,
                    "result": "SKIP - SUBOPTIMAL",
                    "color": RED,
                })
                continue

            # A*/Greedy tinh priority trong _push_priority roi dua vao heap.
            new_priority, h_cost = self._push_priority(child, child_path, new_g_cost)
            if self.mode == 6:
                result = "ADD h=" + str(int(h_cost))
            else:
                result = "ADD f=" + str(int(new_priority)) + " h=" + str(int(h_cost))

            self.children_info.append({
                "state": child,
                "path": child_path,
                "action": action,
                "result": result,
                "color": YELLOW,
            })

        if self.mode == 6:
            self.status = "Expanded node with h=" + str(int(priority)) + ". Greedy uses h(n)."
        elif self.mode == 7:
            self.status = "Expanded node with f=" + str(int(priority)) + ". Manhattan A* uses f(n)=g(n)+h(n)."
        else:
            self.status = "Expanded node with f=" + str(int(priority)) + ". A* uses f(n)=g(n)+h(n)."

    # Chay mot buoc IDS voi depth limit hien tai.
