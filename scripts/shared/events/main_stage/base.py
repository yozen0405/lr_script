import time
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.ocr import get_main_stage_num
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.events.main_stage.helper import MainStageHelper
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.main_stage.enum import MainStage, Stages, Treasure
from scripts.shared.events.main_stage.finder import MainStageFinder
from scripts.shared.events.main_stage.hooks import MainStageHooks
from scripts.shared.controller.context import GameContext

class BaseMainStage:
    def __init__(self, context: GameContext, hooks=None, is_low=True, team_num=1):
        self.ctx = context
        self.MEMBER3_POS = Positions.MEMBER3.value
        self.MEMBER4_POS = Positions.MEMBER4.value
        self.FRIEND = Positions.FRIEND.value
        self.finder = MainStageFinder(self.ctx.serial)
        self.is_low = is_low
        self.team_num = team_num
        self.hooks = hooks or MainStageHooks(self.ctx.serial)
        self.helper = MainStageHelper(self.ctx.serial)

    def enter_menu(self):
        if self.helper.is_clear():
            return

        if not self.helper.on_page():
            if not wait_click(self.ctx.serial, MainStage.BTN.value):
                raise GameError("無法進入主要關卡選單")
            connection_retry(self.ctx.serial, appear=[(MainStage.TEXT.value, 0.9)], timeout=60.0)
        self.helper.handle_treasure()
        
    def enter_stage(self, custom_stage: Optional[int] = None) -> int:
        if not wait(self.ctx.serial, MainStage.TEXT.value, threshold=0.9, timeout=30.0):
            raise GameError("不在主要關卡")
        
        exist_click(self.ctx.serial, MainStage.NORMAL_NAV.value, threshold=0.9)
        
        if custom_stage is None:
            if not self.finder._check_stage_on_screen():
                self.finder._find_stage()
        else:
            self.finder._find_custom_stage(stage=custom_stage)

        for _ in range(10):
            if wait(self.ctx.serial, MainStage.PRE_START_TEXT.value, timeout=5.5):
                self.hooks.handle_loop_stage_tutorial(self)
                result = self.finder.get_current_stage()
                return result
            elif exist(self.ctx.serial, Retry.TEXT1.value):
                exist_click(self.ctx.serial, Retry.BTN.value)
            else:
                wait_click(self.ctx.serial, Battle.ANIME.value, threshold=0.6, wait_time=2.0)
                continue
        raise GameError("未知的主要關卡")
    
    def leave_menu(self):
        start_time = time.time()
        cnt = 0
        while time.time() - start_time < 60.0:
            if exist(self.ctx.serial, Retry.TEXT1.value) or exist(self.ctx.serial, Retry.TEXT2.value):
                exist_click(self.ctx.serial, Retry.BTN.value)
                continue

            if exist(self.ctx.serial, MainStage.PRE_START_TEXT.value, threshold=0.9):
                exist_click(self.ctx.serial, MainView.BACK.value)
                cnt = 0
                continue
            elif exist(self.ctx.serial, MainStage.TEXT.value, threshold=0.9):
                exist_click(self.ctx.serial, MainView.BACK.value)
                cnt = 0
                continue

            cnt += 1
            if cnt >= 2:
                return

        raise GameError("無法離開主要關卡選單")

             
    def _battle_loop(self, timeout=300) -> bool:
        start_time = time.time()

        while time.time() - start_time < timeout:
            if exist(self.ctx.serial, Settlement.TEXT.value, threshold=0.9):
                return

            if exist(self.ctx.serial, Retry.TEXT1.value) or exist(self.ctx.serial, Retry.TEXT2.value):
                exist_click(self.ctx.serial, Retry.BTN.value)
                continue

            if exist(self.ctx.serial, Battle.START.value):
                wait_click(self.ctx.serial, Battle.START.value)
                continue

            if not exist(self.ctx.serial, Battle.AUTO_BTN_ON.value):
                wait_click(self.ctx.serial, self.MEMBER3_POS)
                wait_click(self.ctx.serial, self.MEMBER4_POS)
                continue
            
            if exist(self.ctx.serial, Battle.PAUSE.value, threshold=0.9):
                self.hooks.on_start_page(self)
                

    def enter_battle(self, multiplier: int):
        log_msg(self.ctx.serial, "Main Stage 戰鬥開始")

        self.hooks.on_pre_start_page_prev(self)
        self.hooks.handle_auto_btn(ctx=self)
        self.hooks.handle_multiplier(times=multiplier, ctx=self)
        
        self.hooks.handle_team_num(ctx=self)

        wait_click(self.ctx.serial, Battle.NEXT.value, timeout=3.0)
        self.hooks.on_pre_start_page_next(ctx=self)

        self._battle_loop()

        log_msg(self.ctx.serial, "結算中")
        self.settlement()
        log_msg(self.ctx.serial, "Main Stage 任務完成")

    def settlement(self):
        connection_retry(self.ctx.serial, appear=Settlement.TEXT.value, timeout=40.0)

        for _ in range(3):
            wait_click(self.ctx.serial, self.MEMBER4_POS)

        cnt = 0
        while True:
            for item in self.hooks.settlement_items(ctx=self):
                if isinstance(item, tuple):
                    img, threshold = item
                    exist_click(self.ctx.serial, img, threshold=threshold, wait_time=1.5)
                else:
                    exist_click(self.ctx.serial, item, wait_time=1.5)

            if exist(self.ctx.serial, Retry.TEXT1.value):
                exist_click(self.ctx.serial, Retry.BTN.value)

            self.hooks.on_settlement_page(ctx=self)
            self.hooks.on_settlement_next_feature(ctx=self)

            if exist(self.ctx.serial, MainView.CLOSE_BOARD.value):
                if exist(self.ctx.serial, Retry.TEXT1.value) or exist(self.ctx.serial, Retry.TEXT2.value):
                    exist_click(self.ctx.serial, Retry.BTN.value)
                    cnt += 1
                else:
                    return

            for terminal_img in [MainView.GACHA_SKIP.value, MainView.SETTINGS.value]:
                if exist(self.ctx.serial, terminal_img):
                    return
            if exist(self.ctx.serial, MainStage.TEXT.value, threshold=0.9):
                return
            
            if cnt >= 5:
                raise GameError("無法完成結算")