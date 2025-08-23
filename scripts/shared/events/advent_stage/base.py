from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logger import log_msg
from .enum import Advent
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStage

class BaseAdventStage:
    def __init__(self, serial):
        self.serial = serial
        self.MEMBER3_POS = Positions.MEMBER3
        self.MEMBER4_POS = Positions.MEMBER4

    def enter_menu(self):
        if exist(self.serial, Advent.TEXT):
            return
        
        for _ in range(5):
            if wait_click(self.serial, Advent.BTN):
                connection_retry(self.serial, image_name=Advent.BTN, exception_msg="不在主畫面", timeout=40.0)
                self._on_pre_anime()
                return
            elif exist(self.serial, MainStage.BTN):
                drag(self.serial, (800, 400), (200, 400))

        raise GameError("無法進入降臨關卡")
    
    def _on_pre_anime(self):
        for _ in range(7):
            if exist(self.serial, Advent.TEXT):
                break
            if not wait_click(self.serial, Battle.ANIME, wait_time=2.0, threshold=0.6):
                break
    
    def find_target_boss(self, boss: Optional[str] = None, crop_region: Optional[Tuple[int, int, int, int]] = None) -> None:
        if boss is None or boss == "":
            raise GameError("custom stage 型別錯誤")

        for _ in range(5):
            drag(self.serial, (100, 523), (800, 523), wait_time=0.3)

        region: Tuple[int, int, int, int] = (280, 90, 800, 470)

        for _ in range(7):
            pos = get_pos(self.serial, boss)
            if pos:
                x, y = pos
                drag(self.serial, (x, y), (640, y), wait_time=1.5)
                for i in range(2):
                    pos = get_pos(self.serial, boss)
                    if pos is None:
                        continue
                    x, y = pos
                if crop_region:
                    (offsets_x1, offsets_y1, offsets_x2, offsets_y2) = crop_region
                    region = (x - offsets_x1, y - offsets_y1, x + offsets_x2, y + offsets_y2)
                break

            drag(self.serial, (400, 523), (100, 523), wait_time=1.0)
        return region

    def enter_stage(self, boss: str, crop_region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        if not wait(self.serial, Advent.TEXT, timeout=30.0):
            raise GameError("不在降臨關卡")
        
        region = self.find_target_boss(boss=boss, crop_region=crop_region)
        if wait_click(self.serial, boss, region=region, timeout=7.0, threshold=0.8):
            connection_retry(self.serial, wait_name=Advent.TEXT, exception_msg="進不去降臨關卡", timeout=40.0)
            wait_click(self.serial, Battle.ENTER, timeout=25.0)
            while True:
                if exist(self.serial, Retry.TEXT1):
                    exist_click(self.serial, Retry.BTN)
                elif not exist(self.serial, Battle.ENTER):
                    return True
        else:
            return False

    def battle(self) -> bool:
        log_msg(self.serial, "Advent 任務開始")
        exist_click(self.serial, Battle.AUTO_BTN_OFF2, threshold=0.99)

        wait_click(self.serial, Battle.NEXT)
        wait_click(self.serial, Battle.START)
        connection_retry(self.serial, image_name=Battle.START, timeout=60.0)

        wait_vanish(self.serial, Battle.PAUSE, threshold=0.97, timeout=60.0)

        log_msg(self.serial, "結算中")
        self.settlement()

    def settlement(self):
        if wait_click(self.serial, Settlement.CANCEL_LOSE, wait_time=10.0):
            wait_click(self.serial, Settlement.CLOSE_LOSE_TIPS, wait_time=7.0)
            if not wait_click(self.serial, Confirm.SMALL, wait_time=7.0):
                raise GameError("沒有進入失敗葉面")
            raise GameError("輸了")

        connection_retry(self.serial, wait_name=Settlement.TEXT, retry_text=Retry.TEXT2, timeout=40.0)
        for _ in range(3):
            wait_click(self.serial, self.MEMBER4_POS)

        while True:
            for img in [Confirm.BIG1, Confirm.BIG2, Settlement.ONE_REWARD, Confirm.SMALL, Settlement.STOP, Settlement.SILVER_BOX, Settlement.BRONZE_BOX]:
                exist_click(self.serial, img, wait_time=1.5)
            if exist(self.serial, Retry.TEXT1):
                exist_click(self.serial, Retry.BTN)
            if exist(self.serial, Advent.TEXT):
                break