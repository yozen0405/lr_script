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
        if exist(self.serial, Guild.RAID_TEXT.value):
            wait_click(self.serial, MainView.BACK.value)
            connection_retry(self.serial, appear=Guild.TEXT.value, timeout=40.0)
            return
        
        if exist(self.serial, MainStage.BTN.value):
            drag(self.serial, (200, 400), (800, 400))
            drag(self.serial, (200, 400), (800, 400))

        if exist_click(self.serial, Guild.BTN.value):
            connection_retry(self.serial, vanish=Guild.BTN.value, timeout=40.0)
            
        if wait(self.serial, Guild.TEXT.value, timeout=10.0):
            wait_click(self.serial, Guild.WAR_REWARD_POP.value, wait_time=2.0)
        else:
            raise GameError("無法進入公會")
        
    def _support_members(self):
        exist_click(self.serial, Guild.MEMBER_NAV_LIGHT.value)
        while True:
            if exist(self.serial, Guild.SUPPORT_DARK.value, threshold=0.97):
                return
            if exist_click(self.serial, Guild.SUPPORT_LIGHT.value, threshold=0.95, wait_time=1.5):
                exist_click(self.serial, Confirm.SMALL.value)
                break
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.BTN.value)

        connection_retry(self.serial, appear=(Guild.SUPPORT_DARK.value, 0.97), timeout=40.0)
        
    def do_quest(self):
        self._support_members()
        wait_click(self.serial, Guild.QUEST_BTN.value)
        while True:
            if exist(self.serial, Guild.QUEST_CLAIMED_TEXT.value, threshold=0.9):
                exist_click(self.serial, Confirm.SMALL.value)
            elif exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Confirm.SMALL.value)
            elif wait_click(self.serial, Guild.CLAIM.value, timeout=3.0):
                continue
            else:
                wait_click(self.serial, MainView.CLOSE_BOARD2.value, threshold=0.9, timeout=3.0)
                if not wait_vanish(self.serial, MainView.CLOSE_BOARD2.value, threshold=0.9, timeout=3.0):
                    continue
                else:
                    break
        

    def enter_raid_menu(self):
        if exist(self.serial, Guild.RAID_TEXT.value):
            return
        
        self.enter_menu()

        wait_click(self.serial, Guild.RAID_BTN.value)
        connection_retry(self.serial, appear=Guild.RAID_TEXT.value, timeout=40.0)

    def enter_raid_stage(self):
        if not wait(self.serial, Guild.RAID_ATTACK.value, timeout=3.0):
            wait_click(self.serial, Battle.ENTER.value)
            connection_retry(self.serial, vanish=Battle.ENTER.value, timeout=40.0)
        for _ in range(10):
            wait_click(self.serial, Guild.TOUCH_SCREEN.value, timeout=3.0)
            wait_click(self.serial, MainView.CLOSE_BOARD2.value, threshold=0.9, timeout=3.0)
            if wait_click(self.serial, Guild.RAID_ATTACK.value):
                break
        while True:
            if exist(self.serial, Guild.RAID_LIMITED.value):
                exist_click(self.serial, Confirm.CANCEL.value, wait_time=1.0)
                wait_click(self.serial, MainView.BACK.value)
                connection_retry(self.serial, appear=Battle.ENTER.value, timeout=40.0)
                return False
            if exist(self.serial, Guild.RAID_OCCUPIED.value):
                exist_click(self.serial, Confirm.SMALL.value)
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.BTN.value)
            if exist(self.serial, Battle.PAUSE.value):
                break
        return True

    def raid_run(self):
        log_msg(self.serial, "公會副本任務開始")
        if not self.enter_raid_stage():
            return False

        wait_vanish(self.serial, Battle.PAUSE.value, threshold=0.97, timeout=60.0)

        log_msg(self.serial, "結算中")
        self.raid_settlement()
        log_msg(self.serial, "公會副本任務完成")
        return True

    def raid_settlement(self):
        connection_retry(self.serial, appear=Guild.LVL_UP.value, timeout=40.0)
        wait_click(self.serial, Guild.LVL_UP.value, wait_time=1.0)
        wait_click(self.serial, Guild.COMPLETE.value)
        wait_click(self.serial, Settlement.SILVER_BOX.value, wait_time=1.0)
        wait_click(self.serial, Confirm.BIG2.value, wait_time=1.5)
        wait_click(self.serial, Guild.COMPLETE.value)
        connection_retry(self.serial, appear=Guild.RAID_TEXT.value, timeout=40.0)
        wait_click(self.serial, MainView.BACK.value)
        connection_retry(self.serial, vanish=Guild.RAID_ATTACK.value, timeout=40.0)

def guild_raid_battle(serial):
    grd = GuildRaid(serial)
    grd.enter_raid_menu()
    for _ in range(3):
        if not grd.raid_run():
            break
    grd.enter_menu()
    grd.do_quest()