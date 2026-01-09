from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from .enum import TrainImg
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStageImg
from core.system.config import Config
from scripts.shared.constants import Leonard, Battle
from scripts.shared.events.pvp.enum import PvP

class BaseTrainStage:
    def __init__(self, serial):
        self.serial = serial
        self.enter_pos = None

    def enter_menu(self):
        if exist(self.serial, TrainImg.TEXT.value):
            return
        
        for _ in range(5):
            if wait_click(self.serial, TrainImg.BTN.value):
                connection_retry(self.serial, vanish=TrainImg.BTN.value, timeout=40.0)
                self._on_pre_anime()
                return
            elif exist(self.serial, MainStageImg.BTN.value):
                drag(self.serial, (200, 400), (800, 400))

        raise GameError("無法進入降臨關卡")
    
    def _on_pre_anime(self):
        pass

    def enter_stage(self) -> bool:
        if not wait(self.serial, TrainImg.TEXT.value, timeout=30.0):
            raise GameError("不在train關卡")
        
        for _ in range(15):
            if exist(self.serial, TrainImg.UNLOCK_BTN.value, threshold=0.9):
                wait_click(self.serial, TrainImg.UNLOCK_BTN.value, threshold=0.9)
                self.enter_pos = get_pos(self.serial, TrainImg.UNLOCK_BTN.value, threshold=0.9)
                if wait(self.serial, TrainImg.UNLOCK_TEXT.value, threshold=0.9):
                    wait_click(self.serial, Confirm.SMALL.value)
                    break
            elif exist(self.serial, TrainImg.UNLOCK_BTN_DARK.value, threshold=0.9):
                break   

            drag(self.serial, (595, 383), (439, 383))

        if self.enter_pos is not None:
            wait_click(self.serial, self.enter_pos)
        elif exist(self.serial, PvP.BATTLE.value):
            wait_click(self.serial, PvP.BATTLE.value)
        else:
            raise GameError("無法進入train關卡戰鬥")
        
        wait_click(self.serial, TrainImg.NORMAL_BTN.value)
        connection_retry(self.serial, vanish=TrainImg.NORMAL_BTN.value, timeout=40.0)
        
    def _handle_introduction(self):
        if not wait(self.serial, TrainImg.INTRODUCTION.value, timeout=3.0):
            return
        for _ in range(5):
            wait_click(self.serial, (1096, 303), wait_time=0.3)
        wait_click(self.serial, (1234, 35), wait_time=0.5)        


    def battle(self):
        log_msg(self.serial, "Space train 任務開始")

        self._handle_introduction()

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