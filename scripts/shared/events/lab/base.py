import time
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.ocr import get_main_stage_num
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.lab.enum import LabMenu, MakeMenu, ExtractMenu

class LabeMake:
    def __init__(self, serial):
        self.serial = serial
    
    def enter_menu(self):
        if exist(self.serial, MakeMenu.TEXT.value, threshold=0.9):
            return

        if wait(self.serial, MakeMenu.ICON.value, timeout=20.0, wait_time=1.0):
            wait_click(self.serial, MakeMenu.ICON.value)
            connection_retry(self.serial, vanish=[MakeMenu.ICON.value], timeout=60.0)
            self._handle_pre_tutorial()
        else:
            raise GameError("不在主畫面")
        
    def _handle_pre_tutorial(self):
        if not wait(self.serial, Leonard.TP_POINT2.value, threshold=0.85, wait_time=0.3):
            return
        cnt = 0
        for _ in range(10):
            if exist_click(self.serial, Leonard.TP_STICK.value, wait_time=1.0):
                cnt = 0
                continue
            if exist_click(self.serial, Leonard.TP_POINT2.value, threshold=0.85, wait_time=1.0):
                cnt = 0
                continue
            if exist_click(self.serial, MakeMenu.CRAFT.value, threshold=0.9, wait_time=0.3):
                wait_vanish(self.serial, MakeMenu.CRAFT.value, threshold=0.9, timeout=3.0, wait_time=1.0)
                cnt = 0
                continue
            time.sleep(0.5)
            cnt += 1
            if cnt >= 3:
                return
        raise GameError("進入lab製作頁面失敗")


    def claim_materials(self) -> bool:
        if not exist_click(self.serial, MakeMenu.BTN_LIGHT.value, threshold=0.9):
            return False
        connection_retry(self.serial, appear=[MakeMenu.SUCCESS_TEXT.value], timeout=60.0)
        wait_click(self.serial, Confirm.BIG2.value)
        return True

    def make_material(self):
        wait_click(self.serial, MakeMenu.REGULAR_MATERIAL_NAV.value)
        wait_click(self.serial, MakeMenu.INT_POTION.value)
        wait_click(self.serial, Battle.MAX_ON.value)
        wait_click(self.serial, MakeMenu.CRAFT.value)
        wait_click(self.serial, Confirm.SMALL.value)
        
    def quit(self):
        while True:
            if exist(self.serial, MakeMenu.TEXT.value, threshold=0.9):
                exist_click(self.serial, MainView.BACK.value)
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.BTN.value)
            if exist(self.serial, LabMenu.TEXT.value):
                break

    def run(self):
        self.enter_menu()
        if self.claim_materials():
            self.make_material()
        self.quit()

class LabExtract:
    def __init__(self, serial):
        self.serial = serial
    
    def enter_menu(self):
        if exist(self.serial, ExtractMenu.TEXT.value, threshold=0.9):
            return

        if wait(self.serial, ExtractMenu.ICON.value, timeout=20.0, wait_time=1.0):
            wait_click(self.serial, ExtractMenu.ICON.value)
            connection_retry(self.serial, vanish=[ExtractMenu.ICON.value], timeout=60.0)
            self._handle_pre_tutorial()
        else:
            raise GameError("不在主畫面")
        
    def _handle_pre_tutorial(self):
        pass

    def extract_material(self):
        wait_click(self.serial, ExtractMenu.MATERIAL_NAV.value)

        for _ in range(15):
            if exist_click(self.serial, ExtractMenu.DESTRUCTIVE_JEWEL.value, threshold=0.9):
                break
            drag(self.serial, (310, 558), (310, 324))

        for _ in range(30):
            exist_click(self.serial, ExtractMenu.MINUS_ON.value, threshold=0.99)
            if exist(self.serial, ExtractMenu.MINUS_OFF.value, threshold=0.99):
                break
        wait_click(self.serial, Confirm.SMALL.value)
        wait_click(self.serial, ExtractMenu.BTN.value)
        wait_click(self.serial, Confirm.SMALL.value)
        connection_retry(self.serial, appear=[ExtractMenu.SUCCESS.value], timeout=60.0)
        wait_click(self.serial, Confirm.BIG2.value, wait_time=1.0)

    def quit(self):
        wait_click(self.serial, MainView.BACK.value)
        connection_retry(self.serial, vanish=[ExtractMenu.TEXT.value], timeout=60.0)

    def run(self):
        self.enter_menu()
        self.extract_material()
        self.quit()

class LabBase:
    def __init__(self, serial):
        self.serial = serial
        self.extractor = LabExtract(serial)
        self.maker = LabeMake(serial)

    def enter_menu(self):
        if exist(self.serial, LabMenu.TEXT.value, threshold=0.9):
            return
        
        if exist(self.serial, MainStage.BTN.value):
            drag(self.serial, (200, 400), (800, 400))
            drag(self.serial, (200, 400), (800, 400))
            drag(self.serial, (200, 400), (800, 400))

        if wait(self.serial, LabMenu.BTN.value, timeout=20.0, wait_time=1.0):
            wait_click(self.serial, LabMenu.BTN.value)
            connection_retry(self.serial, vanish=[LabMenu.BTN.value], timeout=60.0)
            self._handle_pre_anime()
            wait(self.serial, LabMenu.TEXT.value)
            self._handle_pre_tutorial()
        else:
            raise GameError("不在主畫面")
        
    def _handle_pre_anime(self):
        for _ in range(7):
            if exist(self.serial, LabMenu.TEXT.value):
                break
            if not wait_click(self.serial, Battle.ANIME.value, wait_time=2.0, threshold=0.8):
                break

    def _handle_pre_tutorial(self):
        if not wait(self.serial, Leonard.TP_POINT.value):
            return
        for _ in range(10):
            wait_click(self.serial, LabMenu.TEXT.value)

    def complete_make_quest(self):
        self.maker.run()

    def complete_extract_quest(self):
        self.extractor.run()

def complete_lab_quest(serial):
    lab = LabBase(serial)
    lab.enter_menu()
    lab.complete_make_quest()
    lab.complete_extract_quest()