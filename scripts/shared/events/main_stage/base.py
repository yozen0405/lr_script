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
from scripts.shared.events.main_stage.finder import MainStageFinder
from scripts.shared.events.main_stage.hooks import MainStageHooks

class BaseMainStage:
    def __init__(self, serial, hooks=None, is_low=True, team_num=1):
        self.serial = serial
        self.MEMBER3_POS = Positions.MEMBER3.value
        self.MEMBER4_POS = Positions.MEMBER4.value
        self.FRIEND = Positions.FRIEND.value
        self.finder = MainStageFinder(serial)
        self.is_low = is_low
        self.team_num = team_num
        self.hooks = hooks or MainStageHooks(serial)

    def enter_menu(self):
        if exist(self.serial, MainStage.TEXT.value, threshold=0.9):
            return

        if wait(self.serial, MainStage.BTN.value, timeout=20.0, wait_time=1.0):
            wait_click(self.serial, MainStage.BTN.value)
            connection_retry(self.serial, appear=[(MainStage.TEXT.value, 0.9)], timeout=60.0)
        else:
            raise GameError("不在主畫面")
        
    def enter_stage(self, custom_stage: Optional[int] = None) -> int:
        if not wait(self.serial, MainStage.TEXT.value, threshold=0.9, timeout=30.0, wait_time=2.5):
            raise GameError("不在主要關卡")
        
        exist_click(self.serial, MainStage.NORMAL_NAV.value, threshold=0.9)
        
        if custom_stage is None:
            if not self.finder._check_stage_on_screen():
                self.finder._find_stage()
        else:
            self.finder._find_custom_stage(stage=custom_stage)

        for _ in range(10):
            if wait(self.serial, MainStage.PRE_START_TEXT.value, timeout=5.5):
                self.hooks.handle_loop_stage_tutorial(self)
                result = self.finder.get_current_stage()
                return result
            elif exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.BTN.value)
            else:
                wait_click(self.serial, Battle.ANIME.value, threshold=0.6, wait_time=2.0)
                continue
        raise GameError("未知的主要關卡")

    def enter_battle(self, multiplier: int):
        log_msg(self.serial, "Main Stage 戰鬥開始")

        self.hooks.on_pre_start_page_prev(self)
        self.hooks.handle_auto_btn(ctx=self)
        self.hooks.handle_multiplier(times=multiplier, ctx=self)
        
        self.hooks.handle_team_num(ctx=self)

        wait_click(self.serial, Battle.NEXT.value, timeout=3.0)
        self.hooks.on_pre_start_page_next(ctx=self)
        wait_click(self.serial, Battle.START.value)

        try:
            connection_retry(self.serial, vanish=Battle.START.value, timeout=60.0)
        except GameError:
            wait_click(self.serial, Battle.START.value)

        if wait(self.serial, Battle.PAUSE.value, timeout=15.0, threshold=0.9):
            self.hooks.on_start_page(self)
            while exist(self.serial, Battle.PAUSE.value, threshold=0.97):
                wait_click(self.serial, self.MEMBER3_POS)
                wait_click(self.serial, self.MEMBER4_POS)
        else:
            raise GameError("無法確認戰鬥狀態，跳出")

        log_msg(self.serial, "結算中")
        self.settlement()
        log_msg(self.serial, "Main Stage 任務完成")

    def settlement(self):
        connection_retry(self.serial, appear=Settlement.TEXT.value, timeout=40.0)

        for _ in range(3):
            wait_click(self.serial, self.MEMBER4_POS)

        while True:
            for item in self.hooks.settlement_items(ctx=self):
                if isinstance(item, tuple):
                    img, threshold = item
                    exist_click(self.serial, img, threshold=threshold, wait_time=1.5)
                else:
                    exist_click(self.serial, item, wait_time=1.5)

            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.BTN.value)

            self.hooks.on_settlement_page(ctx=self)
            self.hooks.on_settlement_next_feature(ctx=self)

            if exist(self.serial, MainView.CLOSE_BOARD.value):
                if exist(self.serial, Retry.TEXT1.value):
                    exist_click(self.serial, Retry.BTN.value)
                else:
                    return

            for terminal_img in [MainView.GACHA_SKIP.value, MainView.SETTINGS.value]:
                if exist(self.serial, terminal_img):
                    return
            if exist(self.serial, MainStage.TEXT.value, threshold=0.9):
                return