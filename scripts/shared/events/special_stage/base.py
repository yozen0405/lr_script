import time
from core.system.logger import log_msg
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, get_pos, drag
from core.base.exceptions import GameError
from scripts.shared.constants import positions
from scripts.shared.utils.retry import connection_retry
from typing import Optional, Tuple

class BaseSpecialStage:
    def __init__(self, serial):
        self.serial = serial
        self.MEMBER3_POS = positions["member3"]
        self.MEMBER4_POS = positions["member4"]

    def enter_menu(self):
        if exist(self.serial, "special_stage_text.png"):
            return
        
        for _ in range(5):
            if wait_click(self.serial, "special_stage_btn.png"):
                connection_retry(self.serial, image_name="special_stage_btn.png", exception_msg="不在主畫面", timeout=40.0)
                return
            elif exist(self.serial, "main_stage_btn.png"):
                drag(self.serial, (200, 400), (800, 400))
        raise GameError("無法進入特殊關卡")

    def _find_target_planet(
        self,
        stage_num: int,
        planet: Optional[str] = None,
        crop_region: Optional[Tuple[int, int, int, int]] = None,
    ) -> None:
        region = crop_region or (280, 90, 800, 470)
        if planet is None or planet == "":
            raise GameError("custom stage 型別錯誤")

        for _ in range(4):
            pos = get_pos(self.serial, planet, region=region)
            if pos:
                x, y = pos
                drag(self.serial, (x, y), (640, y), wait_time=1.5)
                break

            drag(self.serial, (400, 523), (100, 523), wait_time=1.0)

        if not wait_click(self.serial, f"special_stage{stage_num}.png", region=region, timeout=10.0):
            raise GameError(f"找不到指定特殊關卡")
        connection_retry(self.serial, wait_name="special_stage_text.png", exception_msg="進不去特殊關卡的關卡", timeout=40.0)

    def enter_stage(
        self,
        stage_num: int,
        planet: Optional[str] = None,
        crop_region: Optional[Tuple[int, int, int, int]] = None,
    ) -> None:
        self._on_pre_anime()

        if not wait(self.serial, "special_stage_text.png", timeout=30.0):
            raise GameError("不在特殊")
        
        self._find_target_planet(planet=planet, stage_num=stage_num, crop_region=crop_region)
            
    def single_mode_run(self):
        log_msg(self.serial, "Special Stage 進場")

        wait_click(self.serial, "enter_special_stage.png", timeout=25.0)
        wait_click(self.serial, "next.png")
        wait_click(self.serial, "start.png")
        connection_retry(self.serial, image_name="start.png", timeout=60.0)

        if wait(self.serial, "pause.png", timeout=15.0, threshold=0.9):
            self._on_start_page()
            while exist(self.serial, "pause.png", threshold=0.97):
                wait_click(self.serial, self.MEMBER3_POS)
                wait_click(self.serial, self.MEMBER4_POS)
        else:
            raise GameError("無法確認戰鬥狀態，跳出")

        log_msg(self.serial, "結算中")
        self.settlement()
        wait_click(self.serial, "back.png", timeout=20.0)
        connection_retry(self.serial, wait_name="special_stage_text.png", exception_msg="無法回去特殊關卡選單", timeout=40.0)
        
        log_msg(self.serial, "Special Stage 任務完成")

    def loop_mode_run(self):
        log_msg(self.serial, "Special Stage 迴圈進場")

        wait_click(self.serial, "enter_special_stage.png", timeout=25.0)

        wait_click(self.serial, "pre_start_again.png")
        wait_click(self.serial, "pre_start_max.png")
        wait_click(self.serial, "confirm_small.png")

        wait_click(self.serial, "next.png")
        wait_click(self.serial, "start.png")
        connection_retry(self.serial, image_name="start.png", timeout=60.0)

        if wait(self.serial, "pause.png", timeout=15.0, threshold=0.9):
            while True:
                if exist(self.serial, "loop_settlement_end_text.png", threshold=0.9):
                    break

                if exist(self.serial, "retry_text.png"):
                    exist_click(self.serial, "retry.png", wait_time=2.5)

                wait_click(self.serial, self.MEMBER3_POS)
                wait_click(self.serial, self.MEMBER4_POS)
        else:
            raise GameError("無法確認戰鬥狀態，跳出")

        log_msg(self.serial, "結算中")
        wait_click(self.serial, "confirm_big.png")

        wait_click(self.serial, "back.png", timeout=20.0)
        connection_retry(self.serial, wait_name="special_stage_text.png", exception_msg="無法回去特殊關卡選單", timeout=40.0)
        
        log_msg(self.serial, "Special Stage 迴圈任務完成")

    def _on_start_page(self):
        if not wait_click(self.serial, "leonard_teacher_circle_special_stage.png", wait_time=1.5):
            return
        wait_click(self.serial, "leonard_teacher_circle_special_stage.png", wait_time=1.5)

    def _on_pre_anime(self):
        for _ in range(7):
            if exist(self.serial, "special_stage_text.png"):
                break
            if not wait_click(self.serial, "stage_anime.png", wait_time=2.0, threshold=0.6):
                break

    def settlement(self):
        """
        子類別可 override 此函式以實作不同帳號的結算畫面。
        預設版本包含常見的點擊流程。
        """
        if wait_click(self.serial, "cancel_lose.png", wait_time=10.0):
            wait_click(self.serial, "close_lose_tips.png", wait_time=7.0)
            if not wait_click(self.serial, "smallOK.png", wait_time=7.0):
                raise GameError("沒有進入失敗葉面")
            raise GameError("輸了")

        connection_retry(self.serial, wait_name="main_stage_settlement_text.png", retry_text="retry_text2.png", timeout=40.0)
        for _ in range(3):
            wait_click(self.serial, self.MEMBER4_POS)

        while True:
            for img in ["acquired.png", "confirm_big.png", "confirm_big2.png", "oneReward.png", "confirm_small.png", "stop.png"]:
                exist_click(self.serial, img, wait_time=1.5)
            if exist(self.serial, "retry_text.png"):
                exist_click(self.serial, "retry.png")
            if exist(self.serial, "special_stage_text.png"):
                break
