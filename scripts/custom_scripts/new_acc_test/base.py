from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.system import force_close
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.events.login.sec import line_login, guest_login
from scripts.shared.utils.mainview.base import on_main_view
from scripts.shared.events.special_stage.selector import special_stage_single_game
from scripts.shared.events.main_stage.selector import main_stage_finish_new, main_stage_finish_custom
from scripts.shared.events.pre_stage.base import pre_stage_finish
from scripts.shared.events.teams.base import on_team_event, on_upgrade_event
from scripts.shared.events.seven_days.base import seven_days_event, seven_days_claim
from scripts.shared.events.special_quest.base import special_quest_event
from scripts.shared.utils.mainview.enum import MainViewState
from core.actions.system import log_msg
from scripts.shared.controller.context import GameContext
from scripts.shared.events.special_stage.enum import Planet
from scripts.shared.utils.mainview.base import MainViewHandler
from scripts.shared.constants import Confirm, MainView
import time

class NewAccBase:
    def __init__(self, serial):
        self.ctx = GameContext(serial)

        self.mainview_handler = MainViewHandler(self.ctx)
        self.ctx.max_main_stage_num = 30

    def _perform(self):
        if self.ctx.current_stage_num is None:
            main_stage_finish_new(self.ctx)
            return
        
        if self.ctx.current_stage_num < 30:
            main_stage_finish_new(self.ctx)
            return
        
        if self.ctx.current_stage_num == 30:
            main_stage_finish_custom(self.ctx, custom_stage=30)
            return
        
    def _to_download(self):
        wait_click(self.ctx.serial, Confirm.SMALL.value)
        connection_retry(self.ctx.serial, vanish=MainView.TO_DOWNLOAD_TEXT.value, timeout=40)
        guest_login(self.ctx.serial)

    def _task(self):
        while True:
            event = self.mainview_handler.proccess(timeout=60.0)

            if event == MainViewState.PRE_STAGE:
                pre_stage_finish(self.ctx)
                continue
            elif event == MainViewState.MAIN_STAGE:
                self._perform()
                continue
            elif event == MainViewState.SPECIAL_STAGE:
                special_stage_single_game(self.ctx.serial, planet=Planet.EVO_MINE.value, stage=1)
                continue
            elif event == MainViewState.TEAM:
                on_team_event(self.ctx)
                continue
            elif event == MainViewState.UPGRADE:
                on_upgrade_event(self.ctx)
                continue
            elif event == MainViewState.SEVEN_DAYS:
                seven_days_event(self.ctx)
                continue
            elif event == MainViewState.SPECIAL_QUEST:
                special_quest_event(self.ctx)
                continue
            elif event == MainViewState.TO_DOWNLOAD:
                self._to_download()
                continue
            elif event == MainViewState.NONE:
                self._perform()
                continue
            elif event == MainViewState.UNKNOWN:
                force_close(self.ctx.serial)
                guest_login(self.ctx.serial)
                continue