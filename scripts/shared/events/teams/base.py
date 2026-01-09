from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos, check_region_brightness
from core.actions.vision import back
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.constants.leonard import Leonard
from scripts.shared.events.teams.pages.rangers.teams.base import TeamsPage
from scripts.shared.events.teams.pages.rangers.info.base import RangerInfoPage
from scripts.shared.events.teams.pages.rangers.upgrade.base import RangerUpgradePage
from scripts.shared.events.teams.pages.rangers.filters.base import RangerFilterPage
from scripts.shared.events.teams.pages.gears.base import GearBase
from scripts.shared.controller.context import GameContext
import time

class TeamsBase():
    def __init__(self, context: GameContext):
        self.ctx = context

        self.teams_page = TeamsPage(context)
        self.ranger_info_page = RangerInfoPage(context)
        self.ranger_upgrade_page = RangerUpgradePage(context)
        self.ranger_filter_page = RangerFilterPage(context)
        self.gear_page = GearBase(context)

    def enter_menu(self):
        self.teams_page.enter_menu()
        log_msg(self.ctx.serial, "Entered teams menu.")

    def on_upgrade_event(self):
        if not exist_click(self.ctx.serial, TeamsImg.RENE_MAINVIEW.value, wait_time=1.0) and \
           not exist_click(self.ctx.serial, TeamsImg.SHEEP_MAINVIEW.value, wait_time=1.0):
            raise GameError("Not on Rene main view.")
        
        if exist(self.ctx.serial, TeamsImg.RENE_UPGRADE_TEXT.value, threshold=0.9):
            self.ranger_info_page.on_event()
            self.ranger_upgrade_page.on_event()
        else:
            self.ranger_info_page.on_event()
            self.gear_page.on_event()
    
    def on_team_event(self):
        self.teams_page.on_jessica_event()

    def upgrade_ranger(self, type: int = 1):
        self.ranger_filter_page.filter(filter_list=[TeamsImg.FILTER_SIX_STARS, TeamsImg.FILTER_RANGER])
        self.teams_page.select_ranger()
        self.ranger_info_page.go_upgrade_page()
        if type == 0: # poor upgrade
            self.ranger_filter_page.reset()
        self.ranger_upgrade_page.upgrade_ranger()
        self.ranger_upgrade_page.leave_menu()
        self.teams_page.leave_menu()

    def upgrade_gears(self):
        self.ranger_filter_page.filter(filter_list=[TeamsImg.FILTER_SIX_STARS, TeamsImg.FILTER_RANGER])
        self.teams_page.select_ranger()
        self.ranger_info_page.go_gear_page()
        self.gear_page.run()
        self.ranger_info_page.leave_menu()
        self.teams_page.leave_menu()    

def upgrade_ranger(context: GameContext, type: int = 1):
    teams = TeamsBase(context)
    teams.enter_menu()
    teams.upgrade_ranger(type=type)

def gear_enhance(context: GameContext):
    teams = TeamsBase(context)
    teams.enter_menu()
    teams.upgrade_gears()

def on_team_event(context: GameContext):
    teams = TeamsBase(context)
    teams.on_team_event()

def on_upgrade_event(context: GameContext):   
    teams = TeamsBase(context)
    teams.on_upgrade_event()