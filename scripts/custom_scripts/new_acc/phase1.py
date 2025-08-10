from core.system.logger import log_msg
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.constants import positions
from core.base.exceptions import GameError
from scripts.shared.events.main_stage.selector import main_stage_finish_new
from scripts.shared.events.login import first_guest_login

class Phase1:
    def __init__(self, serial):
        self.serial = serial
        self.MEMBER1 = positions["member1"]
        self.MEMBER2 = positions["member2"]
        self.MEMBER3 = positions["member3"]
        self.MEMBER4 = positions["member4"]
        self.MEMBER5 = positions["member5"]
        self.DIAMOND = positions["diamond"]
        self.MISSILE = positions["missile"]

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

        if wait(self.serial, "nickname_setup.png"):
            wait_click(self.serial, "confirm_small.png")
            wait_click(self.serial, "confirm_small.png")
            wait_click(self.serial, "confirm_small.png")
        elif wait(self.serial, "pre_stage_text.png", timeout=2.0):
            pass
        else:
            return
        
        wait_click(self.serial, "skip.png")
        wait_click(self.serial, "confirm_small.png", wait_time=0.5)

        if wait(self.serial, "pause.png", threshold=0.5, timeout=15.0):
            for _ in range(60):
                if exist_click(self.serial, "skip.png", threshold=0.8):
                    break
                self._spam_click_members()
        else:
            raise GameError("無法確認戰鬥狀態，跳出")
        
        wait_click(self.serial, "confirm_small.png", wait_time=3)

        for _ in range(30):
            if not exist(self.serial, "pause.png", threshold=0.8):
                break
            self._spam_click_members()
        
        if wait_click(self.serial, "skip.png", timeout=5.0):
            wait_click(self.serial, "confirm_small.png", wait_time=2)

        if wait_click(self.serial, "skip.png", timeout=5.0):
            wait_click(self.serial, "confirm_small.png", wait_time=2)
        connection_retry(self.serial, wait_name="settings_btn.png", timeout=120.0)

    def _first_stage(self):
        log_msg(self.serial, "遊戲開場介紹")
        if not exist(self.serial, "phase1_lvl1_text.png"):
            return

        if wait_click(self.serial, "skip.png", timeout=5.0):
            wait_click(self.serial, "confirm_small.png", wait_time=2)
        
        wait_click(self.serial, "skip.png", timeout=5.0)

        apply_mode(self.serial, mode_name="main_stage", state="on")
        main_stage_finish_new(self.serial)

    def _first_ranger(self):
        if not exist(self.serial, "phase1_new_friend_text.png"):
            return

        wait_click(self.serial, "skip.png")
        wait_click(self.serial, "confirm_small.png")
        wait_click(self.serial, "gacha_icon.png", timeout=7.0)
        if not wait(self.serial, "gacha_text.png", timeout=40.0):
            raise GameError("無法進入扭蛋")
        wait_click(self.serial, "skip.png", timeout=1.5)
        wait_click(self.serial, "gacha_jessica.png")
        wait_click(self.serial, "gacha_skip.png", timeout=40.0)
        wait_click(self.serial, "confirm_small.png")
        wait_click(self.serial, "gacha_confirm.png")
        wait_click(self.serial, "skip.png", timeout=40.0)
        wait_click(self.serial, "confirm_small.png")
        connection_retry(self.serial, wait_name="settings_btn.png", timeout=35.0)


    def _first_arrange_team(self):
        if wait_click(self.serial, "skip.png", timeout=3):
            wait_click(self.serial, "confirm_small.png")
        wait_click(self.serial, "team_icon.png")
        connection_retry(self.serial, wait_name="leonard_teacher.png", exception_msg="找不到隊伍教學", timeout=35.0)
        wait_click(self.serial, "leonard_teacher.png")
        wait_click(self.serial, "leonard_teacher.png")

        if exist(self.serial, "leonard_teacher.png"):
            drag(self.serial, (641, 285), (182, 576), wait_time=1.0, timeout=10.0)
            drag(self.serial, (182, 576), (641, 285), wait_time=1.0, timeout=10.0)

        wait_click(self.serial, "skip.png")
        wait_click(self.serial, "confirm_small.png")
        wait_click(self.serial, "save_team.png", wait_time=3.0)
        connection_retry(self.serial, wait_name="settings_btn.png", exception_msg="未進入主畫面，隊伍教學失敗", timeout=35.0)
        for _ in range(3):
            if wait_click(self.serial, "skip.png", timeout=5, wait_time=1.0):
                if not exist(self.serial, "confirm_small.png"):
                    continue
                wait_click(self.serial, "confirm_small.png", wait_time=0.5)
                break
        wait_click(self.serial, "confirm_small.png", wait_time=0.5)

    def run(self):
        self._first_time_login()
        self._pre_stage()

        if exist(self.serial, "long_quest.png", threshold=0.65):
            return

        self._first_stage()
        self._first_ranger()
        self._first_arrange_team()

def phase1(serial):
    runner = Phase1(serial)
    runner.run()