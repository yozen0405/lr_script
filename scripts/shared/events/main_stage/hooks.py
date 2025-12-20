import time
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.ocr import get_main_stage_num
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.main_stage.enum import MainStage, Stages, Treasure

class MainStageHooks:
    def __init__(self, serial):
        self.serial = serial

    def on_pre_start_page_prev(self, base):
        pass

    def on_pre_start_page_next(self, base):
        pass

    def on_start_page(self, base):
        pass

    def on_settlement_page(self, base):
        pass

    def on_settlement_next_feature(self, base):
        if not exist(self.serial, MainStage.NEXT_FEATURE.value):
            return
        wait_click(self.serial, Settlement.AGAIN.value, wait_time=1.2)
        wait_click(self.serial, Settlement.NEXT.value)

    def handle_multiplier(self, times, base):
        if not exist(self.serial, Battle.MULTIPLIER_OFF.value):
            return
        for _ in range(5):
            if base.is_low:
                did_found = exist(self.serial, MainStage.MULTIPLIER_LOW_BTN(times=times), threshold=0.9)
            else:
                did_found = exist(self.serial, MainStage.MULTIPLIER_HIGH_BTN(times=times), threshold=0.9)

            if did_found:
                return
            exist_click(self.serial, Battle.MULTIPLIER_OFF.value, wait_time=0.5)

    def handle_loop_stage_tutorial(self, base):
        if not wait(self.serial, Battle.MULTIPLIER_TEXT.value, timeout=2.0):
            return
        wait_click(self.serial, Battle.CYCLE.value, wait_time=2.5)
        wait_click(self.serial, Leonard.BG_POINT.value, wait_time=2.5)
        wait_click(self.serial, Battle.MULTIPLIER_OFF.value, wait_time=1.0)
        wait_click(self.serial, Battle.MULTIPLIER_ON.value, wait_time=1.0)
        wait_click(self.serial, Leonard.BG_HAPPY.value, wait_time=1.0)

    def handle_team_num(self, base):
        if base.is_low:
            if not exist_click(self.serial, MainStage.TEAM_BTN_LOW.value):
                return
            if exist_click(self.serial, MainStage.TEAM_NUM_LOW_ON(num=base.team_num), threshold=0.999):
                return
            elif exist_click(self.serial, MainStage.TEAM_NUM_LOW_OFF(num=base.team_num), threshold=0.9):
                return
            elif not exist_click(self.serial, MainStage.TEAM_NUM_LOW_ON(num=1), threshold=0.9):
                raise GameError("無法設定隊伍人數")
        else:
            if not exist_click(self.serial, MainStage.TEAM_BTN_HIGH.value):
                return
            if exist_click(self.serial, MainStage.TEAM_NUM_HIGH_ON(num=base.team_num), threshold=0.999):
                return
            exist_click(self.serial, MainStage.TEAM_NUM_HIGH_OFF(num=base.team_num), threshold=0.9)

    def handle_auto_btn(self, base):
        if base.is_low:
            exist_click(self.serial, MainStage.AUTO_BTN_LOW_OFF.value, threshold=0.99)
        else:
            exist_click(self.serial, MainStage.AUTO_BTN_HIGH_OFF.value, threshold=0.99)

    def settlement_items(self, base):
        return [
            Settlement.ACQUIRED.value,
            (Confirm.BIG1.value, 0.9),
            (Confirm.BIG2.value, 0.9),
            Settlement.ONE_REWARD.value,
            (Confirm.SMALL2.value, 0.9),
            Settlement.STOP.value,
            (MainStage.SETTLEMENT.value, 0.9)
        ]