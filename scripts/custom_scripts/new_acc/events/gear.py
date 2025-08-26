from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.hacks import apply_mode
from core.base.exceptions import GameError
from scripts.shared.events.main_stage.selector import main_stage_finish_new
from scripts.shared.events.login import first_guest_login
from scripts.shared.constants import GameView, Settlement, Battle, Confirm, MainView, Leonard, Retry, Positions
from scripts.custom_scripts.new_acc.enum import PreStage, Phase1UI, Quests
from scripts.shared.events.teams.enum import Teams
from scripts.shared.events.gacha.enum import Gacha

class GearEvent:
    def __init__(self, serial):
        self.serial = serial
    
    def _is_active(self):
        