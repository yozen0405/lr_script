from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.screen import back
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logger import log_msg
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.teams.sec import TeamsBase
from scripts.shared.events.teams.enum import GearImg, WeaponType, EnhancePageImg, EnhancePagePos
from scripts.shared.constants.leonard import Leonard
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.events.teams.pages.gears.main.base import GearsMainPage
from scripts.shared.controller.context import GameContext
import time

class GearBase:
    def __init__(self, context: GameContext):
        self.ctx = context
        self.gears_main_page = GearsMainPage(context)

        self.FILTER_POS = (1106, 108)
        self.FILTER_GRADE_DESC = (1076, 236)
        self.DRAG_START_POS = (888, 626)
        self.DRAG_END_POS = (888, 246)

    def find_gear(self):
        start_time = time.time()
        while time.time() - start_time < 120.0:
            if exist_click(self.ctx.serial, WeaponType.WAND.value, threshold=0.95):
                log_msg(self.ctx.serial, "找到裝備")
                continue

            if exist_click(self.ctx.serial, EnhancePageImg.BTN.value):
                continue

            if exist(self.ctx.serial, EnhancePageImg.TEXT.value):
                return True

            drag(self.ctx.serial, self.DRAG_START_POS, self.DRAG_END_POS)
        return False
    
    def enhance_gear(self):
        if not wait(self.ctx.serial, EnhancePageImg.TEXT.value):
            raise GameError(self.ctx.serial, "未進入強化頁面")

        if not exist(self.ctx.serial, GearImg.FILTER_GRADE_DESC.value, threshold=0.99):
            wait_click(self.ctx.serial, self.FILTER_POS)
            wait_click(self.ctx.serial, self.FILTER_GRADE_DESC)

        if not exist(self.ctx.serial, GearImg.FILTER_GRADE_DESC.value):
            raise GameError(self.ctx.serial, "無法開啟稀有度篩選")

        wait_click(self.ctx.serial, EnhancePagePos.GEAR1.value)
        if not exist(self.ctx.serial, EnhancePageImg.CHECKED.value):
            raise GameError(self.ctx.serial, "無法選擇裝備")
        
        suc = False
        while True:
            if exist_click(self.ctx.serial, EnhancePageImg.SUCCESS_TEXT.value):
                log_msg(self.ctx.serial, "強化完成")
                suc = True
                continue

            if suc == True and exist(self.ctx.serial, EnhancePageImg.TEXT.value):
                break

            if exist(self.ctx.serial, EnhancePageImg.UPGRADE_TEXT.value):
                wait_click(self.ctx.serial, Confirm.SMALL.value)
                continue
            
            if exist_click(self.ctx.serial, EnhancePageImg.ENHANCE.value):
                pass
        
    def do_filter(self):
        pass

    def on_event(self):
        self.gears_main_page.handle_event()

    def run(self):
        self.find_gear()
        self.enhance_gear()

        wait_click(self.ctx.serial, MainView.BACK.value)
        connection_retry(self.ctx.serial, vanish=[(EnhancePageImg.TEXT.value, 0.95)], retry=MainView.BACK.value)
        wait_click(self.ctx.serial, MainView.BACK.value)
        connection_retry(self.ctx.serial, vanish=[(GearImg.TEXT.value, 0.95)], retry=MainView.BACK.value)
        