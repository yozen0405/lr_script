import os
import time
from configparser import ConfigParser
from core.system.config import Config
from core.system.logger import log_msg
from core.actions.screen import (
    wait_click, wait, wait_vanish,
    drag, back, get_clipboard_text,
    pull_account_file
)
from core.actions.ocr import match_string_from_region
from scripts.shared.utils.game_view import on_main_view
from core.base.exceptions import GameError

class Gacha:
    def __init__(self, serial, config_path="./bin/config.ini"):
        self.serial = serial
        config = Config()

        self.target_count = config.target_count
        self.expected_names = config.expected_names
        self.name_map = config.name_map
        self.pool_image = config.get("pool", fallback="gacha_boss_pool.png")

        self.matched = []
        self.rangers = []
        self.rangers_short_names = []

    def _match_from_region(self, region=None):
        for name in self.expected_names:
            if match_string_from_region(self.serial, name, region = (630, 216, 950, 300), threshold=0.95):
                return name
            if match_string_from_region(self.serial, name, region = (630, 230, 950, 300), threshold=0.95):
                return name
        return None

    def enter_gacha(self):
        if not wait(self.serial, "main_stage_btn.png", timeout=15.0):
            raise GameError("不在主畫面")

        if not wait(self.serial, "gacha_icon.png", timeout=30.0, threshold=0.97):
            raise GameError("不在主畫面")
        wait_click(self.serial, "gacha_icon.png", timeout=7.0)
        if not wait(self.serial, "gacha_text.png", timeout=40.0):
            raise GameError("無法進入扭蛋頁")

        self._skip_tutorial()

    def _skip_tutorial(self):
        pass

    def pull(self, attempts: int = 15):
        log_msg(self.serial, f"開抽扭蛋, 預計要抽到 {self.target_count} 個 ranger 才會留下帳號")

        if not wait(self.serial, "gacha_text.png", timeout=20.0):
            raise GameError("不在扭蛋頁")
        for _ in range(5):
            if wait_click(self.serial, self.pool_image, timeout=3.0):
                break
            drag(self.serial, (980, 450), (980, 266), wait_time=1.0)

        success = False
        for _ in range(attempts):
            if not wait_click(self.serial, "gacha_pull_tickets.png"):
                break
            wait_click(self.serial, "confirm_small.png", wait_time=2.0)
            wait_click(self.serial, "gacha_skip.png", timeout=20.0, wait_time=2.0)
    
            wait_click(self.serial, "confirm_small.png")
            hero = self._match_from_region()
            wait_click(self.serial, "gacha_confirm.png", wait_time=2.0)
            if hero:
                log_msg(self.serial, f"抽到 {hero} 了!")
                if hero not in self.rangers:
                    self.rangers.append(hero)

                hero = self.name_map[hero]
                if hero not in self.rangers_short_names:
                    self.rangers_short_names.append(hero)
                
                if len(self.rangers) >= self.target_count:
                    success = True

        if success:
            self._log_gacha_rangers()
            self.store_acc()
        else:
            wait_click(self.serial, "back.png", timeout=20.0)
            print(f"只抽到 {len(self.rangers)} 名角色，捨棄帳號。")

    def _log_gacha_rangers(self):
        log_msg(self.serial, "")
        print("===== Gacha rangers =====")
        for i, name in enumerate(self.rangers, 1):
            print(f"{i}. {name}")
        print("=" * 27)


    def store_acc(self):
        log_msg(self.serial, f"已抽中足夠的腳色，準備拉帳號檔")

        wait_click(self.serial, "back.png", timeout=20.0)
        on_main_view(self.serial, skip_included=True)
        wait_click(self.serial, "settings_btn.png", timeout=10.0, wait_time=1.5)
        wait_click(self.serial, "settings_account_nav.png")
        wait_click(self.serial, "settings_uid_copy.png")
        wait_click(self.serial, "confirm_small.png")
        uid = get_clipboard_text(self.serial).strip()
        pull_account_file(self.serial, uid, self.rangers_short_names)