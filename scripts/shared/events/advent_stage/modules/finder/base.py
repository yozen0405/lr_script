from scripts.shared.controller.context import GameContext
from core.actions.vision import (
    wait_click, exist_click, exist, 
    wait, wait_vanish, drag, get_pos,
      check_region_brightness, get_all_pos,
      save_screenshot, get_text_num
)
from scripts.shared.events.advent_stage.modules.navigator.utils import StageNavigatorUtils
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from scripts.shared.events.advent_stage.enum import AdventImg, AdventStageName
from typing import Dict, Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStageImg
from core.system.config import Config
from scripts.shared.constants import Leonard
from scripts.shared.events.advent_stage.modules.interrupt.tutorial import TutorialInterrupt 
from scripts.shared.events.advent_stage.session import AdventStageSession
import time

class StageFinder:
    def __init__(self, 
                 context: GameContext, 
                 # session: AdventStageSession
                 ):
        self.ctx = context
        # self.session = session

    def collect_stage_info(self) -> Dict[str, int]:
        # 找畫面上的綠色青蛙
        dct: Dict[str, int] = {
        }


        while True:
            lst = get_all_pos(self.ctx.serial, AdventImg.FROG.value, return_center=False)
            found_new = False
            cnt = 0

            for rect in lst:
                (x1, y1, x2, y2) = rect
                leonard_point = get_text_num(self.ctx.serial, 
                                             region=(x1 + 23, y1, x2 + 28, y2), 
                                             template_dir=AdventImg.DIGIT_DIR.value,
                                             debug=False  
                                            )
                region = (x1 - 100, y1 + 300, x2 + 100, y2 + 333)

                for name in AdventStageName:
                    if exist(self.ctx.serial, name.value, region=region, threshold=0.85):
                        if name.name in dct:
                            continue
                        dct[name.name] = leonard_point
                        found_new = True
                        log_msg(self.ctx.serial, f"找到關卡: {name.name}，他的 Leonard: {leonard_point}")
                        break
            
            if not found_new:
                break
            drag(self.ctx.serial, (436, 255), (136, 255), duration=1000, wait_time=4.5)

        return dct
    
    def attempt_enter_stage(self, stage_name: AdventStageName) -> bool:
        drag(self.ctx.serial, (136, 255), (636, 255), duration=3000, wait_time=4.5)

        for _ in range(3):
            pos = get_pos(self.ctx.serial, stage_name.value, threshold=0.85)
            if pos is None:
                drag(self.ctx.serial, (436, 255), (136, 255), duration=1000, wait_time=4.5)
                continue
            (x1, y1) = pos
            region = (x1 - 120, y1 - 82, x1 + 120, y1 - 15)

            if wait_click(self.ctx.serial, Battle.ENTER.value, region=region, threshold=0.85, wait_time=1.5):
                if wait_click(self.ctx.serial, AdventImg.VERY_HARD.value, threshold=0.85, wait_time=1.0, timeout=3.0):
                    connection_retry(self.ctx.serial, vanish=AdventImg.VERY_HARD.value, timeout=40.0)
                    return True
                elif exist(self.ctx.serial, AdventImg.NOT_OPEN_TEXT.value, threshold=0.9):
                    wait_click(self.ctx.serial, Confirm.SMALL.value)
                    return False
                else:
                    continue
                
    def enter_stage(self):
        names = self.collect_stage_info()
        for name in sorted(names, key=names.get):
            log_msg(self.ctx.serial, f"嘗試進入關卡: {name}，他的 Leonard: {names[name]}")
            if self.attempt_enter_stage(AdventStageName[name]):
                log_msg(self.ctx.serial, f"成功進入關卡: {name}")
                return
            else:
                log_msg(self.ctx.serial, f"無法進入關卡: {name}，嘗試下一個關卡")