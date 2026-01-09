import time
from core.actions.system import force_close
from core.actions.vision import VisionManager 
from scripts.shared.events.main_stage.custom_stages.enum import Stage1Img
from scripts.shared.events.main_stage.enum import MainStageImg, MainStageSettlementImg
from scripts.shared.constants import GameView, Settlement, Confirm, Battle, MainView, Retry, Leonard
from scripts.shared.events.gacha.enum import GachaImg, GachaPool
from core.actions.vision import wait_click, exist, wait, exist_click, get_all_pos, save_screenshot
from core.env.base import initialize_environment
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.events.login.sec import line_login
from scripts.shared.controller.context import GameContext
from scripts.shared.events.main_stage.base import main_stage_finish_custom
from core.system.adb import connect_all_mumu_instances
from scripts.shared.controller.lifecycle.manager import ensure_main_view
from scripts.shared.events.advent_stage.modules.finder.base import StageFinder
from scripts.shared.events.advent_stage.enum import AdventImg
from core.actions.vision import OCRMode

def test_speed():
    devices = connect_all_mumu_instances(goal=1)
    serial = devices[0]

    # cls = StageFinder(GameContext(serial=serial))
    # cls.enter_stage()

    # serial = "127.0.0.1:16576"
    # print(get_main_stage_num(serial))
    # wait(serial, Leonard.TP_STICK.value)
    # print(get_main_stage_num(serial, region=(779, 108, 802, 126)))
    # print(get_text(serial, region=(443, 207, 519, 248), mode=OCRMode.NUMERICAL))

    initialize_environment(serial)
    # line_login(GameContext(serial=serial))
    # apply_mode(serial, "advent", "on")
    # apply_mode(serial, "pvp", "off")
    # context = GameContext(serial=serial)
    # ensure_main_view(context)
    
    # main_stage_finish_custom(context, custom_stage=323)

if __name__ == "__main__":
    test_speed()