from dataclasses import dataclass
import os
import time
from core.system.logging.logger import log_msg
from core.actions.vision import (
    exist_click, wait_click, wait, wait_vanish,
    drag, back, exist, get_pos,
    check_region_brightness
)
from core.actions.system import pull_account_file
from core.actions.vision import match_string_from_region
from scripts.shared.utils.retry import connection_retry
from core.base.exceptions import GameError
from scripts.shared.events.gacha.enum import GachaImg
from scripts.shared.constants import MainView, Confirm, Leonard
from scripts.shared.controller.context import GameContext

from scripts.shared.events.gacha.modules.ranger import PullRangerModule
from scripts.shared.events.gacha.navigator import GachaNavigator
from scripts.shared.events.gacha.config import GachaSession


class BaseGacha:
    def __init__(self, context: GameContext, session: GachaSession):
        self.ctx = context
        self.serial = context.serial

        self.pull_ranger_module = PullRangerModule(context, session)
        self.navigator = GachaNavigator(context, session)
        
    def enter_menu(self):
        self.navigator.enter_menu()

    def leave_menu(self):
        self.navigator.leave_menu() 
        
    def pull_ranger(self):
        self.pull_ranger_module.run()

def pull_ranger(context: GameContext):
    gacha = BaseGacha(context, session=GachaSession())
    gacha.enter_menu()
    gacha.pull_ranger()
    gacha.leave_menu()

def on_gacha_event(context: GameContext):
    gacha = BaseGacha(
        context,
        session=GachaSession(
            on_event=True
        )
    )
    gacha.enter_menu()