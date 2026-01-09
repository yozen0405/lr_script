from core.base.exceptions import RecoverableError
from scripts.shared.controller.context import GameContext
from scripts.shared.controller.lifecycle.manager import ensure_main_view
from scripts.custom_scripts.fast_acc.controller import FastAccController
from scripts.custom_scripts.fast_acc.sequencer import FastAccSequencer
from core.system.logging.reporter import AccountRunReporter, RunStatus
from scripts.custom_scripts.fast_acc.decorators import handle_run_exceptions
from scripts.shared.utils.mainview.base import on_main_view
from core.actions.vision import (
    exist_click, wait_click, wait, wait_vanish,
    drag, back, exist, get_pos,
    check_region_brightness
)
from core.env.base import initialize_environment
from core.system.logging.logger import log_msg
from core.system.adb import adb_cmd
from core.system.emulator.exceptions import EmulatorRebootRequired
from core.system.adb import heartbeat

class FastAccBase:
    def __init__(self, serial):
        self.serial = serial

        self.reporter = AccountRunReporter(serial)
        self.ctx = GameContext(
            serial=self.serial,
        )
        self.controller = None
        self.sequencer = None

    def setup(self):
        self.ctx = GameContext(
            serial=self.serial,
            max_main_stage_num=1,
            pulled_rangers=[],
            is_guest=True,
        )
        # if self.serial.endswith(":16480"):
        #     self.ctx.complete_stage_1 = True
        #     self.ctx.current_stage_num = 1
        #     self.ctx.gift_box_done = True
        #     self.ctx.seven_days_done = True
        #     self.ctx.pulled_rangers = [
        #         "Carrot"
        #     ]
        
        self.controller = FastAccController(self.ctx, self.reporter)
        self.sequencer = FastAccSequencer(self.ctx, self.controller)

        self.controller.reset_storage()
        self.controller.close()
        heartbeat(self.serial)

    def _prepare_new_account(self):
        log_msg(self.serial, "=== 準備開始新帳號流程 ===")
        
        self.ctx = GameContext(
            serial=self.serial,
            max_main_stage_num=1,
            pulled_rangers=[],
            is_guest=True,
        )
        
        self.controller = FastAccController(self.ctx, self.reporter)
        self.sequencer = FastAccSequencer(self.ctx, self.controller)

        self.controller.reset_storage()
        heartbeat(self.serial)

    @handle_run_exceptions
    def _init_account_phase(self, is_first_run: bool):
        initialize_environment(self.serial)
        if is_first_run:
            self.setup()
        else:
            self._prepare_new_account() 
            
        return True

    @handle_run_exceptions
    def _run_step(self):
        if self.ctx.done:
            return True
        
        ensure_main_view(self.ctx)
        self.sequencer.push_progress()
        return False

    def run(self):
        for i in range(500):
            while not self._init_account_phase(is_first_run=(i == 0)):
                continue

            while not self.ctx.done:
                if self._run_step():
                    break
            
            self.reporter.record(ctx=self.ctx, status=RunStatus.SUCCESS)

def normal_stage(serial):
    try:
        fast_acc = FastAccBase(serial)
        fast_acc.run()
    except KeyboardInterrupt as e:
        pass