import time
from core.actions.vision import exist_click, wait_click, exist, get_pos, check_region_brightness
from core.actions.system import log_msg
from core.base.exceptions import GameError
from scripts.shared.utils.retry import connection_retry
from scripts.shared.controller.context import GameContext
from scripts.shared.events.gacha.navigator import GachaNavigator
from scripts.shared.events.gacha.config import GachaSession, PoolConfig
from scripts.shared.events.gacha.enum import GachaImg, GachaPullState
from scripts.shared.constants import MainView, Confirm, Retry
from scripts.shared.events.gacha.modules.services import GachaOperations

class PullExecutor:
    def __init__(self, context: GameContext, operations: GachaOperations, session: GachaSession):
        self.ctx = context
        self.ops = operations
        self.session = session
        self.no_button_count = 0
        self.pulled = False

        self.navigator = GachaNavigator(context, session)

    def pull_one_round(self, config: PoolConfig) -> bool:
        start_time = time.time()
        succ = False
        self.no_button_count = 0
        self.pulled = False

        while time.time() - start_time < 120.0:
            if self._handle_retry():
                continue

            if exist(self.ctx.serial, GachaImg.TEXT.value, threshold=0.8):
                if succ:
                    return True
                
                if self._attempt_pull_action(config):
                    self.no_button_count = 0
                else:
                    self.no_button_count += 1
                    if self.no_button_count >= 2:
                        log_msg(self.ctx.serial, "無可用扭蛋資源，停止抽取")
                        return False
                    continue
                
                state = self._handle_pop_up()
                if state == GachaPullState.PULLED:
                    self.no_button_count = 0
                    continue
                elif state == GachaPullState.NO_DIAMOND:
                    return False
                    
            if self._handle_success_screen(config):
                succ = True

            if exist_click(self.ctx.serial, GachaImg.SKIP.value):
                self.no_button_count = 0
                continue
                    
        if exist(self.ctx.serial, GachaImg.SHOP_TEXT.value, threshold=0.9):
            wait_click(self.ctx.serial, MainView.BACK.value)
        else:
            raise GameError("抽取扭蛋操作超時")
        
        return False

    def _handle_retry(self) -> bool:
        if exist(self.ctx.serial, Retry.TEXT1.value) or exist(self.ctx.serial, Retry.TEXT2.value):
            connection_retry(self.ctx.serial, retry=Retry.BTN.value)
            return True
        return False

    def _handle_success_screen(self, config: PoolConfig) -> bool:
        if exist(self.ctx.serial, GachaImg.SUCCESS_TEXT.value, threshold=0.9):
            if not self.pulled:
                self.ops.check_ranger_in_pool(config)
                self.pulled = True
            wait_click(self.ctx.serial, GachaImg.CONFIRM.value)
            return True
        return False

    def _handle_pop_up(self) -> GachaPullState:
        if exist(self.ctx.serial, GachaImg.READY_PULL_TEXT.value, threshold=0.9):
            wait_click(self.ctx.serial, Confirm.SMALL.value, timeout=3.0)
            return GachaPullState.PULLED
        
        elif exist(self.ctx.serial, GachaImg.NO_DIAMOND_TEXT.value, threshold=0.9):
            wait_click(self.ctx.serial, Confirm.CANCEL_SMALL.value, timeout=3.0)
            return GachaPullState.NO_DIAMOND
            
        return GachaPullState.UNKNOWN 

    def _attempt_pull_action(self, config: PoolConfig) -> bool:
        if exist_click(self.ctx.serial, GachaImg.TICKET_PULL.value, wait_time=1.0):
            return True

        if config.tickets_only:
            return False

        if exist_click(self.ctx.serial, GachaImg.DIAMOND_PULL.value, wait_time=1.0):
            return True
        
        if self.navigator.on_interrupt(): # prevent unexpected interrupt
            return True

        return False