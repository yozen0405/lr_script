from core.actions.vision import exist
from scripts.shared.constants import MainView
from scripts.shared.events.main_stage.base import main_stage_finish_new, main_stage_finish_custom
from scripts.shared.events.seven_days.base import seven_days_claim
from scripts.shared.events.gift_box.base import claim_gift_box
from scripts.shared.events.gacha.base import pull_ranger
from scripts.shared.events.settings.base import finalize_account
from core.actions.system import log_msg
from scripts.shared.controller.context import GameContext
from scripts.custom_scripts.fast_acc.controller import FastAccController

class FastAccSequencer:
    def __init__(self, ctx: GameContext, controller: FastAccController):
        self.ctx = ctx
        self.controller = controller

    def push_progress(self):
        if self.ctx.current_stage_num is None:
            if exist(self.ctx.serial, MainView.LEVEL_3_TEXT.value, threshold=0.95):
                self.ctx.current_stage_num = 1
                self.ctx.complete_stage_1 = True
            else:
                main_stage_finish_new(self.ctx)
            return

        if not self.ctx.complete_stage_1:
            log_msg(self.ctx.serial, "要去完成第一章關卡")
            main_stage_finish_custom(self.ctx, custom_stage=1)
            self.ctx.complete_stage_1 = True
            self.controller.restart()
            return

        tasks = [
            (lambda: self.ctx.seven_days_done, self._do_seven_days),
            (lambda: self.ctx.gift_box_done,   self._do_gift_box),
            (lambda: self.ctx.gacha_done,      self._do_gacha),
        ]

        for is_done_check, task_func in tasks:
            if not is_done_check():
                task_func()
                return

        finalize_account(self.ctx)
        self.ctx.done = True

    def _do_seven_days(self):
        seven_days_claim(self.ctx)
        self.ctx.seven_days_done = True

    def _do_gift_box(self):
        claim_gift_box(self.ctx)
        self.ctx.gift_box_done = True

    def _do_gacha(self):
        pull_ranger(self.ctx)
        self.ctx.gacha_done = True