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
from scripts.shared.events.main_stage.session import StageSession
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.events.main_stage.modules.treasure.base import TreasureBase
from scripts.shared.events.main_stage.modules.navigator.base import StageNavigator
from scripts.shared.events.main_stage.modules.finder.base import StageFinder
from scripts.shared.events.main_stage.modules.battle.base import BattleBase
from scripts.shared.events.main_stage.modules.settlement.base import StageSettlement
from scripts.shared.events.main_stage.modules.preperation.base import PreparationBase

class MainStageTask:
    def __init__(self, context: GameContext, session: StageSession):
        self.ctx = context
        self.session = session

        self.navigator = StageNavigator(self.ctx, self.session)
        self.finder = StageFinder(self.ctx, self.session)  
        self.battle = BattleBase(self.ctx, self.session)
        self.settlement = StageSettlement(self.ctx, self.session)
        self.preperation = PreparationBase(self.ctx, self.session)

    def on_page(self) -> bool:
        return self.navigator.on_page()

    def check_if_need_leave(self):
        if self.session.is_first:
            self.ctx.current_stage_num = self.session.stage_num - 1

        self.session.on_interrupt = self.preperation.on_interrupt()
        if self.session.on_interrupt:
            return False

        if self.ctx.max_main_stage_num is not None:
            if self.session.stage_num > self.ctx.max_main_stage_num:
                log_msg(self.ctx.serial, f"[MainStageTask] 當前關卡 {self.session.stage_num} 超過設定的最大關卡 {self.ctx.max_main_stage_num}，停止挑戰。")
                return True
            
        return False
    
    def execute(self):
        self.preperation.run()
        self.battle.run()
        self.settlement.run()
    
    def run(self):
        self.navigator.enter_menu()

        start_time = time.time()
        while time.time() - start_time < 600.0:
            if self.navigator.handle_menu_page():
                return
            
            self.finder.find_stage()
            self.preperation.enter_stage()

            if self.check_if_need_leave():
                self.navigator.leave_menu()
                return
            
            apply_mode(self.ctx.serial, mode_name="main_stage", state="on")
            self.execute()
            apply_mode(self.ctx.serial, mode_name="main_stage", state="off")

def on_main_stage_page(context: GameContext) -> bool:
    main_stage_task = MainStageTask(context, session=StageSession())
    return main_stage_task.on_page()

def on_main_stage_event(context: GameContext):
    session = StageSession(
        is_first=True,
        on_event=True
    )
    main_stage_task = MainStageTask(context, session)
    main_stage_task.run()

def main_stage_finish_new(context: GameContext):
    session = StageSession(
        is_first=True,
    )
    main_stage_task = MainStageTask(context, session)
    main_stage_task.run()

def main_stage_finish_custom(context: GameContext, custom_stage: int, multiplier: int = 1, max_loop: int = 1):
    session = StageSession(
        custom_stage=custom_stage,
        multiplier=multiplier,
        team_num=2,
        max_loop=max_loop,
    )
    main_stage_task = MainStageTask(context, session)
    main_stage_task.run()