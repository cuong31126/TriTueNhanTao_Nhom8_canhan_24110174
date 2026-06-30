from collections import deque

from constants import GREEN, RED, YELLOW
from puzzle import apply_move, ordered_moves


class DfsSearchMixin:
    """DFS, depth-limited DFS, and IDS behavior."""

    def _path_states(self, path):
        """Tao tap cac state nam tren path, dung de IDS tranh lap chu trinh trong nhanh."""
        states = {self.start}
        state = self.start
        for action in path:
            state = apply_move(state, action)
            states.add(state)
        return states

    # Bat dau vong lap IDS tiep theo voi depth limit lon hon.

    def _start_next_ids_iteration(self):
        """Tang depth limit cua IDS va khoi tao stack cho vong lap do sau moi."""
        if self.ids_depth_limit >= self.ids_max_depth:
            self.failed = True
            self.status = (
                "No solution found by IDS up to depth "
                + str(self.ids_max_depth)
                + "."
            )
            self._store_result()
            return False

        self.ids_depth_limit += 1
        self.queue = deque([(self.start, [])])
        self.frontier_count = None
        self.status = "IDS increased depth limit to " + str(self.ids_depth_limit) + "."
        return True

    # Chup snapshot day du de co the quay lai bang Prev Step.

    def _step_mode_3(self):
        """DFS thuong: dung stack, mo rong theo chieu sau."""
        # pop lay phan tu tren dinh stack.
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

        # DFS nay cung kiem tra goal khi pop, va ben duoi con kiem tra khi sinh child.
        if state == self.goal:
            self.solution_path = path
            self.found = True
            self.status = "Goal found when popping from stack."
            self._store_result()
            return

        # ordered_moves uu tien huong co Manhattan nho hon; reversed de khi push vao stack,
        # phan tu uu tien cao se nam tren dinh stack va duoc pop truoc.
        for action in reversed(ordered_moves(state, self.goal, self.goal_pos)):
            child = apply_move(state, action)
            child_path = path + [action]
            self.generated += 1

            # Gap goal khi sinh child thi dung ngay de UI thay duoc child goal.
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
                # State da di qua thi khong push lai.
                self.children_info.append({
                    "state": child,
                    "path": child_path,
                    "action": action,
                    "result": "SKIP - REACHED",
                    "color": RED,
                })
            else:
                # State moi duoc push len stack.
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

    # Chay mot buoc DFS co gioi han do sau.

    def _step_mode_4(self):
        """DFS co gioi han do sau: giong DFS nhung khong sinh con khi cham depth_limit."""
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

        # Neu path da dai bang gioi han, nhanh nay dung lai.
        if len(path) >= self.depth_limit:
            self.status = f"Depth limit reached ({self.depth_limit}) for this branch."
            return

        # Sinh con nhu DFS thuong, nhung chi khi chua vuot depth_limit.
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

    # Chay mot buoc A*/Greedy/Manhattan A* bang priority queue.

    def _step_mode_8(self):
        """IDS: DFS lap sau dan, moi lan chi di toi ids_depth_limit hien tai."""
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

        # IDS tim goal khi pop node ra khoi stack.
        if state == self.goal:
            self.solution_path = path
            self.found = True
            self.status = "Goal found by IDS at depth " + str(len(path)) + "."
            self._store_result()
            return

        # Cham gioi han do sau cua lan lap hien tai thi khong sinh con.
        if len(path) >= self.ids_depth_limit:
            self.status = (
                "IDS depth limit "
                + str(self.ids_depth_limit)
                + " reached for this branch."
            )
            if not self.queue:
                self.status += " Next step starts the next depth."
            return

        # Chi can tranh cycle tren nhanh hien tai, khong can reached toan cuc nhu DFS thuong.
        path_states = self._path_states(path)
        for action in reversed(ordered_moves(state, self.goal, self.goal_pos)):
            child = apply_move(state, action)
            child_path = path + [action]
            self.generated += 1

            if child in path_states:
                # Neu child da nam tren path hien tai thi bo qua de tranh lap vo han.
                self.children_info.append({
                    "state": child,
                    "path": child_path,
                    "action": action,
                    "result": "SKIP - CYCLE",
                    "color": RED,
                })
                continue

            # Gap goal khi sinh child thi dung ngay.
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
                self.status = "Goal found while generating child in IDS."
                self._store_result()
                return

            # Child hop le duoc push vao stack cho lan lap do sau hien tai.
            self.reached.add(child)
            self.queue.append((child, child_path))
            self.children_info.append({
                "state": child,
                "path": child_path,
                "action": action,
                "result": "PUSH TO STACK",
                "color": YELLOW,
            })

        self.status = "Expanded IDS node at limit " + str(self.ids_depth_limit) + "."
        if not self.queue:
            self.status += " Next step starts the next depth."

    def _solve_ids_fast(self, limit):
        """Chay IDS nhanh den khi tim thay goal hoac cham limit, chi giu preview cho UI."""
        if not self.ready or self.found or self.failed:
            return

        # Copy trang thai hien tai ra bien cuc bo de xu ly nhanh.
        stack = list(self.queue)
        reached = set(self.reached) if self.reached else {self.start}
        expanded = 0
        generated = 0
        last_state = self.current_state
        last_path = list(self.current_path)
        last_children = []

        while expanded < limit:
            if not stack:
                # Het stack cua do sau hien tai thi tang depth limit.
                if self.ids_depth_limit >= self.ids_max_depth:
                    self.failed = True
                    self.status = (
                        "No solution found by IDS up to depth "
                        + str(self.ids_max_depth)
                        + "."
                    )
                    break
                self.ids_depth_limit += 1
                stack = [(self.start, [])]

            # Pop node va xu ly nhu IDS binh thuong nhung khong luu history tung buoc.
            state, path = stack.pop()
            last_state = state
            last_path = list(path)
            expanded += 1

            if state == self.goal:
                # Tim thay goal thi cap nhat state hien tai va path loi giai.
                self.current_state = state
                self.current_path = list(path)
                self.current_action = path[-1] if path else "START"
                self.solution_path = list(path)
                self.found = True
                self.status = "Goal found by fast IDS solve at depth " + str(len(path)) + "."
                break

            last_children = []
            if len(path) >= self.ids_depth_limit:
                # Khong sinh con khi cham limit hien tai.
                continue

            path_states = self._path_states(path)
            candidates = []
            for action in ordered_moves(state, self.goal, self.goal_pos):
                child = apply_move(state, action)
                child_path = path + [action]
                generated += 1

                if child in path_states:
                    # Tranh quay lai state da nam trong nhanh hien tai.
                    last_children.append({
                        "state": child,
                        "path": child_path,
                        "action": action,
                        "result": "SKIP - CYCLE",
                        "color": RED,
                    })
                    continue

                reached.add(child)
                candidates.append((child, child_path, action))
                last_children.append({
                    "state": child,
                    "path": child_path,
                    "action": action,
                    "result": "PUSH TO STACK",
                    "color": YELLOW,
                    })

            for child, child_path, _action in reversed(candidates):
                # Push nguoc de giu thu tu uu tien giong step-by-step.
                stack.append((child, child_path))

        # Sau khi solve nhanh, cong counters vao counters chinh.
        self.step += expanded
        self.expanded += expanded
        self.generated += generated
        self.reached = reached
        self.children_info = last_children[:4]
        self.queue = deque(stack[-self.FRONTIER_PREVIEW_LIMIT:])
        self.frontier_count = len(stack)

        if not self.found and not self.failed:
            # Khong tim thay trong limit thi hien node cuoi cung da xu ly.
            self.current_state = last_state
            self.current_path = last_path
            self.current_action = self.current_path[-1] if self.current_path else "START"
            self.failed = True
            self.status = (
                "Stopped: IDS step limit reached. No solution reported within "
                + str(limit)
                + " expanded nodes."
            )

        self.tree_root_state = self.current_state
        self.tree_root_path = list(self.current_path)
        self.tree_focus_path = list(self.solution_path or self.current_path)
        self._store_result()

    # Truy vet duong di tu state ve start bang parent map.

    def _path_from_parent(self, parent, state):
        """Truy vet path tu dict parent ve start."""
        path = []
        while state in parent and parent[state][0] is not None:
            previous, action = parent[state]
            path.append(action)
            state = previous
        path.reverse()
        return path

    # Tao frontier preview tu stack va parent map.

    def _frontier_preview(self, stack, parent):
        """Tao preview frontier tu stack state va parent map cho UI."""
        preview_states = stack[-self.FRONTIER_PREVIEW_LIMIT:]
        return deque((state, self._path_from_parent(parent, state)) for state in preview_states)

    # Chay DFS/DFS L nhanh, dung cho nut Solve Full.

    def _solve_dfs_fast(self, limit):
        """Chay DFS/DFS L nhanh bang parent map de tiet kiem bo nho path."""
        if not self.ready or self.found or self.failed:
            return

        # mode 4 co depth_limit, mode 3 khong co.
        depth_limit = self.depth_limit if self.mode == 4 else None

        # parent luu state truoc va action da di den state hien tai.
        parent = {self.start: (None, None)}
        depth = {self.start: 0}
        stack = []

        # Khoi tao stack tu frontier hien tai, dong thoi tai tao parent/depth cho cac path da co.
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
            # Pop dinh stack de mo rong.
            state = stack.pop()
            last_state = state
            current_depth = depth[state]
            expanded += 1

            if state == self.goal:
                # Truy vet path loi giai bang parent map.
                self.current_state = state
                self.current_path = self._path_from_parent(parent, state)
                self.current_action = self.current_path[-1] if self.current_path else "START"
                self.solution_path = list(self.current_path)
                self.found = True
                self.status = "Goal found by fast DFS solve."
                break

            last_children = []
            if depth_limit is not None and current_depth >= depth_limit:
                # DFS L khong mo rong node da cham depth_limit.
                continue

            candidates = []
            for action in ordered_moves(state, self.goal, self.goal_pos):
                child = apply_move(state, action)
                generated += 1

                if child in reached:
                    # Khong them lai state da reached.
                    last_children.append({
                        "state": child,
                        "parent": state,
                        "action": action,
                        "result": "SKIP - REACHED",
                        "color": RED,
                    })
                    continue

                # Ghi parent/depth cho state moi de truy vet path sau nay.
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
                # Push nguoc de thu tu pop giong ordered_moves.
                stack.append(child)

        # Cap nhat counters va preview UI sau khi chay nhanh.
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
            # Neu khong tim thay, hien node cuoi cung da expand va ly do dung.
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
