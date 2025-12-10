from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.screen import back
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logger import log_msg
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.constants.leonard import Leonard
import time

class TeamsBase:
    def __init__(self, serial):
        self.serial = serial
        self.RANGER_POS1 = (240, 612)
        self.RANGER_POS2 = (587, 612)
        self.RANGER_POS3 = (931, 612)


    def enter_menu(self):
        if exist(self.serial, TeamsImg.TEXT.value) or exist(self.serial, TeamsImg.SWITCH_TEXT.value, threshold=0.9):
            return
        
        if wait_click(self.serial, TeamsImg.BTN.value):
            connection_retry(self.serial, vanish=TeamsImg.BTN.value, retry=TeamsImg.BTN.value, timeout=40.0)
            time.sleep(1.5)
            self._on_pre_anime()
        else:
            raise GameError("無法進入teams")

    def _on_pre_anime(self):
        cnt = 0
        start_time = time.time()
        while time.time() - start_time < 60.0:
            if exist_click(self.serial, Leonard.TP_POINT2.value, threshold=0.85):
                cnt = 0
                continue
            if exist_click(self.serial, Leonard.TP_THUMBS_UP.value):
                continue
            if exist_click(self.serial, TeamsImg.SELECTOR_FINGER.value, threshold=0.85):
                wait_click(self.serial, (1035, 88))
                continue
            if exist(self.serial, TeamsImg.TEXT.value, threshold=0.999) or exist(self.serial, TeamsImg.SWITCH_TEXT.value, threshold=0.9):
                cnt += 1
            if cnt >= 2:
                return
        raise GameError("進入teams頁面失敗")
        

    def _select_ranger(self, lst: Optional[Tuple[TeamsImg]] = None):
        wait_click(self.serial, TeamsImg.FILTER_BTN.value, wait_time=0.0)
        wait_click(self.serial, TeamsImg.RESET.value, wait_time=0.0)
        
        for img in lst:
            wait_click(self.serial, img.value, wait_time=0.0)

        wait_click(self.serial, Confirm.SMALL.value, wait_time=0.2)
        wait_click(self.serial, TeamsImg.SORT_BY_BTN.value, wait_time=0.0)
        wait_click(self.serial, TeamsImg.LVL_DESC.value, wait_time=0.0)

        # 這邊不嚴謹
        wait_click(self.serial, (100, 680))
        self._on_talent_anime()
    
    def _go_to_upgrade_page(self):
        if not wait_click(self.serial, TeamsImg.UPGRADE_BTN.value):
            raise GameError("無法升級ranger")

    def _on_upgrade_page(self):
        connection_retry(self.serial, appear=TeamsImg.LVL_UP_PAGE_TEXT.value, timeout=40.0)
        # drag(self.serial, (80, 574), (478, 341), wait_time=3.0, timeout=10.0) # for rene
        drag(self.serial, (609, 618), (609, 358)) 
        wait_click(self.serial, TeamsImg.UPGRADE_LVL_BTN.value)
        if exist(self.serial, TeamsImg.LVL_UP_POP_TEXT.value):
            wait_click(self.serial, Confirm.SMALL.value)
        for _ in range(3):
            wait_click(self.serial, TeamsImg.UPGRADE_SUCCESS.value, timeout=5.0, wait_time=1.0)
        
    def back_to_team_page(self):
        wait_click(self.serial, MainView.BACK.value)
        connection_retry(self.serial, appear=[(TeamsImg.TEXT.value, 0.9), (TeamsImg.SWITCH_TEXT.value, 0.95)], timeout=40.0)
        self._on_pre_anime()


    def _on_talent_anime(self):
        cnt = 0
        if not wait(self.serial, Leonard.TP_CLAP2.value, timeout=3.0):
            return
        while True:
            if exist_click(self.serial, Leonard.TP_CLAP2.value, threshold=0.95):
                cnt = 0
                continue
            if exist_click(self.serial, Leonard.TP_STICK.value, threshold=0.95):
                cnt = 0
                continue
            if exist_click(self.serial, Leonard.TP_POINT3.value, threshold=0.95):
                cnt = 0
                continue
            if exist_click(self.serial, Leonard.TP_THUMBS_UP.value, threshold=0.95):
                cnt = 0
                continue
            if exist_click(self.serial, Leonard.TP_HAPPY2.value, threshold=0.95):
                cnt = 0
                continue
            cnt += 1
            if cnt >= 2:
                break

    def run(self):
        self._select_ranger(lst=[TeamsImg.FILTER_SIX_STARS, TeamsImg.FILTER_RANGER])
        self._go_to_upgrade_page()
        self._on_upgrade_page()
        self.back_to_team_page()

def upgrade_ranger(serial):
    teams = TeamsBase(serial)
    teams.enter_menu()
    teams.run()