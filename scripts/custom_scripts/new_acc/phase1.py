from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.hacks import apply_mode
from core.base.exceptions import GameError
from scripts.shared.events.main_stage.selector import main_stage_finish_new
from scripts.shared.events.login.sec import first_guest_login
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry, Positions
from scripts.custom_scripts.new_acc.enum import PreStage, Phase1UI, Quests
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.events.gacha.enum import Gacha
from scripts.custom_scripts.new_acc.base import BasePhase

class Phase1(BasePhase):
    def __init__(self, serial):
        self.serial = serial
        self.MEMBER1 = Positions.MEMBER1.value
        self.MEMBER2 = Positions.MEMBER2.value
        self.MEMBER3 = Positions.MEMBER3.value
        self.MEMBER4 = Positions.MEMBER4.value
        self.MEMBER5 = Positions.MEMBER5.value
        self.DIAMOND = Positions.DIAMOND.value
        self.MISSILE = Positions.MISSILE.value

    def _login(self):
        log_msg(self.serial, "首次登入流程啟動")
        first_guest_login(self.serial)

    def _spam_click_members(self):
        wait_click(self.serial, self.MEMBER1, wait_time=0.0)
        wait_click(self.serial, self.MEMBER2, wait_time=0.0)
        wait_click(self.serial, self.MEMBER3, wait_time=0.0)
        wait_click(self.serial, self.MEMBER4, wait_time=0.0)
        wait_click(self.serial, self.MEMBER5, wait_time=0.0)
        wait_click(self.serial, self.DIAMOND, wait_time=0.0)
        wait_click(self.serial, self.MISSILE, wait_time=1.0)

    def _handle_nickname(self):
        if wait(self.serial, PreStage.NICKNAME.value):
            wait_click(self.serial, Confirm.SMALL.value)
            wait_click(self.serial, Confirm.SMALL.value)
            wait_click(self.serial, Confirm.SMALL.value)
        elif wait(self.serial, PreStage.TEXT.value, timeout=2.0):
            pass
        else:
            return
        
        wait_click(self.serial, MainView.SKIP.value)
        wait_click(self.serial, Confirm.SMALL.value, wait_time=0.5)

    def _pre_stage(self):
        log_msg(self.serial, "進去前置關卡")
        
        while True:
            if exist(self.serial, Battle.PAUSE.value, threshold=0.8):
                self._spam_click_members()
            if exist(self.serial, Retry.TEXT1.value, threshold=0.8):
                exist_click(self.serial, Retry.BTN.value)
            if exist(self.serial, MainView.SETTINGS.value):
                break
            if exist_click(self.serial, MainView.SKIP.value):
                wait_click(self.serial, Confirm.SMALL.value)

    def _first_stage(self):
        log_msg(self.serial, "遊戲開場介紹")

        if wait_click(self.serial, MainView.SKIP.value, timeout=5.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=2)
        
        wait_click(self.serial, MainView.SKIP.value, timeout=3.0)

        apply_mode(self.serial, mode_name="main_stage", state="on")
        main_stage_finish_new(self.serial)

    def _first_ranger(self):
        wait_click(self.serial, MainView.SKIP.value)
        wait_click(self.serial, Confirm.SMALL.value)
        wait_click(self.serial, Gacha.ICON.value, timeout=7.0)
        if not wait(self.serial, Gacha.TEXT.value, timeout=40.0):
            raise GameError("無法進入扭蛋")
        wait_click(self.serial, MainView.SKIP.value, timeout=1.5)
        wait_click(self.serial, Gacha.JESSICA.value)
        wait_click(self.serial, Gacha.SKIP.value, timeout=40.0)
        wait_click(self.serial, Confirm.SMALL.value)
        wait_click(self.serial, Gacha.CONFIRM.value)
        wait_click(self.serial, MainView.SKIP.value, timeout=40.0)
        wait_click(self.serial, Confirm.SMALL.value)
        connection_retry(self.serial, appear=MainView.SETTINGS.value, timeout=35.0)

    def _first_arrange_team(self):
        if wait_click(self.serial, MainView.SKIP.value, timeout=3):
            wait_click(self.serial, Confirm.SMALL.value)

        wait_click(self.serial, TeamsImg.ICON_LIGHT.value)
        connection_retry(self.serial, appear=Leonard.BG_HAPPY.value, timeout=35.0)
        wait_click(self.serial, Leonard.BG_HAPPY.value)
        wait_click(self.serial, Leonard.BG_HAPPY.value)

        if exist(self.serial, Leonard.BG_HAPPY.value):
            drag(self.serial, (641, 285), (182, 576), wait_time=1.0, timeout=10.0)
            drag(self.serial, (182, 576), (641, 285), wait_time=1.0, timeout=10.0)

        wait_click(self.serial, MainView.SKIP.value)
        wait_click(self.serial, Confirm.SMALL.value)
        wait_click(self.serial, TeamsImg.SAVE.value, wait_time=3.0)
        connection_retry(self.serial, appear=MainView.SETTINGS.value, timeout=35.0)
        for _ in range(3):
            if wait_click(self.serial, MainView.SKIP.value, timeout=5, wait_time=1.0):
                if not exist(self.serial, Confirm.SMALL.value):
                    continue
                wait_click(self.serial, Confirm.SMALL.value, wait_time=0.5)
                break
        wait_click(self.serial, Confirm.SMALL.value, wait_time=0.5)

    def _detect_event(self):
        return 0
        # if exist(self.serial, GameView.ICON.value):
        #     return 1
        # if exist(self.serial, PreStage.MOON.value):
        #     return 2
        # if exist(self.serial, Phase1UI.LVL1_TEXT.value, threshold=0.9):
        #     return 3
        # elif exist(self.serial, Phase1UI.LVL2_TEXT.value, threshold=0.9999):
        #     if exist(self.serial, Teams.ICON_DARK.value, threshold=0.9999):
        #         return 4
        #     else:  
        #         return 5

    def steps(self):
        return [
            self._login,
            self._handle_nickname,
            self._pre_stage,
            self._first_stage,
            self._first_ranger,
            self._first_arrange_team,
        ]