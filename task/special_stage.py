import time
from logger import log_msg
from action import wait_click, exist_click, exist, wait, wait_vanish, get_pos, drag
from exceptions import GameError
from location.pair import positions
from common.alert import connection_retry

class SpecialStageTask:
    def __init__(self, serial):
        self.serial = serial
        self.MEMBER3_POS = positions["member3"]
        self.MEMBER4_POS = positions["member4"]

    def enter_menu(self):
        if wait(self.serial, "special_stage_btn.png", timeout=20.0, wait_time=1.0):
            wait_click(self.serial, "special_stage_btn.png")
        else:
            raise GameError("不在主畫面")

    def enter_stage(self, custom_stage: str = "", stage_num: int = 0, anime=False):
        if anime:
            self.pre_anime()
        if not wait(self.serial, "special_stage_text.png", timeout=30.0):
            raise GameError("不在特殊")
        if custom_stage:
            region = (350, 90, 840, 470)
            for i in range(4):
                if exist(self.serial, custom_stage):
                    (x, y) = get_pos(self.serial, custom_stage)
                    drag(self.serial, (x, y), (640, y), wait_time=1.5)
                    break
                drag(self.serial, (400, 523), (100, 523), wait_time=1.0)
                
            wait_click(self.serial, f"special_stage{stage_num}.png", region=region, timeout=10.0)

    def run(self, bonus=True):
        log_msg(self.serial, "Special Stage 進場")

        wait_click(self.serial, "enter_special_stage.png", timeout=25.0)
        wait_click(self.serial, "next.png")
        wait_click(self.serial, "start.png")

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
            wait_click(self.serial, "confirm_big2.png", wait_time=7.0)
            wait_click(self.serial, "confirm_big2.png", wait_time=4.0)
        log_msg(self.serial, "Special Stage 任務完成")

    def teach(self):
        pass

    def pre_anime(self):
        pass

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

        for _ in range(3):
            wait_click(self.serial, self.MEMBER4_POS)
        for _ in range(10):
            for img in ["acquired.png", "confirm_big.png", "oneReward.png"]:
                exist_click(self.serial, img)
            if exist_click(self.serial, "stop.png"):
                break
            if exist(self.serial, "special_stage_text.png"):
                break
        
