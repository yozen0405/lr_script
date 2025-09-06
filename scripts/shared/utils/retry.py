import time
import os
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from core.base.exceptions import GameError
from scripts.shared.constants import Retry, Confirm

def _to_list(x):
    if x is None:
        return []
    if isinstance(x, str):
        return [x]
    if isinstance(x, (list, tuple)):
        if isinstance(x, tuple) and 1 <= len(x) <= 3 and (len(x) == 0 or not isinstance(x[0], (list, tuple))):
            return [x]
        return list(x)
    return [x]

def _norm(x):
    items = _to_list(x)
    out = []
    for it in items:
        if isinstance(it, (list, tuple)):
            if len(it) == 0:
                continue
            img = it[0]
            th = it[1] if len(it) >= 2 else 0.7
            tm = it[2] if len(it) >= 3 else 3.0
        else:
            img, th, tm = it, 0.7, 3.0
        out.append((img, th, tm))
    return out

def connection_retry(
    serial,
    vanish=None,
    appear=None,
    retry=None,
    timeout: float = 15.0,
):
    vanish = _norm(vanish)
    appear = _norm(appear)
    retry = _norm(retry)

    start_time = time.time()
    while time.time() - start_time < timeout:
        for img, th, _ in vanish:
            if not exist(serial, img, threshold=th):
                return
        for img, th, _ in appear:
            if exist(serial, img, threshold=th):
                return

        if exist(serial, Retry.TEXT1.value):
            if not exist_click(serial, Retry.BTN.value):
                exist_click(serial, Confirm.SMALL.value)

        if exist(serial, Retry.TEXT2.value):
            if not exist_click(serial, Retry.BTN.value):
                wait_click(serial, Confirm.SMALL.value, wait_time=1.0)
                for img, th, tm in retry:
                    wait_click(serial, img, threshold=th, timeout=tm)

        time.sleep(0.2)

    raise GameError("等待畫面失敗")
