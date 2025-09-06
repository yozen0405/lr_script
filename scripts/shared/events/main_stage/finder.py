import time
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.ocr import get_main_stage_num
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import GameView, Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.main_stage.enum import MainStage, Stages, Treasure

class MainStageFinder:
    def __init__(self, serial):
        self.serial = serial
        self.RIGHT_DRAG = ((800, 360), (500, 360))
        self.LEFT_DRAG = ((500, 360), (800, 360))
        self.UP_DRAG = ((800, 200), (800, 360))
        self.DOWN_DRAG = ((800, 360), (800, 200))

    def _check_stage_on_screen(self):
        for image, threshold in [
            (Stages.NEW_COMMON.value, 0.98),
            (Stages.NEW_EVENT.value, 0.97),
            (Stages.BOSS.value, 0.92),
            (Stages.NEW_SHINE.value, 0.85),
        ]:
            if exist_click(self.serial, image, threshold=threshold):
                connection_retry(self.serial, vanish=MainStage.TEXT.value, retry=[(image, threshold)], timeout=40.0)
                return True
        return False
    
    def _get_drag_table(self):
        return [
            self.RIGHT_DRAG, # 右
            self.RIGHT_DRAG, # 右
            self.RIGHT_DRAG, # 右
            self.RIGHT_DRAG, # 右
            self.RIGHT_DRAG, # 右
            self.UP_DRAG,    # 上
            self.LEFT_DRAG,  # 左
            self.LEFT_DRAG,  # 左
            self.LEFT_DRAG,  # 左
            self.LEFT_DRAG,  # 左
            self.LEFT_DRAG,  # 左
            self.UP_DRAG,    # 上
        ]

    def _find_stage(self, custom_stage: str = None):
        drag_pairs = self._get_drag_table()
        for _ in range(10):
            for base_start, base_end in drag_pairs:
                start_pos = list(base_start)
                end_pos = list(base_end)

                if custom_stage is None:
                    if self._check_stage_on_screen():
                        return
                else:
                    if exist_click(self.serial, custom_stage, threshold=0.9):
                        connection_retry(self.serial, vanish=[(MainStage.TEXT.value, 0.9)], timeout=40.0)
                        return

                if exist(self.serial, Treasure.ICON.value, threshold=0.9):
                    pos = get_pos(self.serial, Treasure.ICON.value, threshold=0.9)

                    if start_pos[1] == end_pos[1]:
                        y_val = pos[1] - 100 if pos[1] >= 360 else pos[1] + 100
                        start_pos[1] = y_val
                        end_pos[1] = y_val
                    else:
                        x_val = pos[0] - 100 if pos[0] >= 640 else pos[0] + 100
                        start_pos[0] = x_val
                        end_pos[0] = x_val
                
                if exist(self.serial, Treasure.ICON2.value, threshold=0.95):
                    pos = get_pos(self.serial, Treasure.ICON2.value, threshold=0.95)

                    if start_pos[1] == end_pos[1]:
                        y_val = pos[1] - 100 if pos[1] >= 360 else pos[1] + 100
                        start_pos[1] = y_val
                        end_pos[1] = y_val
                    else:
                        x_val = pos[0] - 100 if pos[0] >= 640 else pos[0] + 100
                        start_pos[0] = x_val
                        end_pos[0] = x_val

                drag(self.serial, tuple(start_pos), tuple(end_pos))
        raise GameError("找不到關卡")

    def _find_custom_stage(self, stage: int):
        # 魔王關會爛
        # 要去魔王關，先找附近的普通關卡，看他們是否存在
        # 假設存在，點進去魔王關，看是不是我們要的，如果不是就退回來，然後繼續滑動找
        stage_str = f"main_stage_stage_{stage}.png"
        if exist_click(self.serial, stage_str, threshold=0.9):
            return
        exist_click(self.serial, MainStage.STAGE_SELECTOR.value, wait_time=1.0)

        if stage < 100:
            exist_click(self.serial, MainStage.STAGE_NAV_1.value)
        elif stage < 200:
            exist_click(self.serial, MainStage.STAGE_NAV_100.value)
        elif stage < 300:
            exist_click(self.serial, MainStage.STAGE_NAV_200.value)
        elif stage < 400:
            exist_click(self.serial, MainStage.STAGE_NAV_300.value)
        elif stage < 500:
            exist_click(self.serial, MainStage.STAGE_NAV_400.value)

        self._find_stage(custom_stage=stage_str)
        if not wait(self.serial, MainStage.PRE_START_TEXT.value, timeout=5.5):
            raise GameError(f"找不到指定關卡 {stage}")

    def get_current_stage(self) -> int:
        stage = get_main_stage_num(self.serial)
        return stage