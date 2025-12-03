import time
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, get_pos, drag
from core.base.exceptions import GameError
from scripts.shared.constants import Settlement, Confirm, Battle, Retry, MainView, Positions
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.special_stage.enum import SpecialStage
from scripts.shared.events.special_stage.hook import SpecialStageHooks
from scripts.shared.events.special_stage.utils import SpecialStageUtils
from scripts.shared.utils.retry import connection_retry
from typing import Optional, Tuple

class BaseSpecialStage:
    def __init__(self, serial, team_num=1):
        self.serial = serial
        self.MEMBER3_POS = Positions.MEMBER3.value
        self.MEMBER4_POS = Positions.MEMBER4.value
        self.hooks = SpecialStageHooks(serial)
        self.utils = SpecialStageUtils(serial, hooks=self.hooks)
        self.team_num = team_num

    def find_target_planet(self, planet: Optional[str] = None, crop_region: Optional[Tuple[int, int, int, int]] = None) -> None:
        return self.utils.find_target_planet(planet=planet, crop_region=crop_region)

    def enter_menu(self):
        if exist(self.serial, SpecialStage.TEXT.value):
            return
        
        for _ in range(5):
            if wait_click(self.serial, SpecialStage.BTN.value):
                connection_retry(self.serial, vanish=[(SpecialStage.BTN.value)], retry=[(SpecialStage.BTN.value)])
                self.hooks.on_pre_anime()
                return
            elif exist(self.serial, MainStage.BTN.value):
                drag(self.serial, (800, 400), (200, 400))

        raise GameError("無法進入特殊關卡")

    def enter_stage(
        self,
        stage_num: int,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> None:
        if not wait(self.serial, SpecialStage.TEXT.value, timeout=30.0):
            raise GameError("不在特殊")
        
        if wait_click(self.serial, SpecialStage.STAGE(stage=stage_num), region=region, timeout=7.0, threshold=0.8):
            connection_retry(self.serial, appear=[(SpecialStage.ENTER.value)], timeout=40.0)
            wait_click(self.serial, SpecialStage.ENTER.value, timeout=25.0)
            while True:
                if exist(self.serial, Retry.TEXT1.value):
                    exist_click(self.serial, Retry.BTN.value)
                elif not exist(self.serial, SpecialStage.ENTER.value):
                    return True
                elif exist(self.serial, SpecialStage.LIMITED.value):
                    exist_click(self.serial, Confirm.SMALL.value, wait_time=2.0)
                    wait_click(self.serial, MainView.BACK.value)
                    connection_retry(self.serial, appear=[(SpecialStage.LAB.value)], timeout=40.0)
                    return False
        else:
            return False
            
    def single_mode_run(self):
        log_msg(self.serial, "Special Stage 進場")

        self.hooks.handle_team_num(self)
        wait_click(self.serial, Battle.NEXT.value)
        
        is_victory = self.utils._battle_loop(
            end_targets=[Settlement.TEXT.value], 
            auto_mode=False
        )

        if not is_victory:
            raise GameError("Special Stage 戰鬥異常或超時")

        log_msg(self.serial, "結算中")
        self.settlement()

        wait_click(self.serial, MainView.BACK.value, timeout=20.0)
        connection_retry(self.serial, appear=[(SpecialStage.LAB.value)], timeout=40.0)
        
        log_msg(self.serial, "Special Stage 任務完成")

    def loop_mode_run(self):
        log_msg(self.serial, "Special Stage 迴圈進場")

        self.hooks.handle_team_num(self)
        exist_click(self.serial, Battle.AUTO_BTN_OFF2.value, threshold=0.99)

        wait_click(self.serial, Battle.CYCLE.value)
        if wait(self.serial, Confirm.SMALL.value):
            exist_click(self.serial, Battle.MAX_OFF.value, threshold=0.9)
            if not wait_click(self.serial, Confirm.SMALL.value, threshold=0.9):
                self.utils.quit_game()
                return False

        wait_click(self.serial, Battle.NEXT.value)
        is_finished = self.utils._battle_loop(
            end_targets=[Battle.LOOP_END_TEXT.value], 
            auto_mode=True,
            timeout=600
        )

        if not is_finished:
             raise GameError("Special Stage 迴圈執行異常")
        
        log_msg(self.serial, "結算中")
        wait_click(self.serial, Confirm.BIG2.value)

        connection_retry(self.serial, appear=[(SpecialStage.TEXT.value)], timeout=80.0)
        wait_click(self.serial, MainView.BACK.value, timeout=20.0)
        connection_retry(self.serial, appear=[(SpecialStage.LAB.value)], timeout=80.0)

        log_msg(self.serial, "Special Stage 迴圈任務完成")
        return True

    def settlement(self):
        connection_retry(self.serial, appear=[(Settlement.TEXT.value)], timeout=40.0)
        for _ in range(3):
            wait_click(self.serial, self.MEMBER4_POS)

        cnt = 0
        while True:
            for img in [
                Confirm.BIG1.value, Confirm.BIG2.value, Settlement.ONE_REWARD.value, 
                Confirm.SMALL.value, Settlement.STOP.value, Settlement.SILVER_BOX.value, 
                Settlement.BRONZE_BOX.value
            ]:
                exist_click(self.serial, img, wait_time=1.5)
            if exist(self.serial, Retry.TEXT1.value) or exist(self.serial, Retry.TEXT2.value):
                exist_click(self.serial, Retry.BTN.value)
                cnt += 1
            if exist(self.serial, SpecialStage.TEXT.value):
                break
            if cnt >= 5:
                raise GameError("結算異常，跳出")
