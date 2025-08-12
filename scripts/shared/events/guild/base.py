from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.constants import Settlement, Confirm, Battle, Retry, MainView
from scripts.shared.events.guild.enum import Guild
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.utils.retry import connection_retry
from scripts.shared.events.pvp.enum import PvP
from core.base.exceptions import GameError
from core.system.logger import log_msg
from scripts.shared.utils.hacks import apply_mode
import time

class GuildRaid:
    def __init__(self, serial):
        self.serial = serial

    def enter_menu(self):
        if exist(self.serial, Guild.RAID_TEXT):
            wait_click(self.serial, MainView.BACK)
            connection_retry(self.serial, wait_name=Guild.TEXT, timeout=40.0)
            return
        
        if exist(self.serial, MainStage.BTN):
            drag(self.serial, (200, 400), (800, 400))
            drag(self.serial, (200, 400), (800, 400))

        if exist_click(self.serial, Guild.BTN):
            connection_retry(self.serial, image_name=Guild.BTN, exception_msg="不在主畫面", timeout=40.0)
            return
        
        if wait(self.serial, Guild.TEXT, timeout=10.0):
            wait_click(self.serial, Guild.WAR_REWARD_POP, wait_time=2.0)
        else:
            raise GameError("無法進入公會")
        
    def _support_members(self):
        exist_click(self.serial, Guild.MEMBER_NAV_LIGHT)
        while True:
            if exist(self.serial, Guild.SUPPORT_DARK, threshold=0.97):
                return
            if exist_click(self.serial, Guild.SUPPORT_LIGHT, threshold=0.95, wait_time=1.5):
                exist_click(self.serial, Confirm.SMALL)
                break
            if exist(self.serial, Retry.TEXT1):
                exist_click(self.serial, Retry.BTN)

        connection_retry(self.serial, wait_name=Guild.SUPPORT_DARK, timeout=40.0, threshold=0.97)
        
    def do_quest(self):
        self._support_members()
        wait_click(self.serial, Guild.QUEST_BTN)
        while True:
            wait_click(self.serial, Guild.CLAIM, timeout=3.0)
            if exist(self.serial, Retry.TEXT1):
                exist_click(self.serial, Confirm.SMALL)
            elif exist(self.serial, Guild.QUEST_CLAIMED_TEXT, threshold=0.9):
                exist_click(self.serial, Confirm.SMALL)
            else:
                break
        wait_click(self.serial, MainView.CLOSE_BOARD2, threshold=0.9)
        

    def enter_raid_menu(self):
        if exist(self.serial, Guild.RAID_TEXT):
            return
        
        self.enter_menu()

        wait_click(self.serial, Guild.RAID_BTN)
        connection_retry(self.serial, wait_name=Guild.RAID_TEXT, exception_msg="無法進入公會副本", timeout=40.0)

    def enter_raid_stage(self):
        if not wait(self.serial, Guild.RAID_ATTACK, timeout=3.0):
            wait_click(self.serial, Battle.ENTER)
            connection_retry(self.serial, image_name=Battle.ENTER, exception_msg="無法進入公會副本關卡", timeout=40.0)
        for _ in range(3):
            if not wait_click(self.serial, Guild.TOUCH_SCREEN, timeout=3.0):
                break
        for _ in range(3):
            if not wait_click(self.serial, MainView.CLOSE_BOARD, threshold=0.9, timeout=3.0):
                break
        wait_click(self.serial, Guild.RAID_ATTACK)
        while True:
            if exist(self.serial, Guild.RAID_LIMITED):
                exist_click(self.serial, Confirm.CANCEL, wait_time=1.0)
                wait_click(self.serial, MainView.BACK)
                connection_retry(self.serial, wait_name=Battle.ENTER, timeout=40.0)
                return False
            if exist(self.serial, Retry.TEXT1):
                exist_click(self.serial, Retry.BTN)
            if exist(self.serial, Battle.PAUSE):
                break
        return True

    def raid_run(self):
        log_msg(self.serial, "公會副本任務開始")
        if not self.enter_raid_stage():
            return False

        wait_vanish(self.serial, Battle.PAUSE, threshold=0.97, timeout=60.0)

        log_msg(self.serial, "結算中")
        self.raid_settlement()
        log_msg(self.serial, "公會副本任務完成")
        return True

    def raid_settlement(self):
        connection_retry(self.serial, wait_name=Guild.LVL_UP, timeout=40.0)
        wait_click(self.serial, Guild.LVL_UP, wait_time=1.0)
        wait_click(self.serial, Guild.COMPLETE)
        wait_click(self.serial, Settlement.SILVER_BOX, wait_time=1.0)
        wait_click(self.serial, Confirm.BIG2, wait_time=1.5)
        wait_click(self.serial, Guild.COMPLETE)
        connection_retry(self.serial, wait_name=Guild.RAID_TEXT, timeout=40.0)
        wait_click(self.serial, MainView.BACK)
        connection_retry(self.serial, image_name=Guild.RAID_ATTACK, timeout=40.0)

def guild_raid_battle(serial):
    grd = GuildRaid(serial)
    # grd.enter_raid_menu()
    # for _ in range(3):
    #     if not grd.raid_run():
    #         break
    # grd.enter_menu()
    grd.do_quest()