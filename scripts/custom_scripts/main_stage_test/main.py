from scripts.shared.events.main_stage.selector import MainStageTask
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.ocr import get_main_stage_num

def normal_stage(serial):
    main_stage = MainStageTask(serial)
    main_stage.battle()