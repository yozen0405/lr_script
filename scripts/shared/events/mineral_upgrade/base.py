from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStageImg
from core.system.config import Config
from scripts.shared.constants import Leonard, Battle
from scripts.shared.events.pvp.enum import PvP
from scripts.shared.events.mineral_upgrade.enum import MineralUpgradeImg
from scripts.shared.controller.context import GameContext

class MineralUpgrade:
    def __init__(self, context: GameContext):
        self.ctx = context
        self.enter_pos = None

    def on_page(self) -> bool:
        return exist(self.ctx.serial, MineralUpgradeImg.TEXT.value, threshold=0.9)

    def enter_menu(self):
        if not exist(self.ctx.serial, MineralUpgradeImg.TEXT.value, threshold=0.9):
            if not wait_click(self.ctx.serial, MineralUpgradeImg.BTN.value, threshold=0.8):
                raise GameError("無法進入礦石升級活動選單")
            connection_retry(self.ctx.serial, appear=MineralUpgradeImg.TEXT.value, timeout=40.0)
    
    def leave_menu(self):
        if not exist_click(self.ctx.serial, MainView.BACK.value):
            raise GameError("無法離開礦石升級活動選單")
        connection_retry(self.ctx.serial, vanish=MineralUpgradeImg.TEXT.value, timeout=40.0)

    def _handle_times(self):
        if not exist_click(self.ctx.serial, MineralUpgradeImg.MAX.value):
            raise GameError("無法升級")
        for _ in range(7):
            wait_click(self.ctx.serial, MineralUpgradeImg.MINUS.value)
        wait_click(self.ctx.serial, Confirm.SMALL.value)
        connection_retry(self.ctx.serial, appear=MineralUpgradeImg.SUCCESS.value, timeout=40.0)

        for _ in range(3):
            if not exist_click(self.ctx.serial, MineralUpgradeImg.SUCCESS.value):
                break

    def upgrade_production_rate(self):
        pos = get_pos(self.ctx.serial, MineralUpgradeImg.PRODUCTION_RATE_TEXT.value, threshold=0.9)
        if not pos:
            raise GameError("找不到升級文字")
        x, y = pos
        wait_click(self.ctx.serial, (x, y + 350))
        
        self._handle_times()

    def run(self):
        self.enter_menu()
        self.upgrade_production_rate()
        self.leave_menu()

def mineral_upgrade(context: GameContext):
    mineral_upgrade_event = MineralUpgrade(context)
    mineral_upgrade_event.run()

def on_mineral_upgrade_page(context: GameContext) -> bool:
    handler = MineralUpgrade(context)
    return handler.on_page()