from scripts.shared.controller.context import GameContext
from scripts.shared.controller.enum import TaskStatus
from scripts.shared.constants import Retry
from core.actions.screen import exist, wait_click
import time

class BaseModule():
    def __init__(self, context: GameContext):
        self.ctx = context

    def _handle_retry(self) -> bool:
        if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.9) or \
               exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.9):
            wait_click(self.ctx.serial, Retry.BTN.value, threshold=0.9) 
            return True
        return False

    def on_page(self) -> bool:
        pass

    def on_interrupt(self) -> bool:
        pass

    def handle_interrupts(self) -> bool:
        pass

    def fix(self):
        pass

    def perform_logic(self):
        raise NotImplementedError()

    def execute(self):
        pass