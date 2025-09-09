from scripts.shared.events.season_pass.enum import SeasonPass
from scripts.shared.constants import Confirm, MainView, Retry
from core.actions.screen import wait_click, exist_click, exist, wait
from scripts.shared.utils.retry import connection_retry
import time

class SeasonPassClaimer:
    def __init__(self, serial):
        self.serial = serial

    def enter_menu(self):
        if exist(self.serial, SeasonPass.TEXT.value, threshold=0.9):
            return

        if wait(self.serial, SeasonPass.ICON.value, timeout=20.0, wait_time=1.0):
            wait_click(self.serial, SeasonPass.ICON.value, timeout=7.0)
            connection_retry(self.serial, vanish=SeasonPass.ICON.value, retry=SeasonPass.ICON.value, timeout=40.0)
            time.sleep(1.0)
        else:
            raise Exception("不在主畫面")

    def claim_single_reward(self):
        wait_click(self.serial, SeasonPass.CLAIM.value, wait_time=2.0)
        while True:
            if exist(self.serial, Retry.TEXT2.value):
                exist_click(self.serial, Confirm.SMALL.value, wait_time=1.0)
                wait_click(self.serial, SeasonPass.CLAIM.value)
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.BTN.value)
            if exist(self.serial, SeasonPass.CLAIMED_TEXT.value, threshold=0.9):
                exist_click(self.serial, Confirm.SMALL.value, wait_time=0.3)
                return

    def claim(self):
        exist_click(self.serial, Confirm.SMALL.value)
        exist_click(self.serial, SeasonPass.DAILY_NAV.value)

        for _ in range(10):
            if not exist(self.serial, SeasonPass.CLAIM.value, threshold=0.99):
                break
            self.claim_single_reward()

        wait_click(self.serial, MainView.BACK.value)
        connection_retry(self.serial, vanish=MainView.BACK.value, timeout=40.0)

def claim_season_pass(serial):
    claimer = SeasonPassClaimer(serial)
    claimer.enter_menu()
    claimer.claim()