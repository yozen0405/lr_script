from scripts.shared.events.main_stage import BaseMainStage
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.ocr import get_main_stage_num

def normal_stage(serial):
    # main_stage = BaseMainStage(serial)

    # main_stage._find_stage()
    get_main_stage_num(serial)