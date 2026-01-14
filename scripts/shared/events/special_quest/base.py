from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStageImg
from core.system.config import Config
from scripts.shared.constants import Leonard, Battle
from scripts.shared.events.pvp.enum import PvPImg
from scripts.shared.events.special_quest.enum import SpecialQuestImg
from scripts.shared.controller.context import GameContext

class SpecialQuest:
    def __init__(self, context: GameContext):
        self.ctx = context
        self.enter_pos = None

    def on_page(self) -> bool:
        return exist(self.ctx.serial, SpecialQuestImg.TEXT.value, threshold=0.9)

    def enter_menu(self):
        if not exist(self.ctx.serial, SpecialQuestImg.TEXT.value, threshold=0.9):
            if not wait_click(self.ctx.serial, SpecialQuestImg.BTN.value, threshold=0.8):
                raise GameError("無法進入Special quest活動選單")
            connection_retry(self.ctx.serial, appear=SpecialQuestImg.TEXT.value, timeout=40.0)
    
    def leave_menu(self):
        if not exist_click(self.ctx.serial, MainView.CLOSE_BOARD.value):
            raise GameError("無法離開Special quest活動選單")
        connection_retry(self.ctx.serial, vanish=SpecialQuestImg.TEXT.value, timeout=40.0)

    def on_event(self):
        self.enter_menu()
        self.leave_menu()
    
def special_quest_event(context: GameContext):
    special_quest = SpecialQuest(context)
    special_quest.on_event()