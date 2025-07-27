import os
import time
from configparser import ConfigParser
from fuzzywuzzy import fuzz, process
from action import (
    wait_click, wait, wait_vanish,
    match_string_from_region, drag, back, get_clipboard_text,
    pull_account_file
)
from common.utils import open_game_with_hacks, on_main_view
from exceptions import GameError
from logger import log_msg

class Gacha:
    def __init__(self, serial, config_path="./bin/config.ini"):
        self.serial = serial
        self.config_path = config_path
        self.target_count, self.expected_names, self.name_map = self._load_config()
        self.matched = []
        self.rangers = []
        self.rangers_short_names = []

    def _load_config(self):
        config = ConfigParser()
        config.read(self.config_path, encoding="utf-8")

        target_count = int(config.get("SETTINGS", "herowant", fallback="1"))
        expected_names = []
        name_map = {}

        for key in config["SETTINGS"]:
            if key.startswith("name"):
                raw = config["SETTINGS"][key]
                candidates, display_name = raw.split("=")
                name_parts = candidates.split("+")
                full_name = " ".join(name_parts)
                expected_names.append(full_name)
                name_map[full_name] = display_name

        return target_count, expected_names, name_map


    def _match_from_region(self, region=None):
        for name in self.expected_names:
            if match_string_from_region(self.serial, name, region = (630, 216, 950, 300), threshold=0.95):
                return name
        return None

    def enter_gacha(self):
        if not wait(self.serial, "main_stage_btn.png", timeout=15.0):
            raise GameError("不在主畫面")

        if wait_click(self.serial, "skip.png", timeout=5.0):
            wait_click(self.serial, "confirm_small.png", wait_time=3.0)

        if not wait(self.serial, "gacha_icon.png", timeout=30.0, threshold=0.97):
            raise GameError("不在主畫面")
        wait_click(self.serial, "gacha_icon.png", timeout=7.0)
        if not wait(self.serial, "gacha_text.png", timeout=20.0):
            raise GameError("無法進入扭蛋頁")

    def pull(self, pool: str = "gacha_boss_pool.png", attempts: int = 10):
        log_msg(self.serial, f"開抽扭蛋, 預計要抽到 {self.target_count} 個 ranger 才會留下帳號")

        if not wait(self.serial, "gacha_text.png", timeout=20.0):
            raise GameError("不在扭蛋頁")
        for _ in range(5):
            if wait_click(self.serial, pool, timeout=3.0):
                break
            drag(self.serial, (980, 450), (980, 266), wait_time=1.0)

        success = False
        for _ in range(attempts):
            if not wait_click(self.serial, "gacha_pull_tickets.png"):
                break
            wait_click(self.serial, "confirm_small.png", wait_time=2.0)
            wait_click(self.serial, "gacha_skip.png", timeout=20.0, wait_time=2.0)
        
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
            self.store_acc()
        else:
            wait_click(self.serial, "back.png", timeout=20.0)
            print(f"只抽到 {len(self.rangers)} 名角色，捨棄帳號。")

    def store_acc(self):
        log_msg(self.serial, f"已抽中足夠的腳色，準備拉帳號檔")

        wait_click(self.serial, "back.png")
        on_main_view(self.serial)
        wait_click(self.serial, "settings_btn.png", timeout=10.0, wait_time=1.5)
        wait_click(self.serial, "settings_account_nav.png")
        wait_click(self.serial, "settings_uid_copy.png")
        wait_click(self.serial, "confirm_small.png")
        uid = get_clipboard_text(self.serial).strip()
        pull_account_file(self.serial, uid, self.rangers_short_names)