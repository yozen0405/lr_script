from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos, check_region_brightness
from scripts.shared.constants import Settlement, Confirm, Battle, Retry, MainView, Leonard
from scripts.shared.constants.view import GameView
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.utils.retry import connection_retry
from scripts.shared.events.pvp.enum import PvP
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from scripts.shared.utils.hacks import apply_mode
import time

class BasePvP:
    def __init__(self, serial):
        self.serial = serial

    def _close_pvp_in(self):
        loc = get_pos(self.serial, PvP.TEXT.value, threshold=0.9, return_center=False)
        if loc:
            if check_region_brightness(self.serial, region=loc, threshold=50):
                return

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
            elif exist(self.serial, MainStageImg.BTN.value):
                drag(self.serial, (800, 400), (200, 400))
                drag(self.serial, (800, 400), (200, 400))
            elif exist(self.serial, PvP.TEXT.value):
                self._close_pvp_in()
                return

        raise GameError("無法進入特殊關卡")

    def enter_stage(self):
        start_time = time.time()
        found = False
        while time.time() - start_time < 120.0:
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.BTN.value)

            if exist_click(self.serial, PvP.BATTLE.value):
                pass

            if exist(self.serial, PvP.MATCHING_TEXT.value, threshold=0.8):
                wait_click(self.serial, PvP.CHALLENGE.value)
                found = True

            if exist(self.serial, PvP.BLIND_MATCH.value, threshold=0.8):
                wait_click(self.serial, PvP.CHALLENGE.value)
                found = True

            if found:
                if exist(self.serial, PvP.PRE_START_PAGE.value, threshold=0.9):
                    return
        raise GameError("無法進入PVP戰鬥頁面")
                
    def _cancel_match_up(self):
        wait_click(self.serial, Confirm.CANCEL_SMALL.value)
        wait_click(self.serial, MainView.BACK.value)
        wait_click(self.serial, MainView.BACK.value)
        connection_retry(self.serial, appear=PvP.TEXT.value, timeout=40.0)

    def run(self):
        log_msg(self.serial, "PVP 任務開始")
        exist_click(self.serial, Battle.AUTO_BTN_OFF2.value, threshold=0.99)
        wait_click(self.serial, Battle.NEXT.value, wait_time=1.5)
        exist_click(self.serial, Leonard.TP_JUMP.value, wait_time=1.0)
        wait_click(self.serial, Battle.START.value)
        
        start_time = time.time()
        while time.time() - start_time < 240.0:
            if exist(self.serial, Battle.NO_FEATHER.value):
                self._cancel_match_up()
                return False
            if exist(self.serial, Battle.PAUSE.value, threshold=0.9):
                break
            if exist(self.serial, PvP.SETTLEMENT_TEXT.value):
                break
            if exist(self.serial, GameView.ICON.value):
                raise GameError("遊戲回到主畫面，可能因為斷線或異常退出")
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.BTN.value)

        wait_vanish(self.serial, Battle.PAUSE.value, threshold=0.97, timeout=60.0)

        log_msg(self.serial, "結算中")
        self.settlement()
        log_msg(self.serial, "PVP 任務完成")
        return True

    def settlement(self):
        connection_retry(self.serial, appear=PvP.SETTLEMENT_TEXT.value, timeout=40.0)

        start_time = time.time()
        while time.time() - start_time < 120.0:
            if not exist(self.serial, PvP.SETTLEMENT_TEXT.value, wait_time=1.5):
                if exist(self.serial, Settlement.PUZZLE_FOUND_TEXT.value):
                    exist_click(self.serial, Confirm.BIG2.value)
                    continue

                if not exist(self.serial, PvP.TEXT.value, wait_time=3.0, threshold=0.9):
                    continue
                else:
                    wait_click(self.serial, PvP.LVL_UP.value, timeout=3.0, wait_time=2.0)
                    return
            else:
                exist_click(self.serial, PvP.SETTLEMENT_TEXT.value)
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.TEXT1.value)
        raise GameError("結算過程異常")

def pvp_loop_battle(serial):
    pvp = BasePvP(serial)
    pvp.enter_menu()
    pvp.enter_stage()
    return pvp.run()