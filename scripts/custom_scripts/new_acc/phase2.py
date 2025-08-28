from enum import Enum

from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from core.actions.system import force_close
from core.base.exceptions import GameError
from scripts.shared.utils.game_view import close_board, on_main_view
from scripts.shared.utils.retry import connection_retry
from scripts.shared.events.login import guest_login
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.events.main_stage.selector import main_stage_finish_new, main_stage_enter_menu
from scripts.shared.events.main_stage.enum import Treasure, MainStage

from scripts.shared.events.teams.enum import Teams
from scripts.shared.constants import MainView, Confirm
from scripts.custom_scripts.new_acc.enum import Quests  
from scripts.custom_scripts.new_acc.enum import Phase2UI, Phase1UI, SevenDays
from scripts.custom_scripts.new_acc.base import BasePhase

class Phase2(BasePhase):
    def _maybe_skip_and_confirm(self, skip_timeout=5.0, confirm_wait=0.5):
        if wait_click(self.serial, MainView.SKIP.value, timeout=skip_timeout):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=confirm_wait)
            return True
        return False
    
    def _login(self):
        log_msg(self.serial, "二次登入")
        guest_login(self.serial)
        if wait(self.serial, MainView.SETTINGS.value, timeout=40.0):
            close_board(self.serial)
    
    def _finish_main_stage(self):
        main_stage_finish_new(self.serial)

    def _finish_main_and_back(self):
        main_stage_finish_new(self.serial)
        wait_click(self.serial, MainView.BACK.value, timeout=10.0)
        on_main_view(self.serial, sign=MainView.BACK.value, vanish=True)

    def _second_stage(self):
        log_msg(self.serial, "打主要關卡 stage 2")
        self._maybe_skip_and_confirm(skip_timeout=3.0, confirm_wait=0.5)
        main_stage_finish_new(self.serial)
        on_main_view(self.serial, sign=MainView.BACK.value, vanish=True)

    def _claim_treasure(self):
        log_msg(self.serial, "尋找寶物")
        self._maybe_skip_and_confirm(skip_timeout=20.0, confirm_wait=0.5)

        main_stage_enter_menu(self.serial)

        if not wait_click(self.serial, Treasure.ICON.value, timeout=40.0):
            raise GameError("無法進入寶物")

        if not wait(self.serial, Treasure.TEXT.value, timeout=30.0):
            raise GameError("不在寶物室，強制停止")

        self._maybe_skip_and_confirm(skip_timeout=20.0, confirm_wait=0.5)

        if wait_click(self.serial, MainView.BACK.value, timeout=20.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=0.5)

    def _long_quest(self):
        self._maybe_skip_and_confirm(skip_timeout=5.0, confirm_wait=0.5)

        wait_click(self.serial, Quests.LONG.value, timeout=7.0)
        connection_retry(self.serial, appear=MainView.CLOSE_BOARD.value, retry=Quests.LONG.value, timeout=40.0)
        wait_click(self.serial, MainView.CLOSE_BOARD.value, timeout=10.0)

    def _seven_days(self):
        wait_click(self.serial, MainView.BACK.value)
        on_main_view(self.serial, sign=MainView.BACK.value, vanish=True)

        self._maybe_skip_and_confirm(skip_timeout=5.0, confirm_wait=0.5)

        wait_click(self.serial, SevenDays.ICON.value, timeout=7.0)
        connection_retry(self.serial, appear=SevenDays.TEXT.value, retry=SevenDays.ICON.value, timeout=40.0)
        if self._maybe_skip_and_confirm(skip_timeout=10.0, confirm_wait=0.5):
            pass
        wait_click(self.serial, SevenDays.INFO.value, timeout=7.0)
        wait_click(self.serial, MainView.CLOSE_BOARD.value, timeout=10.0, wait_time=1.0)
        wait_click(self.serial, MainView.CLOSE_BOARD.value, timeout=10.0)

    def _upgrade_sheep(self):
        on_main_view(self.serial)

        self._maybe_skip_and_confirm(skip_timeout=5.0, confirm_wait=3.0)

        wait_click(self.serial, Phase2UI.SHEEP.value, timeout=7.0, wait_time=2.0)
        connection_retry(self.serial, appear=Teams.UPGRADE_BTN.value, retry=Phase2UI.SHEEP.value, timeout=40.0)
        wait_click(self.serial, Teams.UPGRADE_BTN.value)

        if not wait(self.serial, MainView.BACK.value, timeout=20.0):
            raise GameError("無法進入升級頁面")

        drag(self.serial, (80, 574), (478, 341), wait_time=3.0, timeout=10.0)
        wait_click(self.serial, Teams.UPGRADE_LVL_BTN.value)
        connection_retry(self.serial, appear=Teams.UPGRADE_SUCCESS.value, retry=Teams.UPGRADE_LVL_BTN.value, timeout=40.0)

        for _ in range(3):
            wait_click(self.serial, Teams.UPGRADE_SUCCESS.value, timeout=5.0, wait_time=1.0)

        self._maybe_skip_and_confirm(skip_timeout=15.0, confirm_wait=0.5)

        wait_click(self.serial, MainView.BACK.value)

    def _back_to_close_board(self):
        if not wait(self.serial, MainStage.TEXT.value, timeout=15.0):
            raise GameError("不在主畫面")
        wait_click(self.serial, MainView.BACK.value)
        on_main_view(self.serial, sign=MainView.BACK.value, vanish=True)
        force_close(self.serial)

    def _detect_event(self):
        return 0
        # if exist(self.serial, Phase1UI.LVL2_TEXT.value):
        #     return 1
        # if exist(self.serial, Phase2UI.SHEEP.value):
        #     if exist(self.serial, Phase2UI.SHEEP_UPGRADE_TEXT.value):
        #         return 6
        #     else:
        #         return 7
        
    def steps(self):
        return [
            self._login,
            self._second_stage,
            self._claim_treasure,
            self._finish_main_and_back,
            self._long_quest,
            self._finish_main_stage,
            self._seven_days,
            self._finish_main_stage,
            self._upgrade_sheep,
            self._finish_main_stage,
            self._back_to_close_board
        ]