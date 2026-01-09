import time
from core.system.logging.logger import log_msg
from core.base.exceptions import GameError
from scripts.shared.controller.context import GameContext
from scripts.shared.events.advent_stage.session import AdventStageSession
from scripts.shared.utils.hacks import apply_mode

from scripts.shared.events.advent_stage.modules.navigator.base import StageNavigator
from scripts.shared.events.advent_stage.modules.finder.base import StageFinder
from scripts.shared.events.advent_stage.modules.battle.base import StageBattle
from scripts.shared.events.advent_stage.modules.settlement.base import StageSettlement
from scripts.shared.events.advent_stage.modules.preperation.base import PreparationBase

class AdventStageTask:
    def __init__(self, context: GameContext, session: AdventStageSession):
        self.ctx = context
        self.session = session

        self.navigator = StageNavigator(self.ctx, self.session)
        self.finder = StageFinder(self.ctx, self.session)
        self.battle = StageBattle(self.ctx, self.session)
        self.settlement = StageSettlement(self.ctx, self.session)
        self.preperation = PreparationBase(self.ctx, self.session)

    def execute(self):
        self.preperation.run()
        self.battle.run()
        self.settlement.run()
    
    def run(self):
        self.navigator.enter_menu()
        if self.navigator.handle_menu_page():
            return
        
        if self.finder.enter_stage():
            try:
                apply_mode(self.ctx.serial, mode_name="advent_stage", state="on")
                self.execute()
            except GameError as e:
                log_msg(self.ctx.serial, f"{e}")
            finally:
                apply_mode(self.ctx.serial, mode_name="advent_stage", state="off")

        self.navigator.leave_menu()

def run_advent_stage(context: GameContext):
    session = AdventStageSession()
    task = AdventStageTask(context, session)
    task.run()
