import time
import os
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from core.base.exceptions import GameError
from scripts.shared.constants import Retry

def connection_retry(
    serial,
    image_name=None,
    wait_name=None,
    retry=Retry.BTN,
    retry_text=Retry.TEXT1,
    exception_msg="等待畫面失敗",
    timeout=15.0,
    wait_time=0.0
):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if image_name and not exist(serial, image_name):
            time.sleep(wait_time)
            return True
        if wait_name and exist(serial, wait_name):
            time.sleep(wait_time)
            return True
        if wait(serial, retry_text, timeout=1.5):
            wait_click(serial, retry, wait_time=4.0)
        time.sleep(0.5)

    raise GameError(exception_msg)