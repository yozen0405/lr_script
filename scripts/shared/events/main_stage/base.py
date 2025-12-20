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
from scripts.shared.utils.hacks import apply_mode

class BaseMainStage:
    def __init__(self, context: GameContext, hooks=None, is_low=True, team_num=1, stage=None, is_first=False):
        self.ctx = context
        self.MEMBER1_POS = Positions.MEMBER1.value
        self.MEMBER2_POS = Positions.MEMBER2.value
        self.MEMBER3_POS = Positions.MEMBER3.value
        self.MEMBER4_POS = Positions.MEMBER4.value
        self.METEOR = Positions.METEOR.value
        self.FRIEND = Positions.FRIEND.value
        self.finder = MainStageFinder(self.ctx.serial)
        self.is_low = is_low
        self.team_num = team_num
        self.stage = stage
        self.is_first = is_first

        self.hooks = hooks or MainStageHooks(self.ctx.serial)
        self.helper = MainStageHelper(self.ctx.serial)

    def on_page(self) -> bool:
        return self.helper.on_page()

    def enter_menu(self) -> bool:
        if not self.helper.on_page():
            if not wait_click(self.ctx.serial, MainStage.BTN.value):
                raise GameError("無法進入主要關卡選單")
            connection_retry(self.ctx.serial, appear=[(MainStage.TEXT.value, 0.9)], timeout=60.0)
        return self.handle_not_clear() # True if on treasure event

    def handle_not_clear(self):
        start_time = time.time()    
        fg = False
        while time.time() - start_time < 60.0:
            if self.helper.is_clear():
                return fg
            elif self.helper.handle_treasure():
                fg = True
                continue
            else:
                return False
        raise GameError("主要關卡 interrupt 處理超時")
        
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

             
    def _battle_loop(self, timeout=600) -> bool:
        start_time = time.time()

        retry_time = 0
        state = 0
        while time.time() - start_time < timeout:
            if exist(self.ctx.serial, MainStage.SETTLEMENT.value, threshold=0.9) or \
                exist(self.ctx.serial, Settlement.LEVEL_UP_TEXT.value):
                return

            if exist(self.ctx.serial, Retry.TEXT1.value) or exist(self.ctx.serial, Retry.TEXT2.value):
                exist_click(self.ctx.serial, Retry.BTN.value)
                retry_time += 1
                if retry_time >= 20:
                    break
                continue

            if exist_click(self.ctx.serial, Battle.START.value):
                state = 1
                continue
            elif state == 1:
                state = 2

            if self.stage < 13 and self.is_first:
                wait_click(self.ctx.serial, self.MEMBER1_POS)
                wait_click(self.ctx.serial, self.MEMBER2_POS)
                wait_click(self.ctx.serial, self.MEMBER3_POS)
                wait_click(self.ctx.serial, self.MEMBER4_POS)
            
            if state == 2:
                self.hooks.on_start_page(self)
        raise GameError("戰鬥超時")
                

    def enter_battle(self, multiplier: int, timeout: int = 600):
        log_msg(self.ctx.serial, "Main Stage 戰鬥開始")

        apply_mode(self.ctx.serial, mode_name="main_stage", state="on")

        self.hooks.on_pre_start_page_prev(self)
        self.hooks.handle_auto_btn(base=self)
       
        if not self.is_first:
            self.hooks.handle_multiplier(times=multiplier, base=self)
            self.hooks.handle_team_num(base=self)

        if not self.is_first or self.stage >= 30:
            if not wait_click(self.ctx.serial, Battle.NEXT.value, timeout=10.0):
                raise GameError("無法開始戰鬥")
            
        if self.is_first:
            self.hooks.on_pre_start_page_next(base=self)

        self._battle_loop(timeout=timeout)

        log_msg(self.ctx.serial, "結算中")
        self.settlement()
        log_msg(self.ctx.serial, "Main Stage 任務完成")
    
        apply_mode(self.ctx.serial, mode_name="main_stage", state="off")

    def settlement(self):
        self.ctx.current_stage_num = self.stage

        start_time = time.time()    
        while time.time() - start_time < 240.0:
            on_page = False
            for item in self.hooks.settlement_items(base=self):
                if isinstance(item, tuple):
                    img, threshold = item
                    if exist_click(self.ctx.serial, img, threshold=threshold, wait_time=1.0):
                        on_page = True
                else:
                    if exist_click(self.ctx.serial, item, wait_time=1.0):
                        on_page = True

            if exist_click(self.ctx.serial, MainView.SKIP.value):
                wait_click(self.ctx.serial, Confirm.SMALL.value)

            self.hooks.on_settlement_page(base=self)
            self.hooks.on_settlement_next_feature(base=self)

            if exist(self.ctx.serial, Retry.TEXT1.value) or exist(self.ctx.serial, Retry.TEXT2.value):
                exist_click(self.ctx.serial, Retry.BTN.value)
                continue

            if not on_page and (
                exist(self.ctx.serial, MainView.AVATAR.value, threshold=0.9) or \
                exist(self.ctx.serial, MainView.CLOSE_BOARD.value) or \
                exist(self.ctx.serial, MainView.SKIP_2.value)
            ):
                return
            
            if not on_page and exist(self.ctx.serial, MainStage.TEXT.value, threshold=0.9):
                self.helper.handle_treasure()
                return
            
        raise GameError("結算超時")