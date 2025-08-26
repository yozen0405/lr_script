from enum import Enum

from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from core.actions.system import force_close
from core.base.exceptions import GameError
from scripts.shared.utils.game_view import close_board, on_main_view
from scripts.shared.utils.retry import connection_retry
from scripts.shared.events.login import guest_login
from scripts.shared.events.main_stage.selector import main_stage_finish_new, main_stage_enter_menu
from scripts.shared.events.main_stage.enum import Treasure, MainStage

from scripts.shared.events.teams.enum import Teams
from scripts.shared.constants import MainView, Confirm
from scripts.custom_scripts.new_acc.enum import Quests  
from scripts.custom_scripts.new_acc.enum import Phase2UI

class Phase2:
    def __init__(self, serial):
        self.serial = serial

    def _maybe_skip_and_confirm(self, skip_timeout=5.0, confirm_wait=0.5):
        if wait_click(self.serial, MainView.SKIP.value, timeout=skip_timeout):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=confirm_wait)
            return True
        return False

    def _login_second(self):
        log_msg(self.serial, "二次登入")
        guest_login(self.serial)
        if wait(self.serial, MainView.SETTINGS.value, timeout=40.0):
            close_board(self.serial)

    def _second_stage(self):
        log_msg(self.serial, "打主要關卡 stage 2")
        self._maybe_skip_and_confirm(skip_timeout=3.0, confirm_wait=0.5)
        main_stage_finish_new(self.serial)

    def _claim_treasure(self):
        log_msg(self.serial, "尋找寶物")
        on_main_view(self.serial, sign=MainView.BACK.value, vanish=True)

        self._maybe_skip_and_confirm(skip_timeout=20.0, confirm_wait=0.5)

        main_stage_enter_menu(self.serial)

        if not wait_click(self.serial, Treasure.ICON.value, timeout=40.0):
            raise GameError("無法進入寶物")

        if not wait(self.serial, Treasure.TEXT.value, timeout=30.0):
            raise GameError("不在寶物室，強制停止")

        self._maybe_skip_and_confirm(skip_timeout=20.0, confirm_wait=0.5)

        if wait_click(self.serial, MainView.BACK.value, timeout=20.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=0.5)

        main_stage_finish_new(self.serial)
        wait_click(self.serial, MainView.BACK.value, timeout=10.0)
        on_main_view(self.serial, sign=MainView.BACK.value, vanish=True)

        self._maybe_skip_and_confirm(skip_timeout=5.0, confirm_wait=0.5)

        wait_click(self.serial, Quests.LONG.value, timeout=7.0)
        wait_click(self.serial, MainView.CLOSE_BOARD.value, timeout=10.0)

    def _seven_days(self):
        wait_click(self.serial, MainView.BACK.value)
        on_main_view(self.serial, sign=MainView.BACK.value, vanish=True)

        self._maybe_skip_and_confirm(skip_timeout=5.0, confirm_wait=0.5)

        wait_click(self.serial, Quests.SEVEN_DAYS.value, timeout=7.0)
        if self._maybe_skip_and_confirm(skip_timeout=10.0, confirm_wait=0.5):
            pass
        wait_click(self.serial, Quests.SEVEN_DAYS_INFO.value, timeout=7.0)
        wait_click(self.serial, MainView.CLOSE_BOARD.value, timeout=10.0, wait_time=1.0)
        wait_click(self.serial, MainView.CLOSE_BOARD.value, timeout=10.0)

    def _upgrade_sheep(self):
        on_main_view(self.serial, sign=MainView.BACK.value, vanish=True)

        if self._maybe_skip_and_confirm(skip_timeout=5.0, confirm_wait=3.0):
            pass

        wait_click(self.serial, Phase2UI.SHEEP.value, timeout=7.0, wait_time=2.0)
        wait_click(self.serial, Teams.UPGRADE_BTN.value)

        if not wait(self.serial, MainView.BACK.value, timeout=20.0):
            raise GameError("無法進入升級頁面")

        drag(self.serial, (80, 574), (478, 341), wait_time=3.0, timeout=10.0)
        wait_click(self.serial, Teams.UPGRADE_LVL_BTN.value)

        for _ in range(3):
            wait_click(self.serial, Teams.UPGRADE_SUCCESS.value, timeout=5.0, wait_time=1.0)

        if self._maybe_skip_and_confirm(skip_timeout=15.0, confirm_wait=0.5):
            pass

        wait_click(self.serial, MainView.BACK.value)

    def _back_to_close_board(self):
        if not wait(self.serial, MainStage.TEXT.value, timeout=15.0):
            raise GameError("不在主畫面")
        wait_click(self.serial, MainView.BACK.value)
        on_main_view(self.serial, sign=MainView.BACK.value, vanish=True)
        force_close(self.serial)

    def run(self):
        if exist(self.serial, Quests.LONG.value, threshold=0.65):
            return
        if exist(self.serial, MainView.CLOSE_BOARD.value):
            return

        self._login_second()
        self._second_stage()
        self._claim_treasure()
        main_stage_finish_new(self.serial)
        self._seven_days()
        main_stage_finish_new(self.serial)
        self._upgrade_sheep()
        main_stage_finish_new(self.serial)
        self._back_to_close_board()


def phase2(serial):
    runner = Phase2(serial)
    runner.run()