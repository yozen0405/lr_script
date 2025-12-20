from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.system import force_close
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.events.login.sec import line_login, guest_login
from scripts.shared.utils.mainview.base import on_main_view
from scripts.shared.events.special_stage.selector import special_stage_single_game
from scripts.shared.events.mineral_upgrade.base import mineral_upgrade
from scripts.shared.events.main_stage.selector import main_stage_finish_new, main_stage_finish_custom
from scripts.shared.events.gacha.base import pull_ranger
from scripts.shared.events.pre_stage.base import pre_stage_finish
from scripts.shared.events.season_pass.sec import claim_tickets
from scripts.shared.events.teams.base import upgrade_ranger
from scripts.shared.events.settings.base import finalize_account
from scripts.shared.events.seven_days.base import seven_days_event, seven_days_claim
from scripts.shared.events.special_quest.base import special_quest_event
from scripts.shared.utils.mainview.enum import MainViewState
from core.actions.system import log_msg
from scripts.shared.controller.context import GameContext
from core.base.exceptions import GameError
from scripts.shared.events.special_stage.enum import Planet
from scripts.shared.utils.mainview.base import MainViewHandler
from scripts.shared.constants import Confirm, MainView
import time

class NewAccBase:
    def __init__(self, serial):
        self.ctx = GameContext(serial)
        self.mainview_handler = MainViewHandler(self.ctx)

        self.reset()

    def reset(self):
        self.complete_stage_30 = False
        self.ctx.current_stage_num = None
        self.ctx.complete_special_stage = False
        self.team_upgrade = False
        self.mineral_upgrade = False
        self.seven_days_done = False
        self.season_pass_done = False
        self.ctx.pulled_rangers = None
        self.ctx.max_main_stage_num = 30
        self.done = False
        self.error_count = 0

    def setup(self):
        # self.complete_stage_30 = False
        # self.ctx.current_stage_num = None
        # self.ctx.complete_special_stage = False
        # self.team_upgrade = False
        # self.mineral_upgrade = False
        # self.seven_days_done = False
        # self.season_pass_done = False
        pass

    def _start_game(self):
        force_close(self.ctx.serial)
        guest_login(self.ctx)

    def _to_download(self):
        wait_click(self.ctx.serial, Confirm.SMALL.value)
        connection_retry(self.ctx.serial, vanish=MainView.TO_DOWNLOAD_TEXT.value, timeout=40.0)
        guest_login(self.ctx)

    def _perform(self):
        if self.ctx.current_stage_num is None or self.ctx.current_stage_num < self.ctx.max_main_stage_num:
            main_stage_finish_new(self.ctx)
            return
        
        if not self.complete_stage_30 and self.ctx.current_stage_num == self.ctx.max_main_stage_num:
            main_stage_finish_custom(self.ctx, custom_stage=self.ctx.max_main_stage_num, leave_menu=True)
            self.complete_stage_30 = True
            return
        
        if not self.ctx.complete_special_stage:
            special_stage_single_game(self.ctx, planet=Planet.COLLAB.value, stage=1, leave_menu=True)
            self.ctx.complete_special_stage = True
            return
        
        if not self.team_upgrade:
            upgrade_ranger(self.ctx, type=0)
            self.team_upgrade = True
            return
        
        if not self.mineral_upgrade:
            mineral_upgrade(self.ctx)
            self.mineral_upgrade = True
            return
        
        if not self.seven_days_done:
            seven_days_claim(self.ctx)
            self.seven_days_done = True
            return
        
        if not self.season_pass_done:
            claim_tickets(self.ctx)
            self.season_pass_done = True

        if self.ctx.pulled_rangers is None:
            pull_ranger(self.ctx)
            return
        else:
            finalize_account(self.ctx)
            self.done = True

    def _task(self):
        self.reset()
        self.setup()

        while True:
            try:
                if self.done:
                    log_msg(self.ctx.serial, "New account completed.")
                    return
                event = self.mainview_handler.proccess()
                log_msg(self.ctx.serial, f"Detected main view event: {event.value}")

                if event == MainViewState.PRE_STAGE:
                    pre_stage_finish(self.ctx)
                    continue
                elif event == MainViewState.MAIN_STAGE:
                    self._perform()
                    continue
                elif event == MainViewState.TO_DOWNLOAD:
                    self._to_download()
                    continue
                elif event == MainViewState.NONE:
                    self._perform()
                    continue
                elif event == MainViewState.UNKNOWN:
                    self._start_game()
                    continue
            except GameError as e:
                log_msg(self.ctx.serial, f"Error occurred: {e}. Retrying...")
                self.error_count += 1
                if self.error_count >= 3:
                    raise GameError("Too many errors occurred. Aborting.")
                self._start_game()

    def run(self):
        self._start_game()
        self._task()

def normal_stage(serial):
    na = NewAccBase(serial)
    na.run()