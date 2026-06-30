from collections import deque
from copy import deepcopy

from puzzle import is_solvable, is_valid_state

from .bfs import BfsSearchMixin
from .dfs import DfsSearchMixin
from .informed import InformedSearchMixin
from .local import LocalSearchMixin
from .result import ResultMixin
from .special_modes import SpecialModesMixin


class SearchVisualizer(
    BfsSearchMixin,
    DfsSearchMixin,
    InformedSearchMixin,
    LocalSearchMixin,
    SpecialModesMixin,
    ResultMixin,
):
    """Quan ly state hien thi va dieu phoi cac thuat toan cho 8-puzzle."""

    # Gioi han so snapshot de nut Prev Step khong ton qua nhieu bo nho.
    HISTORY_LIMIT = 300

    # Gioi han do sau mac dinh cho DFS co gioi han.
    DEFAULT_DFS_DEPTH = 20

    # IDS se tang do sau dan den muc nay roi dung neu chua tim thay.
    DEFAULT_IDS_MAX_DEPTH = 31

    # Gioi han so node expand de tranh DFS chay qua lau.
    DFS_STEP_LIMIT = 200000

    # Khi frontier qua lon, UI chi giu mot phan preview.
    FRONTIER_PREVIEW_LIMIT = 80

    # Cac mode hop le trong chuong trinh.
    RESULT_MODES = range(1, 20)

    # Cac mode dung heapq/priority queue.
    PRIORITY_MODES = (5, 6, 7)

    # Cac mode dung stack.
    STACK_MODES = (3, 4, 8)

    # Cac mode hill climbing.
    HILL_MODES = (9, 10, 11, 12)

    # So lan random-restart toi da de tranh vong lap vo han khi hill climbing bi ket.
    RANDOM_RESTART_LIMIT = 60

    # Moi lan restart se tao mot state moi bang random walk tu START de path van hop le.
    RANDOM_RESTART_WALK = 28

    # So state duoc giu lai trong Local Beam Search.
    DEFAULT_BEAM_WIDTH = 4

    def __init__(self, start, goal, mode=1):
        # start/goal luu dang tuple de co the dua vao set/dict.
        self.start = tuple(start)
        self.goal = tuple(goal)

        # goal_pos giup tinh Manhattan nhanh: tile -> index trong goal.
        self.goal_pos = {value: index for index, value in enumerate(self.goal)}

        # mode la thuat toan hien tai; bfs_mode ghi nho BFS M1/M2 khi doi tab.
        self.mode = mode
        self.bfs_mode = mode if mode in (1, 2) else 1

        # Cac tham so rieng cho DFS L va IDS.
        self.depth_limit = self.DEFAULT_DFS_DEPTH
        self.ids_max_depth = self.DEFAULT_IDS_MAX_DEPTH
        self.ids_depth_limit = 0
        self.restart_count = 0
        self.beam_width = self.DEFAULT_BEAM_WIDTH

        # tie_breaker giup heapq khong so sanh state khi priority bang nhau.
        self.tie_breaker = 0

        # results luu ket qua da chay cua tung mode de UI co the so sanh.
        self.results = self._empty_results()
        self.history = []
        self.reset_run(keep_results=True)

    # Tao dict ket qua rong cho cac mode.

    def _empty_results(self):
        """Tao dict ket qua rong cho tat ca mode."""
        return {mode: None for mode in self.RESULT_MODES}

    # Cap nhat bai toan moi va reset cac ket qua da chay.

    def update_puzzle(self, start, goal):
        """Cap nhat START/GOAL moi va reset toan bo ket qua cu."""
        self.start = tuple(start)
        self.goal = tuple(goal)
        self.goal_pos = {value: index for index, value in enumerate(self.goal)}
        self.results = self._empty_results()
        self.reset_current_mode()

    # Doi thuat toan hien tai va reset lan chay.

    def set_mode(self, mode):
        """Doi thuat toan dang chay va reset lan chay hien tai."""
        self.mode = mode
        if mode in (1, 2):
            self.bfs_mode = mode

        # Special handling: mode 16 generates both start and goal internally.
        if mode == 16:
            self._generate_random_start_goal()
            return

        self.reset_current_mode(request_auto=mode in (14, 15, 17))

    def reset_current_mode(self, keep_results=True, request_auto=False):
        """Reset lan chay va khoi tao lai cac du lieu rieng cua mode dac biet."""
        self.reset_run(keep_results=keep_results)
        self.auto_start_requested = False
        if not self.ready:
            return

        if self.mode == 14:
            self._init_hidden_mode()
            self._prepare_plan_execution("Hidden Tiles Mode", request_auto=request_auto)
        elif self.mode == 15:
            self.hidden_indices = set()
            self._prepare_plan_execution("Blind Mode", request_auto=request_auto)
        elif self.mode == 16:
            self.hidden_indices = set()
            self._prepare_plan_execution("No Start/Goal Mode", request_auto=request_auto)
        elif self.mode == 17:
            self.hidden_indices = set()
            self._prepare_plan_execution(
                "Simulated Local Search Mode",
                request_auto=request_auto,
                planner="best_first",
            )
        elif self.mode == 18:
            self.hidden_indices = set()
            self._prepare_plan_execution("AC-3 Mode", request_auto=request_auto, planner="ac3")
        elif self.mode == 19:
            self.hidden_indices = set()
            self._prepare_plan_execution("Min-Conflicts Mode", request_auto=request_auto, planner="min_conflicts")
        else:
            self.hidden_indices = set()
            self.precomputed_path = None
            self.precomputed_index = 0

    # Reset frontier, counters, history va trang thai hien thi.

    def reset_run(self, keep_results=True):
        """Khoi tao lai frontier, counters va trang thai hien thi cho mode hien tai."""
        if not keep_results:
            self.results = self._empty_results()

        # queue co the la heap list voi A*/Greedy, con lai dung deque.
        self.history = []
        self.queue = [] if self.mode in self.PRIORITY_MODES else deque()

        # frontier_count dung khi solve nhanh chi giu preview nhung van can so luong that.
        self.frontier_count = None

        # reached la dict state->g_cost voi priority modes, la set voi mode con lai.
        self.reached = {} if self.mode in self.PRIORITY_MODES else set()
        self.children_info = []

        # Reset counters va trang thai dang hien tren UI.
        self.ids_depth_limit = 0
        self.restart_count = 0
        self.tie_breaker = 0
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
        self.auto_start_requested = False

        # Kiem tra board hop le truoc khi dua vao thuat toan.
        if not is_valid_state(self.start) or not is_valid_state(self.goal):
            self.ready = False
            self.failed = True
            self.status = "Invalid board: Start and Goal must contain 0..8 exactly once."
            return

        # Neu parity khong dung thi 8-puzzle khong the di tu start den goal.
        if not is_solvable(self.start, self.goal):
            self.ready = False
            self.failed = True
            self.status = "Unsolvable: relative inversion parity does not match this goal."
            return

        # Dua node start vao frontier ban dau.
        if self.mode in self.PRIORITY_MODES:
            self._push_priority(self.start, [], 0)
        else:
            self.queue.append((self.start, []))
            self.reached.add(self.start)

        self.status = "Ready. Press Next Step, Auto Run, or Solve Full."

        # Truong hop dac biet: start da bang goal.
        if self.start == self.goal:
            self.found = True
            self.solution_path = []
            self.status = "Start is already the goal. Solution length = 0."
            self._store_result()

    # Lay mo ta cach mode hien tai kiem tra goal.

    def _make_snapshot(self):
        """Chup lai toan bo trang thai de Prev Step co the quay lui."""
        return {
            "queue": deepcopy(self.queue),
            "frontier_count": self.frontier_count,
            "reached": deepcopy(self.reached),
            "children_info": deepcopy(self.children_info),
            "ids_depth_limit": self.ids_depth_limit,
            "restart_count": self.restart_count,
            "tie_breaker": self.tie_breaker,
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
            "hidden_indices": set(getattr(self, "hidden_indices", set())),
            "precomputed_path": (
                list(self.precomputed_path) if getattr(self, "precomputed_path", None) is not None else None
            ),
            "precomputed_index": getattr(self, "precomputed_index", 0),
        }

    # Khoi phuc trang thai tu snapshot.

    def _restore_snapshot(self, snapshot):
        """Khoi phuc trang thai tu snapshot da luu."""
        self.queue = deepcopy(snapshot["queue"])
        self.frontier_count = snapshot.get("frontier_count")
        self.reached = deepcopy(snapshot["reached"])
        self.children_info = deepcopy(snapshot["children_info"])
        self.ids_depth_limit = snapshot.get("ids_depth_limit", 0)
        self.restart_count = snapshot.get("restart_count", 0)
        self.tie_breaker = snapshot.get("tie_breaker", 0)
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
        self.hidden_indices = set(snapshot.get("hidden_indices", set()))
        self.precomputed_path = (
            list(snapshot["precomputed_path"]) if snapshot.get("precomputed_path") is not None else None
        )
        self.precomputed_index = snapshot.get("precomputed_index", 0)

    # Day snapshot hien tai vao history.

    def _push_history(self):
        """Luu snapshot hien tai vao history truoc khi chay sang buoc moi."""
        self.history.append(self._make_snapshot())
        if len(self.history) > self.HISTORY_LIMIT:
            self.history.pop(0)

    # Kiem tra co the quay lai buoc truoc khong.

    def can_go_back(self):
        """Tra ve True neu co the bam Prev Step."""
        return len(self.history) > 0

    # Lay kich thuoc frontier that.

    def frontier_size(self):
        """Lay kich thuoc frontier that, ke ca khi queue chi la preview sau solve nhanh."""
        if self.frontier_count is not None:
            return self.frontier_count
        return len(self.queue)

    # Quay lai mot buoc thuat toan bang snapshot gan nhat.

    def previous_step(self):
        """Quay lai mot buoc bang snapshot gan nhat."""
        if not self.history:
            return

        self._restore_snapshot(self.history.pop())
        self.status = "Went back one step. " + self.status

    # Luu ket qua cua mode hien tai vao bang results.

    def next_step(self, record_history=True):
        """Chay mot buoc thi thuc cua thuat toan duoc chon."""
        # Neu chua san sang hoac da ket thuc thi khong lam gi.
        if not self.ready or self.found or self.failed:
            return

        # Bao ve DFS/IDS khoi viec expand qua nhieu node.
        if self.mode in self.STACK_MODES and self.expanded >= self.DFS_STEP_LIMIT:
            self.failed = True
            self.status = (
                "Stopped: DFS step limit reached. No solution reported within "
                + str(self.DFS_STEP_LIMIT)
                + " expanded nodes."
            )
            self._store_result()
            return
        
        # Luu history truoc khi thay doi trang thai, de Prev Step quay lai duoc.
        if record_history:
            self._push_history()

        # Neu frontier rong, IDS co the tang do sau; cac mode khac xem nhu that bai.
        if not self.queue:
            if self.mode == 8 and self._start_next_ids_iteration():
                return

            self.failed = True
            if self.mode == 4:
                self.status = "No solution found within depth limit " + str(self.depth_limit) + "."
            elif self.mode == 8:
                self.status = "No solution found by IDS."
            else:
                self.status = "No solution: frontier is empty."
            self._store_result()
            return

        # Goi ham xu ly mot buoc theo mode hien tai.
        if self.mode in (14, 15, 16, 17):
            self._step_plan_execution()
        elif self.mode == 1:
            self._step_mode_1()
        elif self.mode == 2:
            self._step_mode_2()
        elif self.mode == 3:
            self._step_mode_3()
        elif self.mode == 4:
            self._step_mode_4()
        elif self.mode in self.PRIORITY_MODES:
            self._step_mode_5()
        elif self.mode == 8:
            self._step_mode_8()
        elif self.mode == 13:
            self._step_local_beam_search()
        else:
            self._step_hill_climbing()

    # Chay mot buoc BFS Mode 1: kiem tra goal khi sinh child.

    def solve_full(self, limit=200000):
        """Chay thuat toan hien tai den khi tim thay loi giai hoac dung lai."""
        # Luu history mot lan de co the quay lai truoc khi solve full.
        if self.ready and not self.found and not self.failed:
            self._push_history()

        # DFS/IDS co ban solve nhanh rieng de tranh luu path qua nhieu trong queue.
        if self.mode in (3, 4):
            self._solve_dfs_fast(min(limit, self.DFS_STEP_LIMIT))
            return

        if self.mode == 8:
            self._solve_ids_fast(min(limit, self.DFS_STEP_LIMIT))
            return

        # Cac mode con lai lap next_step den khi ket thuc hoac cham limit.
        count = 0
        while self.ready and not self.found and not self.failed and count < limit:
            self.next_step(record_history=False)
            count += 1

        if count >= limit and not self.found:
            # Cham gioi han buoc thi xem nhu that bai de khong treo UI.
            self.failed = True
            self.status = "Stopped: step limit reached."
            self._store_result()

    # Chay IDS nhanh, dung cho nut Solve Full.
