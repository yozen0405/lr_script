import time
from core.system.logger import log_msg
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.ocr import get_main_stage_num
from core.base.exceptions import GameError
from scripts.shared.constants import positions
from scripts.shared.utils.retry import connection_retry

class BaseMainStage:
    def __init__(self, serial):
        self.serial = serial
        self.MEMBER3_POS = positions["member3"]
        self.MEMBER4_POS = positions["member4"]
        self.FRIEND = positions["friend"]

    def enter_menu(self):
        if wait(self.serial, "main_stage_btn.png", timeout=20.0, wait_time=1.0):
            wait_click(self.serial, "main_stage_btn.png")
            connection_retry(self.serial, wait_name="main_stage_text.png", timeout=60.0)
        else:
            raise GameError("不在主畫面")

    def _check_stage_on_screen(self, timeout: float = 3.0):
        for image, threshold in [
            ("new_stage_common.png", 0.98),
            ("new_stage_evt.png", 0.97),
            ("boss_stage.png", 0.92),
            ("new_stage.png", 0.85),
        ]:
            if wait(self.serial, image, threshold=threshold, timeout=timeout):
                connection_retry(self.serial, image_name="main_stage_text.png", retry_text="retry_text2.png", timeout=40.0)
                return True
        return False

    def _find_stage(self):
        y = 360
        x = 800
        drag_pairs = [
            ((800, 360), (500, 360)), # 右
            ((800, 360), (500, 360)), # 右
            ((800, 360), (500, 360)), # 右
            ((800, 360), (500, 360)), # 右
            ((800, 360), (500, 360)), # 右
            ((800, 200), (800, 360)), # 上
            ((500, 360), (800, 360)), # 左
            ((500, 360), (800, 360)), # 左
            ((500, 360), (800, 360)), # 左
            ((500, 360), (800, 360)), # 左
            ((500, 360), (800, 360)), # 左
            ((800, 200), (800, 360)), # 上
        ]
        timeout = 1.0
        for _ in range(10):
            for base_start, base_end in drag_pairs:
                start_pos = list(base_start)
                end_pos = list(base_end)

                if exist(self.serial, "new_stage_locked.png", threshold=0.9):
                    timeout = 5.0
                if self._check_stage_on_screen(timeout=timeout):
                    return 

                if wait(self.serial, "treasure_icon.png", threshold=0.9, timeout=3.5):
                    pos = get_pos(self.serial, "treasure_icon.png", threshold=0.9)

                    if start_pos[1] == end_pos[1]:
                        y_val = pos[1] - 100 if pos[1] >= 360 else pos[1] + 100
                        start_pos[1] = y_val
                        end_pos[1] = y_val
                    else:
                        x_val = pos[0] - 100 if pos[0] >= 640 else pos[0] + 100
                        start_pos[0] = x_val
                        end_pos[0] = x_val
                
                if wait(self.serial, "treasure_icon2.png", threshold=0.95, timeout=3.5):
                    pos = get_pos(self.serial, "treasure_icon2.png", threshold=0.95)

                    if start_pos[1] == end_pos[1]:
                        y_val = pos[1] - 100 if pos[1] >= 360 else pos[1] + 100
                        start_pos[1] = y_val
                        end_pos[1] = y_val
                    else:
                        x_val = pos[0] - 100 if pos[0] >= 640 else pos[0] + 100
                        start_pos[0] = x_val
                        end_pos[0] = x_val

                drag(self.serial, tuple(start_pos), tuple(end_pos))

    def get_current_stage(self) -> int:
        return get_main_stage_num(self.serial)

    def enter_stage(self) -> int:
        if not wait(self.serial, "main_stage_text.png", timeout=30.0, wait_time=2.5):
            raise GameError("不在主要關卡")

        if not self._check_stage_on_screen():
            self._find_stage()

        for _ in range(10):
            if wait(self.serial, "main_stage_pre_start_text.png", timeout=5.5):
                self.handle_loop_stage_tutorial()
                return self.get_current_stage()
            else:
                wait_click(self.serial, "stage_anime.png", threshold=0.6, wait_time=2.0)
                continue
        raise GameError("未知的主要關卡")

    def run(self, anime=True, has_next=True, big_ok=False):
        log_msg(self.serial, "Main Stage 戰鬥開始")

        wait_vanish(self.serial, "main_stage_text.png", timeout=20.0)

        if anime:
            time.sleep(2.0)
            for _ in range(3):
                if not wait_click(self.serial, "stage_anime.png", wait_time=1.0, threshold=0.6):
                    break

        if has_next:
            wait_click(self.serial, "next.png")

        self._pre_start_page()

        wait_click(self.serial, "start.png")
        connection_retry(self.serial, image_name="start.png", timeout=60.0)

        if wait(self.serial, "pause.png", timeout=15.0, threshold=0.9):
            self._on_start_page()
            while exist(self.serial, "pause.png", threshold=0.97):
                wait_click(self.serial, self.MEMBER3_POS)
                wait_click(self.serial, self.MEMBER4_POS)
        else:
            raise GameError("無法確認戰鬥狀態，跳出")

        log_msg(self.serial, "結算中")
        self.settlement()
        log_msg(self.serial, "Main Stage 任務完成")

    def _handle_loop_stage_tutorial(self):
        pass

    def _on_pre_start_page(self):
        pass

    def _on_start_page(self):
        pass

    def _on_settlement_page(self):
        pass

    def settlement(self):
        if wait_click(self.serial, "cancel_lose.png", wait_time=10.0):
            wait_click(self.serial, "close_lose_tips.png", wait_time=7.0)
            if not wait_click(self.serial, "confirm_small.png", wait_time=7.0):
                raise GameError("沒有進入失敗葉面")
            raise GameError("輸了")

        connection_retry(self.serial, wait_name="main_stage_settlement_text.png", retry_text="retry_text2.png", timeout=40.0)

        for _ in range(3):
            wait_click(self.serial, self.MEMBER4_POS)

        while True:
            for img in ["acquired.png", "confirm_big.png", "confirm_big2.png", "oneReward.png", "confirm_small.png", "stop.png"]:
                exist_click(self.serial, img, wait_time=1.5)

            if exist(self.serial, "retry_text.png"):
                exist_click(self.serial, "retry.png")

            self._on_settlement_page()
            
            if exist(self.serial, "close_board.png"):
                if exist(self.serial, "retry_text.png"):
                    exist_click(self.serial, "retry.png")
                else:
                    return

            for terminal_img in ["gacha_skip.png", "settings_btn.png", "main_stage_text.png"]:
                if exist(self.serial, terminal_img):
                    return