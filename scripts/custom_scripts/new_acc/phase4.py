import time
import os
from core.system.logger import log_msg
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, extract_text, back, drag, force_close
from core.base.exceptions import GameError
from scripts.shared.utils.game_view import close_board
from scripts.shared.events.main_stage import MainStageTask
from scripts.shared.events.special_stage import SpecialStageTask
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_boot import open_game_with_hacks
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.login import login_entry

class AutoStageTask(MainStageTask):
    def teach(self):
        time.sleep(1.0)
        if not wait_click(self.serial, "auto_btn_on.png", wait_time=3.0):
            raise GameError("無法點擊 auto")
        if not wait_click(self.serial, "auto_btn_off.png"):
            raise GameError("無法點擊 auto")
        if not wait_click(self.serial, "auto_btn_off.png"):
            raise GameError("無法點擊 auto")

class EvoMineTask(SpecialStageTask):
    def pre_anime(self):
        for _ in range(7):
            if exist(self.serial, "special_stage_text.png"):
                break
            if not wait_click(self.serial, "stage_anime.png", wait_time=2.0, threshold=0.6):
                break

    def teach(self):
        wait_click(self.serial, "leonard_teacher_circle_special_stage.png", wait_time=1.5)
        wait_click(self.serial, "leonard_teacher_circle_special_stage.png", wait_time=1.5)

def normal_stage(serial, main_stage_task, anime=False, has_next=False, bonus=True, enter_menu=False):
    if enter_menu:
        main_stage_task.enter_menu()
    main_stage_task.enter_stage()
    main_stage_task.run(anime=anime, has_next=has_next, big_ok=True, bonus=bonus)

def upgrade_equip(serial):
    log_msg(serial, "升級裝備")
    on_main_view(serial)

    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)

    wait_click(serial, "rene.png", timeout=7.0, wait_time=2.0)
    wait_click(serial, "rene_go_equip.png", timeout=10.0)

    if not wait(serial, "equip_text.png", timeout=20.0):
        raise GameError("沒進去裝備頁面")

    wait_click(serial, "skip.png", timeout=5.0, wait_time=1.2)
    wait_click(serial, "equip_shield_icon.png", timeout=5.0, wait_time=1.2)
    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)
    wait_click(serial, "equip_go_upgrade.png", timeout=5.0, wait_time=2.0, threshold=0.99)
    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)
    wait_click(serial, "equip_shield_icon.png", timeout=5.0, wait_time=2.0)
    wait_click(serial, "equip_upgrade.png", timeout=5.0, wait_time=3.0)
    for _ in range(3):
        if not wait_click(serial, "equip_upgrade_finish.png", timeout=5.0, wait_time=1.5):
            break
    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)
    wait_click(serial, "back.png")


def auto_stage(serial):
    log_msg(serial, "auto stage 開始")
    auto_stage_task = AutoStageTask(serial)
    auto_stage_task.enter_menu()
    auto_stage_task.enter_stage()
    auto_stage_task.run(anime=True, has_next=False, big_ok=True)

def introduce_scene(serial):
    wait_click(serial, "back.png")
    on_main_view(serial, sign="gacha_skip.png", timeout=40.0)

    wait_click(serial, "gacha_skip.png", timeout=5.0, wait_time=2.0)
    evo = EvoMineTask(serial)
    evo.enter_menu()
    evo.enter_stage(anime=True, custom_stage="evo_mine.png", stage_num=1)
    evo.run(bonus=False)

    wait_click(serial, "back.png", timeout=20.0)
    if not wait(serial, "evo_mine.png", timeout=15.0):
        raise GameError("無法回去特殊關卡選單")
    wait_click(serial, "back.png", wait_time=2.0)
    

def phase4(serial):
    main_stage_task = MainStageTask(serial)
    log_msg(serial, "第四階段")

    try:
        auto_stage(serial)
    except GameError as e:
        raise

    try:
        normal_stage(serial, main_stage_task, enter_menu=False)
    except GameError as e:
        raise

    try:
        normal_stage(serial, main_stage_task, enter_menu=False)
    except GameError as e:
        raise

    try:
        upgrade_equip(serial)
    except GameError as e:
        raise

    try:
        normal_stage(serial, main_stage_task, enter_menu=True)
    except GameError as e:
        raise

    for _ in range(8):
        try:
            normal_stage(serial, main_stage_task, enter_menu=False)
        except GameError as e:
            raise

    try:
        normal_stage(serial, main_stage_task, anime=True, enter_menu=False)
    except GameError as e:
        raise

    try:
        introduce_scene(serial)
    except GameError as e:
        raise