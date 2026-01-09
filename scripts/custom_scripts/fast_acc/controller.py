from core.actions.system import force_close, clear_game_storage
from scripts.shared.events.login.sec import guest_login
from scripts.shared.controller.context import GameContext
from core.base.exceptions import GameError
from core.actions.system import log_msg
from core.system.logging.reporter import RunStatus, AccountRunReporter

class FastAccController:
    def __init__(self, ctx: GameContext, reporter: AccountRunReporter):
        self.ctx = ctx
        self.reporter = reporter

    def start(self):
        guest_login(self.ctx)

    def restart(self):
        force_close(self.ctx.serial)
        self.start()

    def close(self):
        force_close(self.ctx.serial)

    def reset_storage(self):
        force_close(self.ctx.serial)
        clear_game_storage(self.ctx.serial)