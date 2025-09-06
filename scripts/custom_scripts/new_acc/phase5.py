import time
import os
from core.system.logger import log_msg
from core.actions.screen import (
    wait_click, exist_click, exist,
    wait, wait_vanish,
    back, drag,
    get_pos
)
from core.base.exceptions import GameError
from scripts.shared.utils.game_view import close_board
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.main_stage.selector import main_stage_finish_new, main_stage_finish_custom
from scripts.shared.constants import GameView, Settlement, Battle, Confirm, MainView, Leonard, Retry, Positions
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.login import guest_login
from scripts.shared.events.teams.enum import Teams
from scripts.shared.events.gacha.enum import Gacha

from scripts.custom_scripts.new_acc.enum import Phase5UI, Gear, Diamond, SeasonPass, SevenDays
from scripts.custom_scripts.new_acc.base import BasePhase

class Phase5(BasePhase):
    def _finish_main_stage(self, times: int = 1):
        def _step():
            for _ in range(times):
                main_stage_finish_new(self.serial)
        return _step

    def _james_friend(self):
        on_main_view(self.serial)
        if wait_click(self.serial, MainView.SKIP.value, timeout=5.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=3.0)
        main_stage_finish_new(self.serial)

    def _stage30(self):
        main_stage_finish_custom(self.serial, custom_stage=30)

    def _do_team_upgrade(self):
        if not wait_click(self.serial, MainView.BACK.value):
            raise GameError("未知狀態")
        on_main_view(self.serial)
        wait_click(self.serial, Teams.ICON_LIGHT.value)
        connection_retry(self.serial, appear=Teams.TEXT.value, retry=Teams.ICON_LIGHT.value, timeout=40.0)
        wait_click(self.serial, Leonard.TP_POINT.value)
        wait_click(self.serial, Leonard.TP_HAPPY.value, wait_time=2.0)
        wait_click(self.serial, Phase5UI.JESSICA.value, wait_time=1.5)
        wait_click(self.serial, Teams.UPGRADE_BTN.value)
        connection_retry(self.serial, appear=MainView.BACK.value, retry=Teams.UPGRADE_BTN.value, timeout=40.0)
        time.sleep(3.0)
        for _ in range(2):
            drag(self.serial, (449, 605), (449, 357), timeout=10.0)
        wait_click(self.serial, Teams.UPGRADE_LVL_BTN.value)
        if not wait_click(self.serial, Confirm.SMALL.value, wait_time=3.0):
            raise GameError("升級失敗")

        connection_retry(self.serial, appear=Teams.UPGRADE_SUCCESS.value, retry=[(Teams.UPGRADE_LVL_BTN.value), (Confirm.SMALL.value)], timeout=40.0)

        for _ in range(3):
            if not wait_click(self.serial, Teams.UPGRADE_SUCCESS.value, timeout=5.0, wait_time=1.0):
                break
        wait_click(self.serial, MainView.BACK.value)
        wait(self.serial, Teams.TEXT.value, timeout=20.0)
        wait_click(self.serial, MainView.BACK.value, timeout=20.0)
        on_main_view(self.serial, timeout=40.0)

    def _do_diamond_upgrade(self):
        wait_click(self.serial, Diamond.ICON.value)
        connection_retry(self.serial, appear=Diamond.UPGRADE_TEXT.value, retry=Diamond.ICON.value, timeout=40.0)
        pos = get_pos(self.serial, Diamond.UPGRADE_TEXT.value)
        if not pos:
            raise GameError("找不到升級文字")
        x, y = pos
        wait_click(self.serial, (x, y + 350))
        if not wait_click(self.serial, Diamond.MAX.value):
            raise GameError("無法升級")
        for _ in range(7):
            wait_click(self.serial, Diamond.MINUS.value)
        wait_click(self.serial, Confirm.SMALL.value, wait_time=1.0)
        connection_retry(self.serial, appear=Diamond.SUCCESS.value, timeout=40.0)
        for _ in range(3):
            wait_click(self.serial, Diamond.SUCCESS.value, timeout=5.0, wait_time=1.0)
            if wait_click(self.serial, MainView.BACK.value):
                break
        connection_retry(self.serial, vanish=MainView.BACK.value, retry=MainView.BACK.value, timeout=40.0)

    def _claim_seven_day(self):
        wait_click(self.serial, SevenDays.ICON.value)
        connection_retry(self.serial, appear=SevenDays.QUEST_REWARD.value, retry=SevenDays.ICON.value, timeout=40.0)
        pos = get_pos(self.serial, SevenDays.QUEST_REWARD.value)
        if not pos:
            raise GameError("找不到升級文字")
        x, y = pos
        wait_click(self.serial, (x + 500, y), wait_time=1.0)
        wait_click(self.serial, Confirm.SMALL.value, timeout=10.0)
        wait_click(self.serial, SevenDays.DAILY_REWARD.value, timeout=10.0, wait_time=1.0)
        wait_click(self.serial, Confirm.SMALL.value, timeout=10.0)
        if not wait(self.serial, SevenDays.CLAIM.value):
            raise GameError("沒領到扭蛋卷")
        wait_click(self.serial, MainView.CLOSE_BOARD.value)

    def _claim_single_reward(self):
        wait_click(self.serial, SeasonPass.CLAIM.value, wait_time=2.0)

        while True:
            if exist(self.serial, Retry.TEXT2.value):
                exist_click(self.serial, Confirm.SMALL.value, wait_time=1.0)
                wait_click(self.serial, SeasonPass.CLAIM.value)
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.BTN.value)
            if exist(self.serial, SeasonPass.CLAIMED_TEXT.value, threshold=0.9):
                exist_click(self.serial, Confirm.SMALL.value, wait_time=2.0)
                return

    def _claim_season_pass(self):
        wait_click(self.serial, SeasonPass.ICON.value, timeout=7.0)
        connection_retry(self.serial, appear=Confirm.SMALL.value, retry=SeasonPass.ICON.value, timeout=40.0)
        wait_click(self.serial, Confirm.SMALL.value, timeout=10.0)
        for _ in range(13):
            wait_click(self.serial, SeasonPass.TEXT.value, wait_time=1.5)
        wait(self.serial, SeasonPass.TEXT.value, timeout=10.0, threshold=0.99)
        
        for _ in range(2):
            wait_click(self.serial, SeasonPass.DAILY_NAV.value, timeout=10.0, wait_time=1.0)
        for _ in range(3):
            self._claim_single_reward()

        wait_click(self.serial, SeasonPass.WEELKY_NAV.value, timeout=10.0, wait_time=1.0)
        self._claim_single_reward()
        
        if wait(self.serial, SeasonPass.TEXT.value, timeout=10.0, threshold=0.99):
            wait_click(self.serial, SeasonPass.PASS_NAV.value, timeout=10.0, wait_time=1.0)
            wait_click(self.serial, Phase5UI.SEASON_PASS_TICKETS.value, timeout=10.0, wait_time=2.0)
            connection_retry(self.serial, appear=SeasonPass.CONGRATS.value, retry=Phase5UI.SEASON_PASS_TICKETS.value, timeout=40.0)
            wait_click(self.serial, Confirm.BIG1.value, wait_time=2.0, threshold=0.65)
            connection_retry(self.serial, appear=SeasonPass.HISTORY_TEXT.value, retry=Confirm.BIG1.value, timeout=40.0)
            if wait(self.serial, Phase5UI.SEASON_PASS_LVL1.value, timeout=60.0):
                wait_click(self.serial, MainView.CLOSE_BOARD.value, timeout=10.0)
            else:
                raise GameError("季票領取獎勵錯誤")
        else:
            raise GameError("季票領取獎勵錯誤")
        
        wait_click(self.serial, MainView.BACK.value)
        connection_retry(self.serial, vanish=MainView.BACK.value, timeout=40.0)
        on_main_view(self.serial)

    def _detect_event(self):
        return 0

    def steps(self):
        return [
            self._finish_main_stage(4),
            self._james_friend,
            self._stage30,
            self._do_team_upgrade,
            self._do_diamond_upgrade,
            self._claim_seven_day,
            self._claim_season_pass,
        ]