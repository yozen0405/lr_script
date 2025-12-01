from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.constants import Settlement, Confirm, Battle, Retry, MainView, Leonard
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

    def _close_pvp_in(self):
        cnt = 0
        while True:
            if exist_click(self.serial, PvP.LVL_DOWN.value):
                cnt = 0
                continue
            if exist_click(self.serial, Leonard.TP_POINT.value):
                cnt = 0
                continue
            if exist_click(self.serial, Leonard.TP_JUMP.value):
                cnt = 0
                continue
            if exist_click(self.serial, PvP.CLOSE_TIPS.value):
                cnt = 0
                continue
            if exist(self.serial, PvP.SEASON_END_TEXT.value, threshold=0.9):
                cnt = 0
                exist_click(self.serial, Confirm.SMALL.value)
                continue
            if exist(self.serial, PvP.TEXT.value, threshold=0.9):
                cnt += 1
                if cnt >= 2:
                    return
            

    def enter_menu(self):
        if exist(self.serial, PvP.TEXT.value, threshold=0.999):
            return
        
        for _ in range(5):
            if wait_click(self.serial, PvP.BTN.value):
                connection_retry(self.serial, vanish=[(PvP.BTN.value)], timeout=40.0)
                self._close_pvp_in()
                # 判賽季結算(或聯盟初始化) 跟 pvp介紹 跟 屬性關卡介紹 跟 降級
                return
            elif exist(self.serial, MainStage.BTN.value):
                drag(self.serial, (800, 400), (200, 400))
                drag(self.serial, (800, 400), (200, 400))
            elif exist(self.serial, PvP.TEXT.value):
                self._close_pvp_in()
                return

        raise GameError("無法進入特殊關卡")

    def enter_stage(self):
        for _ in range(3):
            wait_click(self.serial, PvP.BATTLE.value)
            if wait(self.serial, PvP.MATCHING_TEXT.value, timeout=3.0):
                break

        for _ in range(5):
            wait_click(self.serial, PvP.BATTLE.value)
            if wait(self.serial, PvP.MATCHING_TEXT.value, timeout=3.0):
                wait_click(self.serial, PvP.CHALLENGE.value)
                break
            if wait(self.serial, PvP.BLIND_MATCH.value, timeout=3.0):
                wait_click(self.serial, PvP.CHALLENGE.value)
                break
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.BTN.value)

        connection_retry(self.serial, appear=PvP.MATCHED.value, timeout=40.0)
        wait_click(self.serial, PvP.CHALLENGE.value)
        connection_retry(self.serial, appear=Battle.NEXT.value, timeout=40.0)

    def _cancel_match_up(self):
        wait_click(self.serial, Confirm.CANCEL.value)
        wait_click(self.serial, MainView.BACK.value)
        wait_click(self.serial, MainView.BACK.value)
        connection_retry(self.serial, appear=PvP.TEXT.value, timeout=40.0)

    def run(self):
        log_msg(self.serial, "PVP 任務開始")
        exist_click(self.serial, Battle.AUTO_BTN_OFF2.value, threshold=0.99)
        wait_click(self.serial, Battle.NEXT.value, wait_time=1.5)
        exist_click(self.serial, Leonard.TP_JUMP.value, wait_time=1.0)
        wait_click(self.serial, Battle.START.value)
        
        while True:
            if exist(self.serial, Battle.NO_FEATHER.value):
                self._cancel_match_up()
                return False
            if exist(self.serial, Battle.PAUSE.value, threshold=0.9):
                break
            if exist(self.serial, PvP.SETTLEMENT_TEXT.value):
                break
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.BTN.value)

        wait_vanish(self.serial, Battle.PAUSE.value, threshold=0.97, timeout=60.0)

        log_msg(self.serial, "結算中")
        self.settlement()
        log_msg(self.serial, "PVP 任務完成")
        return True

    def settlement(self):
        connection_retry(self.serial, appear=PvP.SETTLEMENT_TEXT.value, timeout=40.0)
        exist_click(self.serial, PvP.SETTLEMENT_TEXT.value)

        while True:
            if not exist(self.serial, PvP.SETTLEMENT_TEXT.value):
                time.sleep(2.0)
                wait(self.serial, PvP.TEXT.value, timeout=40.0, wait_time=3.0, threshold=0.9)
                exist_click(self.serial, PvP.LVL_UP.value, wait_time=2.0)
                return
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.TEXT1.value)

def pvp_loop_battle(serial):
    pvp = BasePvP(serial)
    pvp.enter_menu()
    pvp.enter_stage()
    return pvp.run()