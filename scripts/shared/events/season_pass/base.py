from scripts.shared.events.season_pass.enum import SeasonPassImg, SeasonPassState
from scripts.shared.constants import Confirm, MainView, Retry
from core.actions.vision import wait_click, exist_click, exist, wait
from scripts.shared.utils.retry import connection_retry
from scripts.shared.controller.context import GameContext
import time

class SeasonPassBase:
    def __init__(self, ctx: GameContext):
        self.ctx = ctx
        self.current_state = SeasonPassState.NOT_ENTERED

    def _detect_state(self) -> SeasonPassState:
        if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.9):
            return SeasonPassState.RETRY

        if exist(self.ctx.serial, SeasonPassImg.ICON.value, threshold=0.9):
            return SeasonPassState.NOT_ENTERED
        
        if exist(self.ctx.serial, SeasonPassImg.POP_TEXT.value, threshold=0.9):
            return SeasonPassState.POP_TEXT
        
        if exist(self.ctx.serial, SeasonPassImg.CLAIMED_TEXT.value, threshold=0.9):
            return SeasonPassState.CLAIM_POP
        
        if exist(self.ctx.serial, SeasonPassImg.EXP_UP_TEXT.value, threshold=0.9):
            return SeasonPassState.EXP_UP
        
        if not exist(self.ctx.serial, SeasonPassImg.TEXT.value, threshold=0.9):        
            return SeasonPassState.UNKNOWN
        
        if exist(self.ctx.serial, SeasonPassImg.EXP_UP_TEXT.value, threshold=0.9):
            return SeasonPassState.EXP_UP
        
        if exist(self.ctx.serial, SeasonPassImg.ON_DAILY_NAV.value, threshold=0.99):
            if not exist(self.ctx.serial, SeasonPassImg.CLAIM.value):
                return SeasonPassState.DAILY_DONE
            return SeasonPassState.DAILY
        elif exist(self.ctx.serial, SeasonPassImg.ON_WEEKLY_NAV.value, threshold=0.99):
            if not exist(self.ctx.serial, SeasonPassImg.CLAIM.value):
                return SeasonPassState.WEEKLY_DONE
            return SeasonPassState.WEEKLY
        elif exist(self.ctx.serial, SeasonPassImg.ON_PASS_NAV.value, threshold=0.99):
            if not exist(self.ctx.serial, SeasonPassImg.TICKETS.value, threshold=0.99):
                return SeasonPassState.PASS_DONE
            return SeasonPassState.PASS
        elif exist(self.ctx.serial, SeasonPassImg.HISTORY_TEXT.value, threshold=0.9):
            return SeasonPassState.HISTORY
        else:
            return SeasonPassState.ANIME
            
        
    def run(self):
        start_time = time.time()
        while time.time() - start_time < 300:
            self.current_state = self._detect_state()

            if self.current_state == SeasonPassState.NOT_ENTERED:
                self.handle_enter_menu()
            elif self.current_state == SeasonPassState.RETRY:
                self.handle_retry()
            elif self.current_state == SeasonPassState.ANIME:
                self.handle_anime()
            elif self.current_state == SeasonPassState.HISTORY:
                self.handle_history()
            elif self.current_state == SeasonPassState.EXP_UP:
                self.handle_exp_up()
            elif self.current_state == SeasonPassState.DAILY_DONE:
                self.handle_daily_done()
            elif self.current_state == SeasonPassState.CLAIM_POP:
                self.handle_claim_pop()
            elif self.current_state == SeasonPassState.POP_TEXT:
                self.handle_pop_text()
            elif self.current_state == SeasonPassState.DAILY:
                self.handle_daily_nav()
            elif self.current_state == SeasonPassState.WEEKLY_DONE:
                self.handle_weekly_done()
            elif self.current_state == SeasonPassState.WEEKLY:
                self.handle_weekly_nav()
            elif self.current_state == SeasonPassState.PASS:
                self.handle_pass_nav()

            if self.is_on_exit() == self.current_state:
                break

    def is_on_exit(self) -> SeasonPassState:
        return SeasonPassState.PASS_DONE

    def handle_enter_menu(self):
        if wait(self.ctx.serial, SeasonPassImg.ICON.value, timeout=20.0, wait_time=1.0):
            wait_click(self.ctx.serial, SeasonPassImg.ICON.value, timeout=7.0)

    def handle_retry(self):
        wait_click(self.ctx.serial, Retry.BTN.value)

    def handle_anime(self):
        for _ in range(13):
            wait_click(self.ctx.serial, SeasonPassImg.TEXT.value, wait_time=1.0)

    def handle_history(self):
        wait_click(self.ctx.serial, MainView.CLOSE_BOARD.value, threshold=0.9)

    def handle_exp_up(self):
        wait_click(self.ctx.serial, Confirm.BIG2.value)

    def handle_claim_pop(self):
        wait_click(self.ctx.serial, Confirm.SMALL.value)

    def handle_daily_done(self):
        wait_click(self.ctx.serial, SeasonPassImg.WEELKY_NAV.value)

    def handle_daily_nav(self):
        wait_click(self.ctx.serial, SeasonPassImg.CLAIM.value)

    def handle_weekly_done(self):
        wait_click(self.ctx.serial, SeasonPassImg.PASS_NAV.value)

    def handle_weekly_nav(self):
        wait_click(self.ctx.serial, SeasonPassImg.CLAIM.value)

    def handle_pop_text(self):
        wait_click(self.ctx.serial, Confirm.SMALL.value)

    def handle_pass_nav(self):
        wait_click(self.ctx.serial, SeasonPassImg.PASS_NAV.value)
        if exist(self.ctx.serial, SeasonPassImg.CONGRATS.value, threshold=0.9):
            wait_click(self.ctx.serial, Confirm.BIG2.value)

class SeasonPassStandard(SeasonPassBase):
    def is_on_exit(self) -> SeasonPassState:
        return SeasonPassState.WEEKLY_DONE
    
class SeasonPassNewAcc(SeasonPassBase):
    def is_on_exit(self) -> SeasonPassState:
        return SeasonPassState.PASS_DONE

def claim_season_pass(ctx: GameContext):
    cls = SeasonPassStandard(ctx)
    cls.run()