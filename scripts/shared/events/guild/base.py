from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.constants import Settlement, Confirm, Battle, Retry, MainView, Leonard
from scripts.shared.events.guild.enum import Guild, GuildRaidSide
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.utils.retry import connection_retry
from scripts.shared.events.pvp.enum import PvPImg
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from scripts.shared.utils.hacks import apply_mode
import time

class BaseGuild:
    def __init__(self, serial):
        self.serial = serial

    def enter_menu(self):
        if exist(self.serial, Guild.RAID_TEXT.value):
            wait_click(self.serial, MainView.BACK.value)
            connection_retry(self.serial, appear=Guild.TEXT.value, retry=MainView.BACK.value, timeout=40.0)
            return
        
        if exist(self.serial, MainStageImg.BTN.value):
            drag(self.serial, (200, 400), (800, 400))
            drag(self.serial, (200, 400), (800, 400))

        if exist_click(self.serial, Guild.BTN.value):
            connection_retry(self.serial, vanish=Guild.BTN.value, retry=Guild.BTN.value, timeout=40.0)
        
        self._handle_anime()
        self._handle_enter()

    def _handle_anime(self):
        for _ in range(7):
            if exist(self.serial, Guild.TEXT.value):
                break
            if not wait_click(self.serial, Guild.ANIME.value, threshold=0.8):
                break

        connection_retry(self.serial, appear=Guild.TEXT.value, timeout=40.0)

        cnt = 0
        while True:
            if exist_click(self.serial, Leonard.TP_POINT2.value, threshold=0.85):
                cnt = 0
                continue
            if exist_click(self.serial, Leonard.TP_POINT_REV.value, threshold=0.9):
                cnt = 0
                continue
            if exist_click(self.serial, Leonard.TP_CLAP2.value, threshold=0.9):
                cnt = 0
                continue
            if exist_click(self.serial, Leonard.TP_HAPPY2.value, threshold=0.9):
                cnt = 0
                continue
            if exist_click(self.serial, Leonard.TP_THUMBS_UP.value, threshold=0.9):
                cnt = 0
                continue
            cnt += 1
            if cnt >= 3:
                break


    def _handle_enter(self):
        while True:
            if exist(self.serial, Guild.TEXT.value, threshold=0.999):
                break
            exist_click(self.serial, Battle.ANIME.value, threshold=0.6)
            exist_click(self.serial, Guild.WAR_REWARD_POP.value)
            if exist(self.serial, Guild.PURCHASE_POP.value):
                if not exist_click(self.serial, Confirm.SMALL.value):
                    exist_click(self.serial, MainView.CLOSE_BOARD.value)
            if exist(self.serial, Guild.ACCEPT_SUPPORT_POP.value):
                exist_click(self.serial, Confirm.SMALL.value)
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.BTN.value)

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

    def _do_quest(self):
        while True:
            if exist(self.serial, Guild.QUEST_CLAIMED_TEXT.value, threshold=0.9):
                exist_click(self.serial, Confirm.SMALL.value)
            elif exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Confirm.SMALL.value)
            elif wait_click(self.serial, Guild.CLAIM.value):
                continue
            else:
                return
        
    def do_quest(self):
        self._support_members()
        wait_click(self.serial, Guild.QUEST_BTN.value)
        connection_retry(self.serial, appear=Guild.QUEST_TEXT.value, retry=Guild.QUEST_BTN.value, timeout=40.0)

        if exist_click(self.serial, Leonard.TP_CLAP2.value):
            for _ in range(3):
                if not wait_click(self.serial, Leonard.TP_CLAP2.value, timeout=3.0):
                    break

        self._do_quest()
        wait_click(self.serial, Guild.WEEKLY_QUEST_NAV.value)
        self._do_quest()
        
        wait_click(self.serial, MainView.CLOSE_BOARD.value, threshold=0.9, timeout=3.0)
        connection_retry(self.serial, vanish=Guild.QUEST_TEXT.value, retry=[(MainView.CLOSE_BOARD.value, 0.9)], timeout=40.0)

class GuildRaid:
    def __init__(self, serial):
        self.serial = serial
        self.base_guild = BaseGuild(serial)

    def enter_guild_menu(self):
        self.base_guild.enter_menu()

    def handle_anime(self):
        if not wait_click(self.serial, Leonard.TP_POINT.value, threshold=0.8, timeout=3.0, wait_time=1.0):
            return
        
        for _ in range(2):
            wait_click(self.serial, Guild.RAID_TEXT.value, timeout=3.0, wait_time=1.0)

    def enter_raid_menu(self):
        if exist(self.serial, Guild.RAID_TEXT.value):
            return
        
        self.enter_guild_menu()

        wait_click(self.serial, Guild.RAID_BTN.value)
        connection_retry(self.serial, appear=Guild.RAID_TEXT.value, timeout=40.0)

    def enter_raid_stage(self, side):
        self.handle_anime()

        if not wait(self.serial, Guild.RAID_ATTACK.value, timeout=3.0):
            if side == 1:
                wait_click(self.serial, Battle.ENTER.value, region=GuildRaidSide.LEFT.value)
            else:
                wait_click(self.serial, Battle.ENTER.value, region=GuildRaidSide.RIGHT.value)

            connection_retry(self.serial, vanish=Battle.ENTER.value, timeout=40.0)
        for _ in range(10):
            if wait(self.serial, Guild.RAID_ATTACK.value, threshold=0.999):
                break
            wait_click(self.serial, Guild.TOUCH_SCREEN.value, timeout=3.0)
            wait_click(self.serial, MainView.CLOSE_BOARD.value, threshold=0.9, timeout=3.0)
        
        exist_click(self.serial, Guild.AUTO_BTN_OFF.value, threshold=0.999)
        wait_click(self.serial, Guild.RAID_ATTACK.value)

        start_time = time.time()
        while time.time() - start_time < 120.0:
            if exist(self.serial, Guild.RAID_LIMITED.value):
                exist_click(self.serial, Confirm.CANCEL_SMALL.value, wait_time=1.0)
                wait_click(self.serial, MainView.BACK.value)
                connection_retry(self.serial, appear=Battle.ENTER.value, timeout=40.0)
                return False
            if exist(self.serial, Guild.RAID_OCCUPIED.value):
                exist_click(self.serial, Confirm.SMALL.value)
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.BTN.value)
            if exist(self.serial, Guild.RAID_TRY_AGAIN.value):
                exist_click(self.serial, Confirm.SMALL.value, wait_time=1.0)
                wait(self.serial, Guild.RAID_ATTACK.value)
            if exist(self.serial, Battle.PAUSE.value):
                return True
        raise GameError("進入公會副本失敗")

    def raid_run(self, side: int = 1):
        log_msg(self.serial, "公會副本任務開始")
        if not self.enter_raid_stage(side=side):
            return False

        wait_vanish(self.serial, Battle.PAUSE.value, threshold=0.97, timeout=60.0)

        log_msg(self.serial, "結算中")
        self.raid_settlement()
        log_msg(self.serial, "公會副本任務完成")
        return True

    def raid_settlement(self):
        connection_retry(self.serial, appear=[(Guild.LVL_UP.value), (Guild.COMPLETE.value)], timeout=40.0)
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
    
    side = 1
    for i in range(3):
        if i == 2:
            side = 2
        result = grd.raid_run(side=side)
        if not result:
            break

    gbase = BaseGuild(serial)
    gbase.enter_menu()
    gbase.do_quest()