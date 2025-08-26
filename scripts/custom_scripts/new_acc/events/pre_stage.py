from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.hacks import apply_mode
from core.base.exceptions import GameError
from scripts.shared.events.main_stage.selector import main_stage_finish_new
from scripts.shared.events.login import first_guest_login
from scripts.shared.constants import GameView, Settlement, Battle, Confirm, MainView, Leonard, Retry, Positions
from scripts.custom_scripts.new_acc.enum import PreStage, Phase1UI, Quests
from scripts.shared.events.teams.enum import Teams
from scripts.shared.events.gacha.enum import Gacha

class Phase1:
    def __init__(self, serial):
        self.serial = serial
        self.MEMBER1 = Positions.MEMBER1.value
        self.MEMBER2 = Positions.MEMBER2.value
        self.MEMBER3 = Positions.MEMBER3.value
        self.MEMBER4 = Positions.MEMBER4.value
        self.MEMBER5 = Positions.MEMBER5.value
        self.DIAMOND = Positions.DIAMOND.value
        self.MISSILE = Positions.MISSILE.value

    def _first_time_login(self):
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

    def _pre_stage(self):
        log_msg(self.serial, "進去前置關卡")

        if wait(self.serial, PreStage.NICKNAME.value):
            wait_click(self.serial, Confirm.SMALL.value)
            wait_click(self.serial, Confirm.SMALL.value)
            wait_click(self.serial, Confirm.SMALL.value)
        elif wait(self.serial, PreStage.TEXT, timeout=2.0):
            pass
        else:
            return
        
        wait_click(self.serial, MainView.SKIP.value)
        wait_click(self.serial, Confirm.SMALL.value, wait_time=0.5)

        if wait(self.serial, Battle.PAUSE.value, threshold=0.5, timeout=15.0):
            for _ in range(60):
                if exist_click(self.serial, MainView.SKIP.value, threshold=0.8):
                    break
                self._spam_click_members()
        else:
            raise GameError("無法確認戰鬥狀態，跳出")
        
        wait_click(self.serial, Confirm.SMALL.value, wait_time=3)

        for _ in range(30):
            if not exist(self.serial, Battle.PAUSE.value, threshold=0.8):
                break
            self._spam_click_members()
        
        if wait_click(self.serial, MainView.SKIP.value, timeout=5.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=2)

        if wait_click(self.serial, MainView.SKIP.value, timeout=5.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=2)
        connection_retry(self.serial, wait_name=MainView.SETTINGS.value, timeout=120.0)

    def _first_stage(self):
        log_msg(self.serial, "遊戲開場介紹")
        if not exist(self.serial, Phase1UI.LVL1_TEXT.value, threshold=0.9):
            return

        if wait_click(self.serial, MainView.SKIP.value, timeout=5.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=2)
        
        wait_click(self.serial, MainView.SKIP.value, timeout=5.0)

        apply_mode(self.serial, mode_name="main_stage", state="on")
        main_stage_finish_new(self.serial)

    def _first_ranger(self):
        if not exist(self.serial, Phase1UI.NEW_FRIEND_TEXT.value):
            if not exist(self.serial, Phase1UI.LVL2_TEXT.value, threshold=0.9999) or not exist(self.serial, Teams.ICON_DARK.value, threshold=0.9999):
                return

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
        connection_retry(self.serial, wait_name=MainView.SETTINGS.value, timeout=35.0)


    def _first_arrange_team(self):
        if wait_click(self.serial, MainView.SKIP.value, timeout=3):
            wait_click(self.serial, Confirm.SMALL.value)
        wait_click(self.serial, Teams.ICON_LIGHT.value)
        connection_retry(self.serial, wait_name=Leonard.BG_HAPPY.value, exception_msg="找不到隊伍教學", timeout=35.0)
        wait_click(self.serial, Leonard.BG_HAPPY.value)
        wait_click(self.serial, Leonard.BG_HAPPY.value)

        if exist(self.serial, Leonard.BG_HAPPY.value):
            drag(self.serial, (641, 285), (182, 576), wait_time=1.0, timeout=10.0)
            drag(self.serial, (182, 576), (641, 285), wait_time=1.0, timeout=10.0)

        wait_click(self.serial, MainView.SKIP.value)
        wait_click(self.serial, Confirm.SMALL.value)
        wait_click(self.serial, Teams.SAVE.value, wait_time=3.0)
        connection_retry(self.serial, wait_name=MainView.SETTINGS.value, exception_msg="未進入主畫面，隊伍教學失敗", timeout=35.0)
        for _ in range(3):
            if wait_click(self.serial, MainView.SKIP.value, timeout=5, wait_time=1.0):
                if not exist(self.serial, Confirm.SMALL.value):
                    continue
                wait_click(self.serial, Confirm.SMALL.value, wait_time=0.5)
                break
        wait_click(self.serial, Confirm.SMALL.value, wait_time=0.5)

    def run(self):
        self._first_time_login()
        self._pre_stage()

        if exist(self.serial, Quests.LONG.value, threshold=0.65):
            return
        if exist(self.serial, MainView.CLOSE_BOARD.value):
            return

        self._first_stage()
        self._first_ranger()
        self._first_arrange_team()

def phase1(serial):
    runner = Phase1(serial)
    runner.run()