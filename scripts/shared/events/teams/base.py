from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos, check_region_brightness
from core.actions.screen import back
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logger import log_msg
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.constants.leonard import Leonard
from scripts.shared.events.teams.pages.rangers.teams.base import TeamsPage
from scripts.shared.events.teams.pages.rangers.info.base import RangerInfoPage
from scripts.shared.events.teams.pages.rangers.upgrade.base import RangerUpgradePage
from scripts.shared.events.teams.pages.rangers.filters.base import RangerFilterPage
from scripts.shared.events.teams.pages.gears.base import GearBase
import time

class TeamsBase():
    def __init__(self, serial):
        self.serial = serial

        self.teams_page = TeamsPage(serial)
        self.ranger_info_page = RangerInfoPage(serial)
        self.ranger_upgrade_page = RangerUpgradePage(serial)
        self.ranger_filter_page = RangerFilterPage(serial)
        self.gear_page = GearBase(serial)

    def enter_menu(self):
        self.teams_page.enter_menu()

    def on_rene_event(self):
        if not exist_click(self.serial, TeamsImg.RENE_MAINVIEW.value, threshold=0.9):
            raise GameError("Not on Rene main view.")
        
        if exist(self.serial, TeamsImg.RENE_UPGRADE_TEXT.value, threshold=0.9):
            self.ranger_info_page._on_rene_event()
            self.ranger_upgrade_page.on_rene_upgrade()
        else:
            self.ranger_info_page._on_rene_event()
            self.gear_page.handle_event()
    
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
