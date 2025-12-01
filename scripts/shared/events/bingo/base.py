from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.screen import back
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logger import log_msg
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.bingo.enum import Bingo, BingoAdPositions

class BingoBase:
    def __init__(self, serial):
        self.serial = serial
        self.BINGO_CLOSE_AD_LEN = 14

    def enter_menu(self):
        if exist(self.serial, Bingo.TEXT.value):
            return
        
        for _ in range(5):
            if wait_click(self.serial, Bingo.BTN.value):
                connection_retry(self.serial, vanish=Bingo.BTN.value, timeout=40.0)
                self._on_pre_anime()
                return
            elif exist(self.serial, MainStage.BTN.value):
                drag(self.serial, (800, 400), (200, 400))

        raise GameError("無法進入賓果活動")
    
    def _on_pre_anime(self):
        pass

    def _claim_mission(self):
        if not exist_click(self.serial, Bingo.MISSION_ON.value, threshold=0.999):
            return
        
        connection_retry(self.serial, appear=Bingo.MISSION_TEXT.value, timeout=40.0)
        while True:
            if exist(self.serial, Bingo.MISSION_CLAIMED_TEXT.value, threshold=0.9):
                exist_click(self.serial, Confirm.SMALL.value)
            elif exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Confirm.SMALL.value)
            elif wait_click(self.serial, Bingo.GET.value, timeout=3.0):
                continue
            else:
                wait_click(self.serial, MainView.CLOSE_BOARD2.value, threshold=0.9, timeout=3.0)
                if not wait_vanish(self.serial, MainView.CLOSE_BOARD2.value, threshold=0.9, timeout=3.0):
                    continue
                else:
                    break

    def _wait_bingo_text(self) -> int:
        for _ in range(30):
            if wait(self.serial, Bingo.REDRAW.value, timeout=3.0):
                log_msg(self.serial,"抽到重複的，繼續抽獎")
                return 1
            elif wait(self.serial, Bingo.DUPLICATE_TEXT.value, timeout=3.0, threshold=0.99):
                if exist(self.serial, Bingo.REDRAW.value, threshold=0.9):
                    continue
                log_msg(self.serial,"抽到重複的，而且沒廣告看了")
                exist_click(self.serial, Confirm.SMALL.value)
                connection_retry(self.serial, vanish=Bingo.DUPLICATE_TEXT.value, timeout=40.0)
                return 2
            elif wait(self.serial, Bingo.GOT_NEW_TEXT.value, timeout=3.0, threshold=0.99):
                wait_click(self.serial, Confirm.SMALL.value)
                connection_retry(self.serial, vanish=Bingo.GOT_NEW_TEXT.value, timeout=40.0)
                log_msg(self.serial, "抽到新的")
                return 0
            elif wait(self.serial, Bingo.NO_AD_TEXT.value, timeout=3.0, threshold=0.99):
                exist_click(self.serial, Confirm.SMALL.value)
                wait_click(self.serial, Bingo.RANDOM.value)
                return
            elif exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Confirm.SMALL.value)
        raise GameError("無法確認抽獎結果")

    def _do_random(self):
        if not exist(self.serial, Bingo.REDRAW.value):
            wait_click(self.serial, Bingo.RANDOM.value)
            # if exist(self.serial, Bingo.NO_TICKETS_TEXT.value):
            #     log_msg(self.serial,"沒有賓果券了")
            #     exist_click(self.serial, Confirm.SMALL.value)
            #     return False
            res = self._wait_bingo_text()
            if res == 0:
                return True
            elif res == 2:
                return False
        wait_click(self.serial, Bingo.REDRAW.value)

        while True:
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Confirm.SMALL.value)
            elif not exist(self.serial, Bingo.TEXT.value):
                break
            
        while True:
            for i in range(1, self.BINGO_CLOSE_AD_LEN + 1):
                if wait_click(self.serial, Bingo.CLOSE_AD(num=i), threshold=0.4, region=BingoAdPositions.TOP_LEFT.value, timeout=1.0):
                    continue
            for i in range(1, self.BINGO_CLOSE_AD_LEN + 1):
                if wait_click(self.serial, Bingo.CLOSE_AD(num=i), threshold=0.4, region=BingoAdPositions.TOP_RIGHT.value, timeout=1.0):
                    continue
            if exist(self.serial, Bingo.TEXT.value):
                break
            back(self.serial)
        
        res = self._wait_bingo_text()
        return True
    
    def fake_draw(self):
        while True:
            wait_click(self.serial, Bingo.RANDOM.value)
            wait_click(self.serial, Confirm.SMALL.value)
            wait_click(self.serial, Confirm.SMALL.value)
        
    def run(self):
        log_msg(self.serial,"賓果活動開始")
        self.enter_menu()
        self._claim_mission()
        while self._do_random():
            pass
        log_msg(self.serial, "賓果活動結束")

def bingo_attempt(serial):
    bingo = BingoBase(serial)
    # bingo.run()
    bingo.fake_draw()