import time
import os
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from core.base.exceptions import GameError
from scripts.shared.utils.game_view import close_board
from scripts.shared.events.special_stage.selector import special_stage_single_game
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.main_stage.selector import main_stage_finish_new, main_stage_enter_menu
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry, Positions
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.login.base import guest_login
from scripts.shared.events.teams.enum import Teams
from scripts.shared.events.gacha.enum import Gacha

from scripts.custom_scripts.new_acc.enum import Gear, Phase3UI, Phase4UI
from scripts.shared.events.special_stage.enum import Planet
from scripts.custom_scripts.new_acc.base import BasePhase

class Phase4(BasePhase):
    def _finish_main_stage(self, times: int = 1):
        def _step():
            for _ in range(times):
                main_stage_finish_new(self.serial)
        return _step

    def _upgrade_equip(self):
        on_main_view(self.serial)
        if wait_click(self.serial, MainView.SKIP.value, timeout=5.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=3.0)
        wait_click(self.serial, Phase3UI.RENE.value, timeout=7.0, wait_time=2.0)
        wait_click(self.serial, Gear.ARROW.value, timeout=10.0)
        connection_retry(self.serial, appear=Gear.TEXT.value, timeout=40.0)
        wait_click(self.serial, MainView.SKIP.value, timeout=5.0, wait_time=1.2)
        wait_click(self.serial, Phase4UI.SHIELD.value, timeout=5.0, wait_time=1.2)
        if wait_click(self.serial, MainView.SKIP.value, timeout=5.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=3.0)
        wait_click(self.serial, Gear.UPGRADE.value, timeout=5.0, wait_time=2.0, threshold=0.99)
        if wait_click(self.serial, MainView.SKIP.value, timeout=5.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=3.0)
        wait_click(self.serial, Phase4UI.SHIELD.value, timeout=5.0, wait_time=2.0)
        wait_click(self.serial, Gear.ENHANCE.value, timeout=5.0, wait_time=3.0)
        for _ in range(3):
            if not wait_click(self.serial, Gear.ENHANCE_SUCCESS.value, timeout=5.0, wait_time=1.5):
                break
        if wait_click(self.serial, MainView.SKIP.value, timeout=5.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=3.0)
        wait_click(self.serial, MainView.BACK.value)
        on_main_view(self.serial, timeout=40.0)

    def _introduce_scene(self):
        wait_click(self.serial, MainView.BACK.value)
        on_main_view(self.serial, sign=Gacha.SKIP.value, vanish=False, timeout=40.0)
        wait_click(self.serial, Gacha.SKIP.value, timeout=5.0, wait_time=2.0)
        special_stage_single_game(self.serial, planet=Planet.EVO_MINE.value, stage=1)
        wait_click(self.serial, MainView.BACK.value, wait_time=2.0)
    
    def _detect_event(self):
        return 0

    def steps(self):
        return [
            self._finish_main_stage(3),
            self._upgrade_equip,
            self._finish_main_stage(10),
            self._introduce_scene,
        ]