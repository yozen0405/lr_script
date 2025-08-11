import time
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, get_pos, drag
from core.base.exceptions import GameError
from scripts.shared.constants.positions import positions
from scripts.shared.constants import Settlement, Confirm, Battle, Retry, MainView
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.special_stage.enum import SpecialStage
from scripts.shared.utils.retry import connection_retry
from typing import Optional, Tuple

class BaseSpecialStage:
    def __init__(self, serial):
        self.serial = serial
        self.MEMBER3_POS = positions["member3"]
        self.MEMBER4_POS = positions["member4"]

    def enter_menu(self):
        if exist(self.serial, SpecialStage.TEXT):
            return
        
        for _ in range(5):
            if wait_click(self.serial, SpecialStage.BTN):
                connection_retry(self.serial, image_name=SpecialStage.BTN, exception_msg="不在主畫面", timeout=40.0)
                self._on_pre_anime()
                return
            elif exist(self.serial, MainStage.BTN):
                drag(self.serial, (800, 400), (200, 400))

        raise GameError("無法進入特殊關卡")

    def find_target_planet(self, planet: Optional[str] = None, crop_region: Optional[Tuple[int, int, int, int]] = None) -> None:
        if planet is None or planet == "":
            raise GameError("custom stage 型別錯誤")

        for _ in range(5):
            drag(self.serial, (100, 523), (800, 523), wait_time=0.3)

        region: Tuple[int, int, int, int] = (280, 90, 800, 470)

        for _ in range(7):
            pos = get_pos(self.serial, planet)
            if pos:
                x, y = pos
                drag(self.serial, (x, y), (640, y), wait_time=1.5)
                pos = get_pos(self.serial, planet)
                x, y = pos
                if crop_region:
                    (offsets_x1, offsets_y1, offsets_x2, offsets_y2) = crop_region
                    region = (x - offsets_x1, y - offsets_y1, x + offsets_x2, y + offsets_y2)
                break

            drag(self.serial, (400, 523), (100, 523), wait_time=1.0)
        return region

    def enter_stage(
        self,
        stage_num: int,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> None:
        if not wait(self.serial, SpecialStage.TEXT, timeout=30.0):
            raise GameError("不在特殊")
        
        if wait_click(self.serial, SpecialStage.STAGE(stage=stage_num), region=region, timeout=7.0, threshold=0.96):
            connection_retry(self.serial, wait_name=SpecialStage.TEXT, exception_msg="進不去特殊關卡的關卡", timeout=40.0)
            wait_click(self.serial, SpecialStage.ENTER, timeout=25.0)
            while True:
                if exist(self.serial, Retry.TEXT1):
                    exist_click(self.serial, Retry.BTN)
                elif not exist(self.serial, SpecialStage.ENTER):
                    return True
                elif exist(self.serial, SpecialStage.LIMITED):
                    exist_click(self.serial, Confirm.SMALL, wait_time=2.0)
                    wait_click(self.serial, MainView.BACK)
                    connection_retry(self.serial, wait_name=SpecialStage.LAB, exception_msg="回不去特殊關卡主畫面", timeout=40.0)
                    return False
        else:
            return False
            
    def single_mode_run(self):
        log_msg(self.serial, "Special Stage 進場")

        wait_click(self.serial, Battle.NEXT)
        wait_click(self.serial, Battle.START)
        connection_retry(self.serial, image_name=Battle.START, timeout=60.0)

        if wait(self.serial, Battle.PAUSE, timeout=15.0, threshold=0.9):
            self._on_start_page()
            while exist(self.serial, Battle.PAUSE, threshold=0.97):
                wait_click(self.serial, self.MEMBER3_POS)
                wait_click(self.serial, self.MEMBER4_POS)
        else:
            raise GameError("無法確認戰鬥狀態，跳出")

        log_msg(self.serial, "結算中")
        self.settlement()

        wait_click(self.serial, MainView.BACK, timeout=20.0)
        connection_retry(self.serial, wait_name=SpecialStage.LAB, exception_msg="回不去特殊關卡主畫面", timeout=40.0)
        
        log_msg(self.serial, "Special Stage 任務完成")

    def loop_mode_run(self):
        log_msg(self.serial, "Special Stage 迴圈進場")

        exist_click(self.serial, Battle.AUTO_BTN_OFF2, threshold=0.99)

        wait_click(self.serial, Battle.CYCLE)
        if wait(self.serial, Confirm.SMALL):
            exist_click(self.serial, Battle.MAX_OFF, threshold=0.9)
            wait_click(self.serial, Confirm.SMALL)

        wait_click(self.serial, Battle.NEXT)
        wait_click(self.serial, Battle.START)
        connection_retry(self.serial, image_name=Battle.START, timeout=60.0)

        if wait(self.serial, Battle.PAUSE, timeout=15.0, threshold=0.9):
            while True:
                if exist(self.serial, Battle.LOOP_END_TEXT, threshold=0.9):
                    break

                if exist(self.serial, Retry.TEXT1):
                    exist_click(self.serial, Retry.BTN, wait_time=2.5)
        else:
            raise GameError("無法確認戰鬥狀態，跳出")

        log_msg(self.serial, "結算中")
        wait_click(self.serial, Confirm.BIG2)

        connection_retry(self.serial, wait_name=SpecialStage.TEXT, exception_msg="無法回去特殊關卡準備畫面", timeout=40.0)
        wait_click(self.serial, "back.png", timeout=20.0)
        connection_retry(self.serial, wait_name=SpecialStage.LAB, exception_msg="回不去特殊關卡主畫面", timeout=40.0)

        log_msg(self.serial, "Special Stage 迴圈任務完成")

    def _on_start_page(self):
        if not wait_click(self.serial, SpecialStage.CIRCLE, timeout=3.0, wait_time=1.5):
            return
        wait_click(self.serial, SpecialStage.CIRCLE, wait_time=1.5)

    def _on_pre_anime(self):
        for _ in range(7):
            if exist(self.serial, SpecialStage.TEXT):
                break
            if not wait_click(self.serial, Battle.ANIME, wait_time=2.0, threshold=0.6):
                break

    def settlement(self):
        """
        子類別可 override 此函式以實作不同帳號的結算畫面。
        預設版本包含常見的點擊流程。
        """
        if wait_click(self.serial, Settlement.CANCEL_LOSE, wait_time=10.0):
            wait_click(self.serial, Settlement.CLOSE_LOSE_TIPS, wait_time=7.0)
            if not wait_click(self.serial, Confirm.SMALL, wait_time=7.0):
                raise GameError("沒有進入失敗葉面")
            raise GameError("輸了")

        connection_retry(self.serial, wait_name=Settlement.TEXT, retry_text=Retry.TEXT2, timeout=40.0)
        for _ in range(3):
            wait_click(self.serial, self.MEMBER4_POS)

        while True:
            for img in [Confirm.BIG1, Confirm.BIG2, Settlement.ONE_REWARD, Confirm.SMALL, Settlement.STOP, Settlement.SILVER_BOX, Settlement.BRONZE_BOX]:
                exist_click(self.serial, img, wait_time=1.5)
            if exist(self.serial, Retry.TEXT1):
                exist_click(self.serial, Retry.BTN)
            if exist(self.serial, SpecialStage.TEXT):
                break
