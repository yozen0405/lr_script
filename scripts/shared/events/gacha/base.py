import os
import time
from configparser import ConfigParser
from core.system.config import Config
from core.system.logger import log_msg
from core.actions.screen import (
    wait_click, wait, wait_vanish,
    drag, back
)
from core.actions.system import get_clipboard_text
from core.actions.system import pull_account_file
from core.actions.ocr import match_string_from_region
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.utils.retry import connection_retry
from core.base.exceptions import GameError
from scripts.shared.events.gacha.enum import Gacha
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.constants import MainView, Confirm, Leonard

class BaseGacha:
    def __init__(self, serial):
        self.serial = serial
        config = Config()

        self.target_count = config.target_count
        self.expected_names = config.expected_names
        self.name_map = config.name_map
        self.pool_image = config.get("pool", fallback=Gacha.FALLBACK_POOL)

        self.matched = []
        self.rangers = []
        self.rangers_short_names = []

    def _match_from_region(self):
        for name in self.expected_names:
            if match_string_from_region(self.serial, name, region = (630, 216, 950, 300), threshold=0.95):
                return name
            if match_string_from_region(self.serial, name, region = (630, 230, 950, 300), threshold=0.95):
                return name
        return None

    def enter_gacha(self):
        if not wait(self.serial, MainStage.BTN, timeout=15.0):
            raise GameError("不在主畫面")

        if not wait(self.serial, Gacha.ICON, timeout=30.0, threshold=0.97):
            raise GameError("不在主畫面")
        wait_click(self.serial, Gacha.ICON, timeout=7.0)
        connection_retry(self.serial, image_name=Gacha.ICON, exception_msg="不在扭蛋頁", timeout=40.0)

        self._skip_tutorial()

    def _skip_tutorial(self):
        if not wait(self.serial, Leonard.TP_POINT, timeout=2.0):
            return
        for _ in range(5):
            wait_click(self.serial, Gacha.TEXT, wait_time=1.0)
        wait_click(self.serial, Gacha.EQUIP_NAV, wait_time=1.0)
        wait_click(self.serial, Gacha.TEXT, wait_time=1.0)
        wait_click(self.serial, Gacha.GEAR_GAUGE, wait_time=1.0)

        for _ in range(3):
            wait_click(self.serial, MainView.CLOSE_BOARD2, wait_time=1.0, threshold=0.5)
        wait_click(self.serial, Gacha.SHOP, wait_time=1.0)
        for _ in range(2):
            wait_click(self.serial, MainView.BACK, wait_time=1.0, threshold=0.5)
        
        wait_click(self.serial, Gacha.TEXT, wait_time=1.0)

    def pull(self, attempts: int = 15):
        log_msg(self.serial, f"開抽扭蛋, 預計要抽到 {self.target_count} 個 ranger 才會留下帳號")

        if not wait(self.serial, Gacha.TEXT, timeout=20.0):
            raise GameError("不在扭蛋頁")
        for _ in range(5):
            if wait_click(self.serial, self.pool_image, timeout=3.0):
                break
            drag(self.serial, (980, 450), (980, 266), wait_time=1.0)

        success = False
        for _ in range(attempts):
            if not wait_click(self.serial, Gacha.TICKET_PULL):
                break
            wait_click(self.serial, Confirm.SMALL, wait_time=2.0)
            wait_click(self.serial, Gacha.SKIP, timeout=20.0, wait_time=2.0)
    
            wait_click(self.serial, Confirm.SMALL)
            hero = self._match_from_region()
            wait_click(self.serial, Gacha.CONFIRM, wait_time=2.0)
            if hero:
                log_msg(self.serial, f"抽到 {hero} 了!")
                if hero not in self.rangers:
                    self.rangers.append(hero)

                hero = self.name_map[hero]
                if hero not in self.rangers_short_names:
                    self.rangers_short_names.append(hero)
                
                if len(self.rangers) >= self.target_count:
                    success = True

            self.finalize_acc(success)

    def finalize_acc(self, success: bool):
        if success:
            self._log_gacha_rangers()
            self.store_acc()
        else:
            wait_click(self.serial, MainView.BACK, timeout=20.0)
            print(f"只抽到 {len(self.rangers)} 名角色，捨棄帳號。")

    def _log_gacha_rangers(self):
        log_msg(self.serial, "")
        print("===== Gacha rangers =====")
        for i, name in enumerate(self.rangers, 1):
            print(f"{i}. {name}")
        print("=" * 27)

    def store_acc(self):
        log_msg(self.serial, f"已抽中足夠的腳色，準備拉帳號檔")

        wait_click(self.serial, MainView.BACK, timeout=20.0)
        on_main_view(self.serial, skip_included=True)
        wait_click(self.serial, MainView.SETTINGS, timeout=10.0, wait_time=1.5)
        wait_click(self.serial, Gacha.ACC_NAV)
        wait_click(self.serial, Gacha.ACC_UID_COPY)
        wait_click(self.serial, Confirm.SMALL)
        uid = get_clipboard_text(self.serial).strip()
        pull_account_file(self.serial, uid, self.rangers_short_names)