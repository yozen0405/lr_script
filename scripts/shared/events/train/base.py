from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logger import log_msg
from .enum import TrainImg
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStage
from core.system.config import Config
from scripts.shared.constants import Leonard, Battle
from scripts.shared.events.pvp.enum import PvP

class BaseTrainStage:
    def __init__(self, serial):
        self.serial = serial

    def enter_menu(self):
        if exist(self.serial, TrainImg.TEXT.value):
            return
        
        for _ in range(5):
            if wait_click(self.serial, TrainImg.BTN.value):
                connection_retry(self.serial, vanish=TrainImg.BTN.value, timeout=40.0)
                self._on_pre_anime()
                return
            elif exist(self.serial, MainStage.BTN.value):
                drag(self.serial, (200, 400), (800, 400))

        raise GameError("無法進入降臨關卡")
    
    def _on_pre_anime(self):
        pass

    def enter_stage(self) -> bool:
        if not wait(self.serial, TrainImg.TEXT.value, timeout=30.0):
            raise GameError("不在train關卡")
        
        if wait_click(self.serial, PvP.BATTLE.value, timeout=7.0, threshold=0.8):
            wait_click(self.serial, TrainImg.NORMAL_BTN.value)
            connection_retry(self.serial, vanish=TrainImg.NORMAL_BTN.value, timeout=40.0)
            return True
        else:
            return False
        
    def _handle_introduction(self):
        if not wait(self.serial, TrainImg.INTRODUCTION.value, timeout=3.0):
            return
        for _ in range(5):
            wait_click(self.serial, (1096, 303), wait_time=0.3)
        wait_click(self.serial, (1234, 35), wait_time=0.5)        


    def battle(self):
        log_msg(self.serial, "Space train 任務開始")

        wait_click(self.serial, Battle.START.value)
        connection_retry(self.serial, appear=Battle.PAUSE.value, timeout=60.0)

        if wait(self.serial, Battle.PAUSE.value, timeout=15.0, threshold=0.9):
            while True:
                if exist(self.serial, TrainImg.SETTLEMENT_TEXT.value, threshold=0.9):
                    break

                if exist(self.serial, Retry.TEXT1.value) or exist(self.serial, Retry.TEXT2.value):
                    exist_click(self.serial, Retry.BTN.value, wait_time=2.5)
        else:
            raise GameError("無法確認戰鬥狀態，跳出")

        log_msg(self.serial, "結算中")
        self.settlement()

    def settlement(self):
        while True:
            for img in [Confirm.BIG2.value, TrainImg.SETTLEMENT_RESULT.value]:
                exist_click(self.serial, img, wait_time=1.5)
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.BTN.value)
            if exist(self.serial, TrainImg.TEXT.value):
                break

def train_stage_battle(serial: str):
    train = BaseTrainStage(serial)
    train.enter_menu()
    train.enter_stage()
    train.battle()