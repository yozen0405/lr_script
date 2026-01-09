from scripts.shared.controller.lifecycle.base import StateResolver
from scripts.shared.controller.context import GameContext
from scripts.shared.events.login.sec import line_login, guest_login
from scripts.shared.events.pre_stage.base import pre_stage_finish
from scripts.shared.constants import Confirm, MainView
from core.actions.vision import wait_click
from scripts.shared.utils.retry import connection_retry
from core.system.logging.logger import log_msg

class LoginResolver(StateResolver):
    def resolve(self, context: GameContext):
        log_msg(context.serial, "執行登入流程...")
        if context.is_guest:
            guest_login(context)
        else:
            line_login(context)

class PreStageResolver(StateResolver):
    def resolve(self, context: GameContext):
        log_msg(context.serial, "排除前置關卡干擾...")
        pre_stage_finish(context)

class DownloadResolver(StateResolver):
    def resolve(self, context: GameContext):
        log_msg(context.serial, "處理下載畫面...")
        wait_click(context.serial, Confirm.SMALL.value)
        connection_retry(context.serial, vanish=MainView.TO_DOWNLOAD_TEXT.value, timeout=40.0)
        LoginResolver().resolve(context)