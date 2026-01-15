from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos, check_region_brightness
from scripts.shared.constants import Settlement, Confirm, Battle, Retry, MainView, Leonard
from scripts.shared.constants.view import GameView
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.utils.retry import connection_retry
from scripts.shared.events.pvp.enum import PvPImg
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.controller.context import GameContext
from scripts.shared.events.pvp.session import StageSession
import time

class StageBattle:
    def __init__(self, context: GameContext, session: StageSession):
        self.ctx = context
        self.session = session

    def run(self):
        self.session.lose = False

        start_time = time.time()
        while time.time() - start_time < 120:
            if exist(self.ctx.serial, Retry.TEXT1.value):
                exist_click(self.ctx.serial, Retry.BTN.value)

            if exist(self.ctx.serial, PvPImg.SETTLEMENT_TEXT.value, threshold=0.9):
                return

            # if exist error found text, mark lose

        raise GameError("戰鬥超時")