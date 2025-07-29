import time
from logger import log_msg
from action import wait_click, exist_click, exist, wait, wait_vanish
from exceptions import GameError
from location.pair import positions
from common.alert import connection_retry

class MainStageTask:
    def __init__(self, serial):
        self.serial = serial
        self.MEMBER3_POS = positions["member3"]
        self.MEMBER4_POS = positions["member4"]
        self.FRIEND = positions["friend"]

    def enter_menu(self):
        if wait(self.serial, "main_stage_btn.png", timeout=20.0, wait_time=1.0):
            wait_click(self.serial, "main_stage_btn.png")
            connection_retry(self.serial, wait_name="main_stage_text.png", timeout=60.0)
        else:
            raise GameError("不在主畫面")

    def enter_stage(self, custom_stage: str = ""):
        if not wait(self.serial, "main_stage_text.png", timeout=30.0, wait_time=2.5):
            raise GameError("不在主要關卡")
        if custom_stage == "":
            if not wait_click(self.serial, "new_stage_common.png", threshold=0.98, timeout=3.0):
                if not wait_click(self.serial, "new_stage_evt.png", threshold=0.97, timeout=3.0):
                    if not wait_click(self.serial, "boss_stage.png", threshold=0.89, timeout=3.0):
                        if not wait_click(self.serial, "new_stage.png", timeout=3.0):
                            raise GameError("無法找到關卡")
        else:
            if not wait_click(self.serial, custom_stage, timeout=10.0):
                raise GameError("無法找到關卡")

    def run(self, anime=True, has_next=True, big_ok=False, bonus=True):
        log_msg(self.serial, "Main Stage 戰鬥開始")

        wait_vanish(self.serial, "main_stage_text.png", timeout=20.0)
        if anime:
            time.sleep(2.0)
            for _ in range(3):
                if not wait_click(self.serial, "stage_anime.png", wait_time=1.0, threshold=0.6):
                    break

        if has_next:
            wait_click(self.serial, "next.png")
            self.select_friend()

        self.pre_select()
        
        wait_click(self.serial, "start.png")
        connection_retry(self.serial, image_name="start.png", timeout=60.0)

        if wait(self.serial, "pause.png", timeout=15.0, threshold=0.9):
            self.teach()
            while exist(self.serial, "pause.png", threshold=0.97):
                wait_click(self.serial, self.MEMBER3_POS)
                wait_click(self.serial, self.MEMBER4_POS)
        else:
            raise GameError("無法確認戰鬥狀態，跳出")

        log_msg(self.serial, "結算中")
        self.settlement()
        if bonus:
            if big_ok:
                wait_click(self.serial, "confirm_big2.png", wait_time=7.0)
            else:
                wait_click(self.serial, "confirm_small.png", wait_time=7.0)
            if not exist(self.serial, "main_stage_text.png"):
                wait_click(self.serial, "confirm_big2.png", wait_time=4.0)
        log_msg(self.serial, "Main Stage 任務完成")

    def teach(self):
        pass

    def select_friend(self):
        pass

    def pre_select(self):
        pass

    def settlement(self):
        """
        子類別可 override 此函式以實作不同帳號的結算畫面。
        預設版本包含常見的點擊流程。
        """
        if wait_click(self.serial, "cancel_lose.png", wait_time=10.0):
            wait_click(self.serial, "close_lose_tips.png", wait_time=7.0)
            if not wait_click(self.serial, "confirm_small.png", wait_time=7.0):
                raise GameError("沒有進入失敗葉面")
            raise GameError("輸了")

        wait(self.serial, "main_stage_settlement_text.png", timeout=25.0)
        for _ in range(3):
            wait_click(self.serial, self.MEMBER4_POS)
        for _ in range(10):
            for img in ["acquired.png", "confirm_big.png", "oneReward.png"]:
                exist_click(self.serial, img)
            if exist_click(self.serial, "stop.png"):
                break
            if exist(self.serial, "main_stage_text.png"):
                break
        
