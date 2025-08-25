from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logger import log_msg
from .enum import Advent, Stage
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStage

class BaseAdventStage:
    def __init__(self, serial):
        self.serial = serial
        self.MEMBER3_POS = Positions.MEMBER3.value
        self.MEMBER4_POS = Positions.MEMBER4.value

    def enter_menu(self):
        if exist(self.serial, Advent.TEXT.value):
            return
        
        for _ in range(5):
            if wait_click(self.serial, Advent.BTN.value):
                connection_retry(self.serial, image_name=Advent.BTN.value, exception_msg="不在主畫面", timeout=40.0)
                self._on_pre_anime()
                return
            elif exist(self.serial, MainStage.BTN.value):
                drag(self.serial, (800, 400), (200, 400))

        raise GameError("無法進入降臨關卡")
    
    def _on_pre_anime(self):
        for _ in range(7):
            if exist(self.serial, Advent.TEXT.value):
                break
            if not wait_click(self.serial, Battle.ANIME.value, wait_time=2.0, threshold=0.6):
                break
    
    def find_target_boss(self, boss: Optional[str] = None) -> None:
        if boss is None or boss == "":
            raise GameError("custom stage 型別錯誤")

        for _ in range(5):
            drag(self.serial, (100, 609), (800, 609), wait_time=0.3)

        crop_region: Tuple[int, int, int, int] = (168, 370, 168, 26)

        did_find = False
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
                    (offsets_x1, offsets_y1, offsets_x2, offsets_y2) = crop_region
                    region = (x - offsets_x1, y - offsets_y1, x + offsets_x2, y - offsets_y2)
                    did_find = True
                break

            drag(self.serial, (400, 609), (100, 609), wait_time=1.0)

        if not did_find:
            return None

        return region

    def enter_stage(self, boss: str) -> bool:
        if not wait(self.serial, Advent.TEXT.value, timeout=30.0):
            raise GameError("不在降臨關卡")
        
        region = self.find_target_boss(boss=boss)
        if region is None:
            return False

        if wait_click(self.serial, Battle.ENTER.value, region=region, timeout=7.0, threshold=0.8):
            wait_click(self.serial, Advent.VERY_HARD.value)
            connection_retry(self.serial, image_name=Advent.VERY_HARD.value, exception_msg="進不去降臨關卡", timeout=40.0)
            return True
        else:
            return False

    def battle(self) -> bool:
        log_msg(self.serial, "Advent 任務開始")
        exist_click(self.serial, Battle.AUTO_BTN_OFF2.value, threshold=0.96)

        wait_click(self.serial, Battle.NEXT.value)
        wait_click(self.serial, Battle.START.value)
        connection_retry(self.serial, wait_name=Battle.PAUSE.value, timeout=60.0)

        wait_vanish(self.serial, Battle.PAUSE.value, threshold=0.97, timeout=60.0)

        log_msg(self.serial, "結算中")
        self.settlement()

    def settlement(self):
        if wait_click(self.serial, Settlement.CANCEL_LOSE.value, wait_time=10.0):
            wait_click(self.serial, Settlement.CLOSE_LOSE_TIPS.value, wait_time=7.0)
            if not wait_click(self.serial, Confirm.SMALL.value, wait_time=7.0):
                raise GameError("沒有進入失敗葉面")
            raise GameError("輸了")

        connection_retry(self.serial, wait_name=Settlement.TEXT.value, retry_text=Retry.TEXT2.value, timeout=40.0)
        for _ in range(3):
            wait_click(self.serial, self.MEMBER4_POS)

        while True:
            for img in [Confirm.BIG1.value, Confirm.BIG2.value, Settlement.ONE_REWARD.value, Confirm.SMALL.value, Settlement.STOP.value, Settlement.SILVER_BOX.value, Settlement.BRONZE_BOX.value]:
                exist_click(self.serial, img, wait_time=1.5)
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.BTN.value)
            if exist(self.serial, Advent.TEXT.value):
                break

def advent_stage_battle(serial: str):
    advent = BaseAdventStage(serial)
    advent.enter_menu()
    boss: str = ""
    for boss_enum in Stage:
        if advent.enter_stage(boss=boss_enum.value):
            boss = boss_enum.value
            break

    advent.battle()