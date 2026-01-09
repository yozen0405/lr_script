import functools
import logging
from core.base.exceptions import RecoverableError, FatalError
from core.system.logging.logger import log_msg
from core.system.logging.reporter import RunStatus

from scripts.shared.controller.error.handler import RunErrorHandler

def handle_run_exceptions(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        serial = self.ctx.serial if self.ctx else self.serial
        context = getattr(self, 'ctx', None)
        reporter = getattr(self, 'reporter', None)

        try:
            return func(self, *args, **kwargs)
        
        except RecoverableError as e:
            handler = RunErrorHandler(context, reporter)
            return handler.handle(e)
        
        except FatalError as e:
            handler = RunErrorHandler(context, reporter)
            handler.handle(e)
            raise 

        except Exception as e:
            log_msg(serial, f"非預期系統異常: {e}", level=logging.ERROR)
            if context and reporter:
                reporter.record(context, status=RunStatus.ABORTED, error=e)
            raise

    return wrapper