import os
import time
from configparser import ConfigParser
from core.system.config import Config
from core.system.logging.logger import log_msg
from core.actions.vision import (
    exist_click, wait_click, wait, wait_vanish,
    drag, back, exist, get_pos,
    check_region_brightness
)
from core.actions.system import pull_account_file
from core.actions.vision import match_string_from_region
from scripts.shared.events.gacha.modules.executor import PullExecutor
from scripts.shared.events.gacha.modules.services import GachaOperations
from scripts.shared.utils.retry import connection_retry
from core.base.exceptions import GameError
from scripts.shared.events.gacha.enum import GachaImg, GachaPool, GachaPullState
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.constants import MainView, Confirm, Leonard, Retry
from scripts.shared.controller.context import GameContext
from scripts.shared.events.gacha.config import GACHA_PLAYBOOK, GachaSession, RangerTarget, PoolConfig
from typing import Optional, List

class PullRangerModule:
    def __init__(self, context: GameContext, session: GachaSession):
        self.ctx = context
        self.session = session
        
        self.ops = GachaOperations(context)
        self.executor = PullExecutor(context, self.ops, session)

    def run(self):
        playbook: List[PoolConfig] = GACHA_PLAYBOOK
        
        try:
            for pool_config in playbook:
                self._execute_pool_strategy(pool_config)
        finally:
            self.ops.log_summary()

    def _execute_pool_strategy(self, config: PoolConfig):
        log_msg(self.ctx.serial, f"準備抽取卡池: {config.name}")
        
        self.ops.find_pool(config.pool_img)

        for i in range(config.attempts):
            log_msg(self.ctx.serial, f"第 {i+1}/{config.attempts} 次抽取")
            
            success = self.executor.pull_one_round(config)
            
            if not success:
                log_msg(self.ctx.serial, "停止抽取此卡池")
                break