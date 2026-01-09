import time
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.vision import get_main_stage_num
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.controller.context import GameContext
from scripts.shared.events.main_stage.session import StageSession
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.main_stage.enum import MainStageImg, Stages, Treasure

class StageFinder:
    def __init__(self, context: GameContext, session: StageSession):
        self.ctx = context
        self.session = session

        self.SCREEN_CENTER_X = 640
        self.SCREEN_CENTER_Y = 360
        
        self.DRAG_DIRS = {
            "RIGHT": ((800, 360), (500, 360)),
            "LEFT":  ((500, 360), (800, 360)),
            "UP":    ((800, 200), (800, 360)),
        }
        self.BOSS_REGION_OFFSETS = (250, 100, 250, 100) # offset_x1, offset_y1, offset_x2, offset_y2
        self.initialize()

    def initialize(self):
        if self.session.custom_stage:
            self.is_boss = (self.session.custom_stage % 12 == 0)
            self.boss_region = None
            if self.is_boss:
                self.target_img = MainStageImg.STAGE(stage=self.session.custom_stage - 1)
            else:
                self.target_img = MainStageImg.STAGE(stage=self.session.custom_stage)
        else:
            self.target_img = None
            self.is_boss = False
            self.boss_region = None

    def _check_stage_on_screen(self, click: bool = False) -> bool:
        if self.target_img is None:
            targets = [
                (Stages.NEW_COMMON.value, 0.98),
                (Stages.NEW_EVENT.value, 0.95),
                # (Stages.BOSS.value, 0.92),
                (Stages.NEW_SHINE.value, 0.8),
            ]
            for img, threshold in targets:
                if exist(self.ctx.serial, img, threshold=threshold):
                    if click:
                        return exist_click(self.ctx.serial, img, threshold=threshold)
                    return True
            return False
        else:
            if click:
                if self.is_boss and self.boss_region:
                    return exist_click(self.ctx.serial, Stages.BOSS.value, threshold=0.92, region=self.boss_region)
                return exist_click(self.ctx.serial, self.target_img, threshold=0.85)

            loc = get_pos(self.ctx.serial, self.target_img, threshold=0.85)
            if not loc:
                return False

            if self.is_boss:
                x, y = loc
                x1 = max(0, x - self.BOSS_REGION_OFFSETS[0])
                y1 = max(0, y - self.BOSS_REGION_OFFSETS[1])
                x2 = min(1280, x + self.BOSS_REGION_OFFSETS[2])
                y2 = min(720, y + self.BOSS_REGION_OFFSETS[3])
                if exist(self.ctx.serial, Stages.BOSS.value, threshold=0.92, region=(x1, y1, x2, y2)):
                    self.boss_region = (x1, y1, x2, y2)
                else:
                    return False
            return True

    def _get_drag_pos(self, base_start, base_end):
        """核心避讓邏輯：自動避開會干擾拖拽的圖示（如寶箱）"""
        start_pos, end_pos = list(base_start), list(base_end)
        
        # 檢查是否有任何需要避開的圖標
        obstacles = [Treasure.ICON.value, Treasure.ICON2.value]
        for obs in obstacles:
            pos = get_pos(self.ctx.serial, obs, threshold=0.9)
            if not pos: continue

            # 如果是水平拖拽，調整 Y 座標避開
            if start_pos[1] == end_pos[1]:
                offset = -100 if pos[1] >= self.SCREEN_CENTER_Y else 100
                start_pos[1] = end_pos[1] = pos[1] + offset
            # 如果是垂直拖拽，調整 X 座標避開
            else:
                offset = -100 if pos[0] >= self.SCREEN_CENTER_X else 100
                start_pos[0] = end_pos[0] = pos[0] + offset
            break # 避開第一個發現的障礙物即可
            
        return tuple(start_pos), tuple(end_pos)

    def _drag_around(self):
        """執行 S 型或特定路徑搜尋關卡"""
        path_sequence = (
            ["RIGHT"] * 5 + ["UP"] * 1 + 
            ["LEFT"] * 5 + ["UP"] * 1
        )
        log_msg(self.ctx.serial, "[StageFinder] 開始拖曳搜尋關卡...")

        for _ in range(10):
            for direction in path_sequence:
                if self._check_stage_on_screen():
                    return

                base_path = self.DRAG_DIRS[direction]
                start, end = self._get_drag_pos(*base_path)
                drag(self.ctx.serial, start, end)

        raise GameError("在搜尋序列後仍找不到關卡")

    def _navigate_to_section(self):
        if self.session.custom_stage is None:
            return

        nav_base = (self.session.custom_stage // 100) * 100
        nav_base = 1 if nav_base == 0 else nav_base
        
        nav_map = {
            1: MainStageImg.STAGE_NAV_1.value,
            100: MainStageImg.STAGE_NAV_100.value,
            200: MainStageImg.STAGE_NAV_200.value,
            300: MainStageImg.STAGE_NAV_300.value,
            400: MainStageImg.STAGE_NAV_400.value,
        }

        wait_click(self.ctx.serial, MainStageImg.NORMAL_NAV.value, threshold=0.9, timeout=3.0)

        if not wait_click(self.ctx.serial, MainStageImg.STAGE_SELECTOR.value, wait_time=1.0, timeout=3.0):
            return
        
        target_nav_btn = nav_map.get(nav_base)
        if not wait_click(self.ctx.serial, target_nav_btn, threshold=0.8):
            raise GameError(f"無法導航到關卡區段: {nav_base}")

    def attempt_enter_stage(self) -> bool:
        if not self._check_stage_on_screen():
            log_msg(self.ctx.serial, "[StageFinder] 目標關卡不在螢幕上")
            return False
        
        start_time = time.time()
        while time.time() - start_time < 80.0:
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.8) or exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.8):
                if not wait_click(self.ctx.serial, Retry.BTN.value):
                    wait_click(self.ctx.serial, Confirm.SMALL.value)
                continue

            if not exist(self.ctx.serial, MainStageImg.TEXT.value, threshold=0.9):
                return True

            if self._check_stage_on_screen(click=True):
                continue
            
        raise GameError("嘗試進入關卡超時，請檢查網路連線或遊戲狀態")
        

    def find_stage(self):
        self.initialize()

        if self.attempt_enter_stage():
            return
        
        self._navigate_to_section()
        self._drag_around()

        if not self.attempt_enter_stage():
            raise GameError("無法找到指定關卡")