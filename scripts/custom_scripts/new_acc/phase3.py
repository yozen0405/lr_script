import time
import os
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from core.base.exceptions import GameError
from scripts.shared.utils.game_view import close_board
from scripts.shared.events.main_stage.selector import main_stage_enter_menu, main_stage_finish_new
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry, Positions
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.login.sec import guest_login
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.events.gacha.enum import Gacha

from scripts.custom_scripts.new_acc.enum import Phase3UI, Gear
from scripts.custom_scripts.new_acc.base import BasePhase

class Phase3(BasePhase):
    def _login(self):
        log_msg(self.serial, "第三階段")
        guest_login(self.serial)
        close_board(self.serial)

    def _on_main_view_rene(self):
        on_main_view(self.serial) 

        if wait_click(self.serial, MainView.SKIP.value, timeout=5.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=3.0)

    def upgrade_rene(self):
        log_msg(self.serial, "升級炳妮")
        wait_click(self.serial, Phase3UI.RENE.value, timeout=7.0, wait_time=2.0)
        wait_click(self.serial, TeamsImg.UPGRADE_BTN.value)
        connection_retry(self.serial, appear=MainView.BACK.value, timeout=40.0)
        drag(self.serial, (80, 574), (478, 341), wait_time=3.0, timeout=10.0)
        wait_click(self.serial, TeamsImg.UPGRADE_LVL_BTN.value)
        for _ in range(3):
            wait_click(self.serial, TeamsImg.UPGRADE_SUCCESS.value, timeout=5.0, wait_time=1.0)
        if wait_click(self.serial, MainView.SKIP.value, timeout=15.0):
            wait_click(self.serial, Confirm.SMALL.value)
        wait_click(self.serial, MainView.BACK.value)
        connection_retry(self.serial, vanish=MainView.BACK.value, timeout=40.0)

    def _on_main_view_gacha(self):
        on_main_view(self.serial, MainView.CLOSE_BOARD.value, vanish=False)
        if wait_click(self.serial, MainView.SKIP.value, timeout=20.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=3.0)

    def gacha_equip(self):
        wait_click(self.serial, Gacha.ICON.value, timeout=7.0)
        connection_retry(self.serial, appear=Gacha.TEXT.value, timeout=40.0)
        
        if wait_click(self.serial, MainView.SKIP.value, timeout=5.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=3.0)
        wait_click(self.serial, Gacha.EQUIP_NAV.value)
        wait_click(self.serial, Gacha.EQUIP_SHIRT_PULL.value)
        wait_click(self.serial, Gacha.SKIP.value)
        if not wait_click(self.serial, Gacha.CONFIRM.value):
            raise GameError("無法進行扭蛋")
        connection_retry(self.serial, appear=Gacha.TEXT.value, timeout=40.0)
        if not wait_click(self.serial, MainView.BACK.value, timeout=20.0):
            raise GameError("找不到返回鍵")
        connection_retry(self.serial, vanish=MainView.BACK.value, timeout=40.0)
    
    def _pre_skip_rene(self):
        if wait_click(self.serial, MainView.SKIP.value, timeout=30.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=3.0)

    def _rene_equip(self):
        wait_click(self.serial, Phase3UI.RENE.value, timeout=7.0, wait_time=4.0)
        if wait_click(self.serial, MainView.SKIP.value, timeout=10.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=1.0)
        wait_click(self.serial, MainView.SKIP.value, timeout=10.0, wait_time=2.0)
        wait_click(self.serial, Gear.ARROW.value, timeout=10.0)

        connection_retry(self.serial, appear=Gear.TEXT.value, retry=Gear.ARROW.value, timeout=40.0)
        if wait_click(self.serial, MainView.SKIP.value, timeout=5.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=3.0)
        wait_click(self.serial, Leonard.BG_POINT.value, wait_time=3)
        wait_click(self.serial, Leonard.BG_POINT.value, wait_time=3)
        wait_click(self.serial, Leonard.BG_HAPPY.value, wait_time=1.5)
        wait_click(self.serial, Phase3UI.EQUIP_SHIRT.value, wait_time=2)
        wait_click(self.serial, Gear.EQUIP.value, wait_time=1.5)
        wait_click(self.serial, MainView.SKIP.value, timeout=15.0, wait_time=1.5)
        wait_click(self.serial, MainView.SKIP.value, timeout=3.0, wait_time=3.0)
        wait_click(self.serial, MainView.BACK.value)

        connection_retry(self.serial, vanish=MainView.BACK.value, timeout=40.0)
    
    def _enter_main_stage(self):
        on_main_view(self.serial)
        main_stage_enter_menu(self.serial)
        wait_click(self.serial, MainView.BACK.value)
        on_main_view(self.serial)

    def _finish_main_stage(self, times: int = 1):
        def _step():
            for _ in range(times):
                main_stage_finish_new(self.serial)
        return _step

    def _detect_event(self):
        return 0

    def steps(self):
        return [
            self._login,
            self._finish_main_stage(4),
            self._on_main_view_rene,
            self.upgrade_rene,
            self._finish_main_stage(2),
            self._on_main_view_gacha,
            self.gacha_equip,
            self._pre_skip_rene,
            self._rene_equip,
            self._enter_main_stage
        ]