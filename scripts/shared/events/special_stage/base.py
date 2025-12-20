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
from scripts.shared.utils.hacks import apply_mode
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
    
    def leave_menu(self):
        start_time = time.time()
        bein = False

        while time.time() - start_time < 60:
            if exist(self.serial, Retry.TEXT1.value) or exist(self.serial, Retry.TEXT2.value):
                exist_click(self.serial, Retry.BTN.value)
                continue

            if exist(self.serial, SpecialStage.TEXT.value):
                exist_click(self.serial, MainView.BACK.value)
                bein = True
                continue
            
            if bein and not exist(self.serial, SpecialStage.TEXT.value):
                return
        raise GameError("無法離開特殊關卡選單")
    
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
            start_time = time.time()
            while time.time() - start_time < 120:
                if exist(self.serial, Retry.TEXT1.value):
                    exist_click(self.serial, Retry.BTN.value)
                elif not exist(self.serial, SpecialStage.ENTER.value):
                    return True
                elif exist(self.serial, SpecialStage.LIMITED.value):
                    exist_click(self.serial, Confirm.SMALL.value, wait_time=2.0)
                    wait_click(self.serial, MainView.BACK.value)
                    connection_retry(self.serial, appear=[(SpecialStage.LAB.value)], timeout=40.0)
                    return False
            raise GameError("進入特殊關卡超時")
        else:
            return False
            
    def single_mode_run(self):
        log_msg(self.serial, "Special Stage 進場")
        apply_mode(self.serial, mode_name="special_stage", state="on")

        self.hooks.handle_team_num(self)
        self.hooks.handle_auto_btn(self)

        if not wait_click(self.serial, Battle.NEXT.value, timeout=15.0):
            raise GameError("無法點擊下一步按鈕")
        
        self.utils._battle_loop()

        log_msg(self.serial, "結算中")
        self.settlement()

        wait_click(self.serial, MainView.BACK.value, timeout=20.0)
        connection_retry(self.serial, appear=[(SpecialStage.LAB.value)], timeout=40.0)
        apply_mode(self.serial, mode_name="special_stage", state="off")

        log_msg(self.serial, "Special Stage 任務完成")

    def loop_mode_run(self):
        log_msg(self.serial, "Special Stage 迴圈進場")

        self.hooks.handle_team_num(self)
        self.hooks.handle_auto_btn(self)

        wait_click(self.serial, Battle.CYCLE.value)
        if wait(self.serial, Confirm.SMALL.value):
            exist_click(self.serial, Battle.MAX_OFF.value, threshold=0.9)
            if not wait_click(self.serial, Confirm.SMALL.value, threshold=0.9):
                self.utils.quit_game()
                return False

        wait_click(self.serial, Battle.NEXT.value)
        self.utils._battle_loop()
        
        log_msg(self.serial, "結算中")
        wait_click(self.serial, Confirm.BIG2.value)

        connection_retry(self.serial, appear=[(SpecialStage.TEXT.value)], timeout=80.0)
        wait_click(self.serial, MainView.BACK.value, timeout=20.0)
        connection_retry(self.serial, appear=[(SpecialStage.LAB.value)], timeout=80.0)

        log_msg(self.serial, "Special Stage 迴圈任務完成")
        return True

    def settlement(self):
        start_time = time.time()    
        while time.time() - start_time < 120:
            for img in [
                Confirm.BIG1.value, Confirm.BIG2.value, Settlement.ONE_REWARD.value, 
                Confirm.SMALL.value, Settlement.STOP.value, Settlement.SILVER_BOX.value, 
                Settlement.BRONZE_BOX.value, Settlement.TEXT.value
            ]:
                exist_click(self.serial, img)
            if exist(self.serial, Retry.TEXT1.value) or exist(self.serial, Retry.TEXT2.value):
                exist_click(self.serial, Retry.BTN.value)
            if exist(self.serial, SpecialStage.TEXT.value):
                return
        raise GameError("結算超時")
