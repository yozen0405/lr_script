from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.constants import Settlement, Confirm, Battle, Retry, MainView
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.utils.retry import connection_retry
from scripts.shared.events.pvp.enum import PvP
from core.base.exceptions import GameError
from core.system.logger import log_msg
from scripts.shared.utils.hacks import apply_mode
import time

class BasePvP:
    def __init__(self, serial):
        self.serial = serial

    def enter_menu(self):
        if exist(self.serial, PvP.TEXT, threshold=0.9):
            return
        
        for _ in range(5):
            if wait_click(self.serial, PvP.BTN):
                connection_retry(self.serial, image_name=PvP.BTN, exception_msg="不在主畫面", timeout=40.0)
                # 判賽季結算(或聯盟初始化) 跟 pvp介紹 跟 屬性關卡介紹 跟 降級
                return
            elif exist(self.serial, MainStage.BTN):
                drag(self.serial, (800, 400), (200, 400))
                drag(self.serial, (800, 400), (200, 400))

        raise GameError("無法進入特殊關卡")

    def enter_stage(self):
        for _ in range(3):
            wait_click(self.serial, PvP.BATTLE)
            if wait(self.serial, PvP.MATCHING_TEXT, timeout=3.0):
                break

        for _ in range(5):
            wait_click(self.serial, PvP.BATTLE)
            if wait(self.serial, PvP.MATCHING_TEXT, timeout=3.0):
                wait_click(self.serial, PvP.CHALLENGE)
                break
            if wait(self.serial, PvP.BLIND_MATCH, timeout=3.0):
                wait_click(self.serial, PvP.CHALLENGE)
                break
            if exist(self.serial, Retry.TEXT1):
                exist_click(self.serial, Retry.BTN)

        connection_retry(self.serial, wait_name=PvP.MATCHED, timeout=40.0)
        wait_click(self.serial, PvP.CHALLENGE)
        connection_retry(self.serial, wait_name=Battle.NEXT, timeout=40.0)

    def _cancel_match_up(self):
        wait_click(self.serial, Confirm.CANCEL)
        wait_click(self.serial, MainView.BACK)
        wait_click(self.serial, MainView.BACK)
        connection_retry(self.serial, wait_name=PvP.TEXT, timeout=40.0)

    def run(self):
        log_msg(self.serial, "PVP 任務開始")
        exist_click(self.serial, Battle.AUTO_BTN_OFF2, threshold=0.99)
        wait_click(self.serial, Battle.NEXT)
        wait_click(self.serial, Battle.START)

        while True:
            if exist(self.serial, Battle.NO_FEATHER):
                self._cancel_match_up()
                return False
            if exist(self.serial, Battle.PAUSE, threshold=0.9):
                break
            if exist(self.serial, Retry.TEXT1):
                exist_click(self.serial, Retry.BTN)

        wait_vanish(self.serial, Battle.PAUSE, threshold=0.97, timeout=60.0)

        log_msg(self.serial, "結算中")
        self.settlement()
        log_msg(self.serial, "PVP 任務完成")
        return True

    def settlement(self):
        connection_retry(self.serial, wait_name=PvP.SETTLEMENT_TEXT, timeout=40.0)
        exist_click(self.serial, PvP.SETTLEMENT_TEXT)

        while True:
            if not exist(self.serial, PvP.SETTLEMENT_TEXT):
                time.sleep(2.0)
                wait(self.serial, PvP.TEXT, timeout=40.0, wait_time=3.0, threshold=0.9)
                exist_click(self.serial, PvP.LVL_UP, wait_time=2.0)
                return
            if exist(self.serial, Retry.TEXT1):
                exist_click(self.serial, Retry.TEXT1)

def pvp_loop_battle(serial):
    pvp = BasePvP(serial)
    pvp.enter_menu()
    pvp.enter_stage()
    return pvp.run()