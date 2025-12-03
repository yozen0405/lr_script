import time
import os
from core.system.logger import log_msg
from core.actions.screen import (
    wait_click, exist_click, exist, wait,
    wait_vanish, back, drag
)
from core.actions.system import (
    force_close_all_apps,
    clear_game_storage
)
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.gacha.base import BaseGacha
from scripts.shared.events.url.base import LinkNavigator
from core.base.exceptions import GameError
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry, Positions
from scripts.custom_scripts.new_acc.enum import Phase6UI
from scripts.custom_scripts.new_acc.base import BasePhase

class Phase6(BasePhase):
    def _nav_link(self):
        link_nav = LinkNavigator(self.serial)
        link_nav.run()

    def _claim_tickets(self):
        wait_click(self.serial, Phase6UI.GIFT.value, timeout=7.0, wait_time=2.0)
        connection_retry(self.serial, appear=Phase6UI.GIFT_TEXT.value, retry=Phase6UI.GIFT.value, timeout=40.0)
        if not wait_click(self.serial, Phase6UI.ACCEPT_ALL.value, timeout=15.0):
            wait_click(self.serial, MainView.CLOSE_BOARD.value)
            return
        wait_click(self.serial, Confirm.SMALL.value, timeout=15.0, wait_time=3.0)
        wait_click(self.serial, Confirm.SMALL.value, wait_time=1.5)
        wait_click(self.serial, MainView.CLOSE_BOARD.value, wait_time=1.5)

    def _gacha_pull(self):
        gacha = BaseGacha(self.serial)
        gacha.enter_gacha()
        gacha.pull()
        force_close_all_apps(self.serial)
        clear_game_storage(self.serial)

    def _detect_event(self):
        return 0

    def steps(self):
        return [
            self._nav_link,
            self._claim_tickets,
            self._gacha_pull,
        ]