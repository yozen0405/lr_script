import os
import time
from configparser import ConfigParser
from core.system.config import Config
from core.system.logger import log_msg
from core.actions.screen import (
    exist_click, wait_click, wait, wait_vanish,
    drag, back, exist, get_pos,
    check_region_brightness
)
from core.actions.system import get_clipboard_text
from core.actions.system import pull_account_file
from core.actions.ocr import match_string_from_region
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.utils.retry import connection_retry
from core.base.exceptions import GameError
from scripts.shared.events.gacha.enum import GachaImg
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.constants import MainView, Confirm, Leonard, Retry
from scripts.shared.controller.context import GameContext
from scripts.shared.events.gacha.interrupts.tutorial import TutorialStrategy
from typing import Optional

class PullRangerModule:
    def __init__(self, context: GameContext):
        self.ctx = context
        config = Config()

        self.expected_full_names = config.expected_names
        self.name_map = config.name_map # full name to short name
        self.pool = config.get("pool", fallback=GachaImg.FALLBACK_POOL.value)

        self.pulled_full_names = []
        self.pulled_short_names = []

    def _match_from_region(self) -> Optional[str]:
        for name in self.expected_full_names:
            if match_string_from_region(self.ctx.serial, name, region = (630, 216, 950, 300), threshold=0.95):
                return name
            if match_string_from_region(self.ctx.serial, name, region = (630, 230, 950, 300), threshold=0.95):
                return name
        return None
    
    def _log(self):
        log_msg(self.ctx.serial, "")
        print("===== Gacha rangers =====")
        if len(self.pulled_full_names) == 0:    
            print("本次抽取未獲得任何 ranger")
            return
        for i, name in enumerate(self.pulled_full_names, 1):
            print(f"{i}. {name}")
        print("=" * 27)
    
    def _find_pool(self):
        for _ in range(5):
            if exist_click(self.ctx.serial, self.pool):
                return
            drag(self.ctx.serial, (980, 450), (980, 266))
        raise GameError("無法找到指定扭蛋池")
    
    def _check_ranger_in_pool(self) -> bool:
        full_name = self._match_from_region()
        if full_name:
            log_msg(self.ctx.serial, f"抽到 {full_name} 了!")
            if full_name not in self.pulled_full_names:
                self.pulled_full_names.append(full_name)

            short_name = self.name_map[full_name]
            if short_name not in self.pulled_short_names:
                self.pulled_short_names.append(short_name)
            return True
        return False
    
    def _pull_one(self):
        start_time = time.time()
        fg = False
        succ = False
        while time.time() - start_time < 60.0:
            if exist(self.ctx.serial, Retry.TEXT1.value) or exist(self.ctx.serial, Retry.TEXT2.value):
                exist_click(self.ctx.serial, Retry.BTN.value)
                continue

            if not fg and exist_click(self.ctx.serial, GachaImg.TICKET_PULL.value):
                continue

            if fg and exist(self.ctx.serial, GachaImg.TEXT.value, threshold=0.8):
                return succ

            if exist_click(self.ctx.serial, GachaImg.SKIP.value):
                continue

            if exist(self.ctx.serial, GachaImg.SUCCESS_TEXT.value, threshold=0.9):
                fg = True
                succ = self._check_ranger_in_pool()
                wait_click(self.ctx.serial, GachaImg.CONFIRM.value)
                continue
        raise GameError("抽取扭蛋超時")

    def pull(self, attempts: int = 15):
        log_msg(self.ctx.serial, f"開抽扭蛋, 預計要抽到 1 個 ranger 才會留下帳號")

        self.reset()
        self._find_pool()        

        for _ in range(attempts):
            if not exist(self.ctx.serial, GachaImg.TICKET_PULL.value):
                break
            self._pull_one()
            
        self._log()
        self.ctx.pulled_rangers = self.pulled_short_names

    def reset(self):
        self.pulled_full_names = []
        self.pulled_short_names = []
