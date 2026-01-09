
import time
from abc import ABC, abstractmethod
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, back, drag, check_freeze
from core.actions.system import force_close, force_close_line
from core.base.exceptions import GameError
from scripts.shared.utils.mainview.base import is_on_main_view
from scripts.shared.constants import GameView, MainView, Confirm, Retry
from scripts.shared.events.login.enum import LoginState
from scripts.shared.controller.context import GameContext

class BaseHandler(ABC):
    def __init__(self, context: GameContext):
        self.ctx = context

    @abstractmethod
    def on_page(self) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    def handle(self):
        raise NotImplementedError