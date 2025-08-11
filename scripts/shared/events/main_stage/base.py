import time
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.ocr import get_main_stage_num
from core.base.exceptions import GameError
from scripts.shared.constants.positions import positions
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import GameView, Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.main_stage.enum import MainStage, Stages, Treasure

class BaseMainStage:
    def __init__(self, serial):
        self.serial = serial
        self.MEMBER3_POS = positions["member3"]
        self.MEMBER4_POS = positions["member4"]
        self.FRIEND = positions["friend"]

    def enter_menu(self):
        if exist(self.serial, MainStage.TEXT):
            return

        if wait(self.serial, MainStage.BTN, timeout=20.0, wait_time=1.0):
            wait_click(self.serial, MainStage.BTN)
            connection_retry(self.serial, wait_name= MainStage.TEXT, timeout=60.0)
        else:
            raise GameError("不在主畫面")

    def _check_stage_on_screen(self, timeout: float = 3.0):
        for image, threshold in [
            (Stages.NEW_COMMON, 0.98),
            (Stages.NEW_EVENT, 0.97),
            (Stages.BOSS, 0.92),
            (Stages.NEW_SHINE, 0.85),
        ]:
            if wait_click(self.serial, image, threshold=threshold, timeout=timeout):
                connection_retry(self.serial, image_name=MainStage.TEXT, retry_text=Retry.TEXT2, timeout=40.0)
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

                if exist(self.serial, Stages.LOCKED, threshold=0.9):
                    timeout = 5.0
                if self._check_stage_on_screen(timeout=timeout):
                    return 

                if wait(self.serial, Treasure.ICON, threshold=0.9, timeout=3.5):
                    pos = get_pos(self.serial, Treasure.ICON, threshold=0.9)

                    if start_pos[1] == end_pos[1]:
                        y_val = pos[1] - 100 if pos[1] >= 360 else pos[1] + 100
                        start_pos[1] = y_val
                        end_pos[1] = y_val
                    else:
                        x_val = pos[0] - 100 if pos[0] >= 640 else pos[0] + 100
                        start_pos[0] = x_val
                        end_pos[0] = x_val
                
                if wait(self.serial, Treasure.ICON2, threshold=0.95, timeout=3.5):
                    pos = get_pos(self.serial, Treasure.ICON2, threshold=0.95)

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

    def enter_stage(self, custom_stage: Optional[str] = None) -> int:
        if not wait(self.serial, MainStage.TEXT, timeout=30.0, wait_time=2.5):
            raise GameError("不在主要關卡")
        
        if custom_stage is None and not self._check_stage_on_screen():
            self._find_stage()
        if custom_stage is not None:
            wait_click(self.serial, custom_stage)

        for _ in range(10):
            if wait(self.serial, MainStage.PRE_START_TEXT, timeout=5.5):
                self._handle_loop_stage_tutorial()
                return self.get_current_stage()
            elif exist(self.serial, Retry.TEXT1):
                exist_click(self.serial, Retry.BTN)
            else:
                wait_click(self.serial, Battle.ANIME, threshold=0.6, wait_time=2.0)
                continue
        raise GameError("未知的主要關卡")

    def enter_battle(self):
        log_msg(self.serial, "Main Stage 戰鬥開始")

        self._on_pre_start_page_prev()
        wait_click(self.serial, Battle.NEXT, timeout=3.0)
        self._on_pre_start_page_next()

        wait_click(self.serial, Battle.START)
        connection_retry(self.serial, image_name=Battle.START, timeout=60.0)

        if wait(self.serial, Battle.PAUSE, timeout=15.0, threshold=0.9):
            self._on_start_page()
            while exist(self.serial, Battle.PAUSE, threshold=0.97):
                wait_click(self.serial, self.MEMBER3_POS)
                wait_click(self.serial, self.MEMBER4_POS)
        else:
            raise GameError("無法確認戰鬥狀態，跳出")

        log_msg(self.serial, "結算中")
        self.settlement()
        log_msg(self.serial, "Main Stage 任務完成")

    def _handle_loop_stage_tutorial(self):
        if not wait(self.serial, Battle.MULTIPLIER_TEXT, timeout=3.0):
            return
        wait_click(self.serial, Battle.CYCLE, wait_time=2.5)
        wait_click(self.serial, Leonard.BG_POINT, wait_time=2.5)
        wait_click(self.serial, Battle.MULTIPLIER_OFF, wait_time=1.0)
        wait_click(self.serial, Battle.MULTIPLIER_ON, wait_time=1.0)
        wait_click(self.serial, Leonard.BG_HAPPY, wait_time=1.0)


    def _on_pre_start_page_prev(self):
        pass
    
    def _on_pre_start_page_next(self):
        pass

    def _on_start_page(self):
        pass

    def _on_settlement_page(self):
        pass

    def _on_settlement_next_feature(self):
        if not wait(self.serial, MainStage.NEXT_FEATURE, timeout=3.0):
            return
        wait_click(self.serial, Settlement.AGAIN, wait_time=1.2)
        wait_click(self.serial, Settlement.NEXT)


    def settlement(self):
        if wait_click(self.serial, Settlement.CANCEL_LOSE, wait_time=10.0):
            wait_click(self.serial, Settlement.CLOSE_LOSE_TIPS, wait_time=7.0)
            if not wait_click(self.serial, Confirm.SMALL, wait_time=7.0):
                raise GameError("沒有進入失敗葉面")
            raise GameError("輸了")

        connection_retry(self.serial, wait_name=Settlement.TEXT, retry_text=Retry.TEXT2, timeout=40.0)

        for _ in range(3):
            wait_click(self.serial, self.MEMBER4_POS)

        while True:
            for img in [Settlement.ACQUIRED, Confirm.BIG1, Confirm.BIG2, Settlement.ONE_REWARD, Confirm.SMALL, Settlement.STOP]:
                exist_click(self.serial, img, wait_time=1.5)

            if exist(self.serial, Retry.TEXT1):
                exist_click(self.serial, Retry.BTN)

            self._on_settlement_page()
            self._on_settlement_next_feature()
            
            if exist(self.serial, MainView.CLOSE_BOARD):
                if exist(self.serial, Retry.TEXT1):
                    exist_click(self.serial, Retry.BTN)
                else:
                    return

            for terminal_img in [MainView.GACHA_SKIP, MainView.SETTINGS, MainStage.TEXT]:
                if exist(self.serial, terminal_img):
                    return