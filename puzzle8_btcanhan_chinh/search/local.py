import random

from constants import GREEN, RED, YELLOW
from puzzle import apply_move, manhattan_distance, valid_moves


class LocalSearchMixin:
    """Hill climbing and local beam search behavior."""

    def _make_random_restart(self):
        """Tao state restart bang random walk tu START va dua vao queue."""
        state = self.start
        path = []
        previous_state = None

        for _ in range(self.RANDOM_RESTART_WALK):
            moves = valid_moves(state)
            if previous_state is not None:
                filtered = [
                    action for action in moves
                    if apply_move(state, action) != previous_state
                ]
                if filtered:
                    moves = filtered

            action = random.choice(moves)
            previous_state = state
            state = apply_move(state, action)
            path.append(action)
            self.reached.add(state)

            if state == self.goal:
                break

        self.restart_count += 1
        self.queue.clear()
        self.queue.append((state, path))
        self.current_state = state
        self.current_path = list(path)
        self.current_action = path[-1] if path else "START"
        self.tree_root_state = state
        self.tree_root_path = list(path)
        self.tree_focus_path = list(path)
        return state, path

    # Chay mot buoc Hill Climbing hoac Steepest Hill Climbing.

    def _step_hill_climbing(self):
        """Hill Climbing: di sang neighbor co heuristic tot hon hien tai."""
        # Hill climbing chi giu mot state ke tiep trong queue.
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

        # h hien tai la Manhattan distance den goal.
        current_h = manhattan_distance(state, self.goal, self.goal_pos)
        if state == self.goal:
            self.solution_path = path
            self.found = True
            self.status = "Goal found by Hill Climbing. h=0."
            self._store_result()
            return

        # best_item se luu neighbor duoc chon de di tiep.
        best_item = None
        best_h = current_h
        moves = valid_moves(state)
        stochastic_items = []

        # Xet cac neighbor cua state hien tai.
        for action in moves:
            child = apply_move(state, action)
            child_path = path + [action]
            child_h = manhattan_distance(child, self.goal, self.goal_pos)
            self.generated += 1

            # Mac dinh child tot hon thi mau vang, khong tot hon thi mau do.
            item = {
                "state": child,
                "path": child_path,
                "action": action,
                "result": "h=" + str(int(child_h)),
                "color": YELLOW if child_h < current_h else RED,
            }
            self.children_info.append(item)

            if child == self.goal:
                # Gap goal thi chon ngay.
                item["result"] = "GOAL h=0"
                item["color"] = GREEN
                best_item = (child, child_path, action, child_h)
                break

            if self.mode == 9 and child_h < current_h:
                # First-improvement: gap neighbor dau tien tot hon la di ngay.
                item["result"] = "MOVE h=" + str(int(child_h))
                item["color"] = GREEN
                best_item = (child, child_path, action, child_h)
                break

            if self.mode == 11 and child_h < current_h:
                stochastic_items.append((child, child_path, action, child_h, item))

            if self.mode in (10, 12) and child_h < best_h:
                # Steepest-ascent: luu neighbor co h nho nhat trong tat ca neighbor.
                best_h = child_h
                best_item = (child, child_path, action, child_h)

        if self.mode == 11 and stochastic_items:
            child, child_path, action, child_h, chosen_item = random.choice(stochastic_items)
            chosen_item["result"] = "RANDOM h=" + str(int(child_h))
            chosen_item["color"] = GREEN
            best_item = (child, child_path, action, child_h)

        if self.mode in (10, 12) and best_item is not None and not self.found:
            # Sau khi xet het neighbor, danh dau neighbor tot nhat bang mau xanh.
            best_child, best_path, best_action, best_child_h = best_item
            for item in self.children_info:
                if item["state"] == best_child and item["action"] == best_action:
                    item["result"] = "BEST h=" + str(int(best_child_h))
                    item["color"] = GREEN
                elif item["color"] == YELLOW:
                    item["result"] = item["result"] + " OK"

        if best_item is None:
            if self.mode == 12 and self.restart_count < self.RANDOM_RESTART_LIMIT:
                # Random-restart: bi ket cuc tri cuc bo thi tao diem bat dau moi.
                restart_state, restart_path = self._make_random_restart()
                restart_h = manhattan_distance(restart_state, self.goal, self.goal_pos)
                self.status = (
                    "Random restart "
                    + str(self.restart_count)
                    + "/"
                    + str(self.RANDOM_RESTART_LIMIT)
                    + ": new h="
                    + str(int(restart_h))
                    + "."
                )
                if restart_state == self.goal:
                    self.solution_path = list(restart_path)
                    self.found = True
                    self.queue.clear()
                    self.status = "Goal found during random restart. h=0."
                    self._store_result()
                return

            # Khong co neighbor nao tot hon => ket o cuc tri cuc bo.
            self.failed = True
            self.queue.clear()
            self.status = (
                "Stopped at local optimum. No neighbor has smaller h than "
                + str(int(current_h))
                + "."
            )
            self._store_result()
            return

        # Di sang neighbor da chon.
        child, child_path, action, child_h = best_item
        self.current_state = child
        self.current_path = child_path
        self.current_action = action
        self.tree_focus_path = list(child_path)
        self.reached.add(child)

        if child == self.goal:
            # Neu neighbor la goal thi ket thuc thanh cong.
            self.solution_path = child_path
            self.found = True
            self.queue.clear()
            self.status = "Goal found by Hill Climbing. h=0."
            self._store_result()
            return

        # Chua den goal thi dua state moi vao queue de buoc sau tiep tuc leo.
        self.queue.append((child, child_path))
        if self.mode == 9:
            self.status = (
                "Moved to first better neighbor: h "
                + str(int(current_h))
                + " -> "
                + str(int(child_h))
                + "."
            )
        elif self.mode == 11:
            self.status = (
                "Moved to random better neighbor: h "
                + str(int(current_h))
                + " -> "
                + str(int(child_h))
                + "."
            )
        elif self.mode == 12:
            self.status = (
                "Random-restart hill climbing moved to best neighbor: h "
                + str(int(current_h))
                + " -> "
                + str(int(child_h))
                + "."
            )
        else:
            self.status = (
                "Moved to best neighbor: h "
                + str(int(current_h))
                + " -> "
                + str(int(child_h))
                + "."
            )

    # Chay mot buoc Local Beam Search.

    def _step_local_beam_search(self):
        """Local Beam Search: giu k state tot nhat sau moi lan sinh neighbor."""
        beam = list(self.queue)
        self.queue.clear()
        self.children_info = []
        self.step += 1

        if not beam:
            self.failed = True
            self.status = "No solution: beam is empty."
            self._store_result()
            return

        candidates = []
        best_parent_state, best_parent_path = min(
            beam,
            key=lambda item: manhattan_distance(item[0], self.goal, self.goal_pos),
        )
        self.current_state = best_parent_state
        self.current_path = list(best_parent_path)
        self.current_action = best_parent_path[-1] if best_parent_path else "START"
        self.tree_root_state = best_parent_state
        self.tree_root_path = list(best_parent_path)
        self.tree_focus_path = list(best_parent_path)

        for state, path in beam:
            self.expanded += 1
            if state == self.goal:
                self.solution_path = list(path)
                self.found = True
                self.current_state = state
                self.current_path = list(path)
                self.current_action = path[-1] if path else "START"
                self.status = "Goal found by Local Beam Search."
                self._store_result()
                return

            for action in valid_moves(state):
                child = apply_move(state, action)
                child_path = path + [action]
                child_h = manhattan_distance(child, self.goal, self.goal_pos)
                self.generated += 1

                if child == self.goal:
                    self.children_info.append({
                        "state": child,
                        "path": child_path,
                        "action": action,
                        "result": "GOAL h=0",
                        "color": GREEN,
                    })
                    self.current_state = child
                    self.current_path = child_path
                    self.current_action = action
                    self.tree_focus_path = list(child_path)
                    self.solution_path = child_path
                    self.found = True
                    self.status = "Goal found while generating beam child."
                    self._store_result()
                    return

                if child in self.reached:
                    if len(self.children_info) < 4:
                        self.children_info.append({
                            "state": child,
                            "path": child_path,
                            "action": action,
                            "result": "SKIP h=" + str(int(child_h)),
                            "color": RED,
                        })
                    continue

                candidates.append((child_h, child, child_path, action))
                if len(self.children_info) < 4:
                    self.children_info.append({
                        "state": child,
                        "path": child_path,
                        "action": action,
                        "result": "CAND h=" + str(int(child_h)),
                        "color": YELLOW,
                    })

        if not candidates:
            self.failed = True
            self.status = "Local Beam Search stopped: no new candidates."
            self._store_result()
            return

        candidates.sort(key=lambda item: (item[0], len(item[2]), item[3]))
        selected = candidates[:self.beam_width]
        for child_h, child, child_path, action in selected:
            self.queue.append((child, child_path))
            self.reached.add(child)

        best_h, best_state, best_path, _action = selected[0]
        self.current_state = best_state
        self.current_path = list(best_path)
        self.current_action = best_path[-1] if best_path else "START"
        self.tree_focus_path = list(best_path)
        selected_states = {item[1] for item in selected}
        for item in self.children_info:
            if item["state"] in selected_states and item["color"] == YELLOW:
                item["result"] = item["result"].replace("CAND", "BEAM")
                item["color"] = GREEN

        self.status = (
            "Local Beam kept "
            + str(len(selected))
            + " best states. Best h="
            + str(int(best_h))
            + "."
        )

    # Chay thuat toan den khi tim thay loi giai, that bai hoac cham limit.
