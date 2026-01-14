import time
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.vision import get_main_stage_num
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.events.main_stage.custom_stages.base import MainStageCustomHookBase
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.main_stage.enum import MainStageImg, Stages, Treasure
from scripts.shared.controller.context import GameContext
from scripts.shared.events.pvp.session import StageSession
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.events.pvp.enum import PvPImg
from scripts.shared.events.pvp.modules.settlement.base import StageSettlement
from scripts.shared.events.pvp.modules.preperation.base import StagePreperation
from scripts.shared.events.pvp.modules.finder.base import StageFinder
from scripts.shared.events.pvp.modules.battle.base import StageBattle
from scripts.shared.events.pvp.modules.navigator.base import StageNavigator

class PvPTask:
    def __init__(self, context: GameContext, session: StageSession):
        self.ctx = context
        self.session = session

        self.navigator = StageNavigator(self.ctx, self.session)
        self.finder = StageFinder(self.ctx, self.session)  
        self.battle = StageBattle(self.ctx, self.session)
        self.settlement = StageSettlement(self.ctx, self.session)
        self.preperation = StagePreperation(self.ctx, self.session)

    def on_page(self) -> bool:
        return self.navigator.on_page()
    
    def run(self):
        self.navigator.enter_menu()
        apply_mode(self.ctx.serial, mode_name="pvp", state="on")

        start_time = time.time()
        while time.time() - start_time < 600.0:
            if self.navigator.handle_menu_page():
                apply_mode(self.ctx.serial, mode_name="pvp", state="off")
                return
            
            self.finder.enter_stage()
            self.preperation.run()
            if self.session.end:
                continue
            self.battle.run()
            self.settlement.run()
        raise GameError("PvP 主程式執行逾時")
            
def pvp_loop_battle(context: GameContext):
    pvp = PvPTask(context, StageSession(max_loop=5))
    pvp.run()