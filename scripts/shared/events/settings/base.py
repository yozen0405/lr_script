from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.system import get_clipboard_text, pull_account_file, clear_game_storage, force_close_all_apps
from core.actions.vision import get_device_uid
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStageImg
from core.system.config import Config
from scripts.shared.constants import Leonard, Battle
from scripts.shared.events.pvp.enum import PvPImg
from scripts.shared.events.settings.enum import SettingsImg
from scripts.shared.controller.context import GameContext
import time
import threading

class SettingsBase:
    _clipboard_lock = threading.Lock()

    def __init__(self, context: GameContext):
        self.ctx = context

    def enter_menu(self):
        if not wait_click(self.ctx.serial, SettingsImg.BTN.value, threshold=0.8):
            raise GameError("無法進入Settings選單")
        connection_retry(self.ctx.serial, appear=SettingsImg.ACC_NAV.value, timeout=40.0)
    
    def finalize_acc(self):
        if self.ctx.pulled_rangers is not None and len(self.ctx.pulled_rangers) > 0:
            self.store_acc()
        else:
            log_msg(self.ctx.serial, f"沒抽到任何角色，捨棄帳號。")
        force_close_all_apps(self.ctx.serial)
        clear_game_storage(self.ctx.serial)

    def store_acc(self):
        log_msg(self.ctx.serial, f"已抽中足夠的腳色，準備拉帳號檔")
        wait_click(self.ctx.serial, SettingsImg.ACC_NAV.value, wait_time=1.0)
        
        log_msg(self.ctx.serial, "正在排隊等待剪貼簿權限...")

        with SettingsBase._clipboard_lock:
            log_msg(self.ctx.serial, ">>> 取得剪貼簿鎖定，開始執行複製流程")
            if not wait_click(self.ctx.serial, SettingsImg.ACC_UID_COPY_BTN.value):
                raise GameError("無法點擊複製UID按鈕")
            
            wait_click(self.ctx.serial, Confirm.SMALL.value)
            
            uid = get_clipboard_text(self.ctx.serial)
            
            if uid == "":
                uid = get_device_uid(self.ctx.serial)

            if not pull_account_file(self.ctx.serial, uid, self.ctx.pulled_rangers):
                raise GameError("無法拉取帳號檔案")

            log_msg(self.ctx.serial, "<<< 帳號備份完成，釋放鎖定")

            if not pull_account_file(self.ctx.serial, uid, self.ctx.pulled_rangers):
                raise GameError("無法拉取帳號檔案")

            log_msg(self.ctx.serial, "帳號備份完成")

def finalize_account(context: GameContext):
    settings = SettingsBase(context)
    settings.enter_menu()
    settings.finalize_acc()