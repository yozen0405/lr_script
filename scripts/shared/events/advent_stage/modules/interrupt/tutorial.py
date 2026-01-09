from scripts.shared.events.advent_stage.enum import AdventImg, AdventStageName
from scripts.shared.controller.context import GameContext
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Battle, MainView, Leonard

class TutorialInterrupt:
    def __init__(self, context: GameContext):
        self.ctx = context

    def handle(self):
        if not wait_click(self.ctx.serial, Leonard.TP_POINT.value):
            return False
        wait_click(self.ctx.serial, Battle.ENTER.value)
        wait_click(self.ctx.serial, AdventImg.VERY_HARD.value, wait_time=1.0)
        wait_click(self.ctx.serial, AdventImg.VERY_HARD.value)
        connection_retry(self.ctx.serial, appear=Leonard.TP_POINT2.value, timeout=40.0)
        wait_click(self.ctx.serial, Leonard.TP_POINT2.value)
        wait_click(self.ctx.serial, Leonard.TP_POINT2.value)
        wait_click(self.ctx.serial, MainView.BACK.value)
        connection_retry(self.ctx.serial, appear=AdventImg.SCHEDULE.value, timeout=40.0)
        return True