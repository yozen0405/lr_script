import time
from scripts.shared.controller.context import GameContext
from scripts.shared.events.special_stage.session import SpecialStageSession
from scripts.shared.events.special_stage.modules.navigator.base import SpecialStageNavigator
from scripts.shared.events.special_stage.modules.finder.base import SpecialStageFinder
from scripts.shared.events.special_stage.modules.preperation.base import SpecialStagePreperation
from scripts.shared.events.special_stage.modules.battle.base import SpecialStageBattle
from scripts.shared.events.special_stage.modules.settlement.base import SpecialStageSettlement
from scripts.shared.utils.hacks import apply_mode
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg

class SpecialStageTask:
    def __init__(self, context: GameContext, session: SpecialStageSession):
        self.ctx = context
        self.session = session

        self.navigator = SpecialStageNavigator(self.ctx, self.session)
        self.finder = SpecialStageFinder(self.ctx, self.session)
        self.preperation = SpecialStagePreperation(self.ctx, self.session)
        self.battle = SpecialStageBattle(self.ctx, self.session)
        self.settlement = SpecialStageSettlement(self.ctx, self.session)

    def run(self):
        apply_mode(self.ctx.serial, mode_name="special_stage", state="on")
        self.navigator.enter_menu()

        try:
            if self.navigator.handle_menu_page():
                return
            
            self.finder.enter_stage()
            if self.session.stage_stop:
                return

            self.preperation.run()
            self.battle.run()
            self.settlement.run()
        finally:
            apply_mode(self.ctx.serial, mode_name="special_stage", state="off")
            self.navigator.leave_menu()

def special_stage_single_game(context: GameContext, planet: str, stage: int):
    session = SpecialStageSession(planet=planet, stage_num=stage, is_loop_mode=False)
    task = SpecialStageTask(context, session)
    task.run()

def special_stage_loop_game(context: GameContext, planet: str, stage: int):
    session = SpecialStageSession(planet=planet, stage_num=stage, is_loop_mode=True)
    task = SpecialStageTask(context, session)
    task.run()


def special_stage_conquer_planet(context: GameContext, planet: str):
    session = SpecialStageSession(planet=planet, is_conquer_mode=True, is_loop_mode=True)
    task = SpecialStageTask(context, session)
    task.run()

def on_special_stage_event(context: GameContext):
    session = SpecialStageSession(on_event=True)
    task = SpecialStageTask(context, session)
    task.run()