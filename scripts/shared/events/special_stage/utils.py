import time
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, get_pos, drag
from core.base.exceptions import GameError
from scripts.shared.constants import Settlement, Confirm, Battle, Retry, MainView, Positions
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.special_stage.enum import SpecialStage
from scripts.shared.events.special_stage.hook import SpecialStageHooks
from scripts.shared.utils.retry import connection_retry
from typing import Optional, Tuple

class SpecialStageUtils:
    def __init__(self, serial, hooks):
        self.serial = serial
        self.MEMBER3_POS = Positions.MEMBER3.value
        self.MEMBER4_POS = Positions.MEMBER4.value
        self.hooks = hooks

    def _battle_loop(self, timeout=300) -> bool:
        start_time = time.time()
        retry_count = 0

        while time.time() - start_time < timeout:
            if exist(self.serial, MainStage.SETTLEMENT.value, threshold=0.9) or \
                exist(self.serial, Settlement.LEVEL_UP_TEXT.value) or \
                    exist(self.serial, Battle.LOOP_END_TEXT.value):
                return
            
            if exist(self.serial, Retry.TEXT1.value) or exist(self.serial, Retry.TEXT2.value):
                wait_click(self.serial, Retry.BTN.value)
                retry_count += 1
                if retry_count >= 20:
                    break
                continue

            if exist_click(self.serial, Battle.START.value):
                state = 1
                continue
            elif state == 1:
                state = 2

            if state == 2:
                self.hooks.on_start_page()
        raise GameError("戰鬥超時")

    def find_target_planet(self, planet: Optional[str] = None, crop_region: Optional[Tuple[int, int, int, int]] = None) -> None:
        if planet is None or planet == "":
            raise GameError("custom stage 型別錯誤")

        for _ in range(5):
            drag(self.serial, (100, 523), (800, 523), wait_time=0.3)

        region: Tuple[int, int, int, int] = (280, 90, 800, 470)

        for _ in range(7):
            pos = get_pos(self.serial, planet)
            if pos:
                x, y = pos
                drag(self.serial, (x, y), (640, y), wait_time=1.5)
                for i in range(2):
                    pos = get_pos(self.serial, planet)
                    if pos is None:
                        continue
                    x, y = pos
                if crop_region:
                    (offsets_x1, offsets_y1, offsets_x2, offsets_y2) = crop_region
                    region = (x - offsets_x1, y - offsets_y1, x + offsets_x2, y + offsets_y2)
                break

            drag(self.serial, (400, 523), (100, 523), wait_time=1.0)
        return region
    
    def quit_game(self):
        wait_click(self.serial, Confirm.CANCEL.value, wait_time=1.0)
        wait_click(self.serial, MainView.BACK.value)
        connection_retry(self.serial, appear=[(SpecialStage.TEXT.value)], timeout=40.0)
        wait_click(self.serial, MainView.BACK.value, timeout=20.0)
        connection_retry(self.serial, appear=[(SpecialStage.LAB.value)], timeout=40.0)