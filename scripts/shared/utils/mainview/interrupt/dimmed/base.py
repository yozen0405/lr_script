import time
import os
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, back, drag, find_spotlight_center
from core.base.exceptions import GameError
from scripts.shared.constants import MainView, Confirm, Retry
import time
from core.actions.vision import wait_click, exist_click, exist, wait, get_pos, check_region_brightness
from core.base.exceptions import GameError
from scripts.shared.constants.view import GameView
from scripts.shared.events.season_pass.enum import SeasonPassImg
from scripts.shared.constants import MainView
from typing import List
from scripts.shared.controller.context import GameContext
from scripts.shared.utils.mainview.enum import MainViewState

class DimmedStrategy():
    def __init__(self, ctx: GameContext):
        self.ctx = ctx

    def on_no_avatar(self) -> bool:
        if exist(self.ctx.serial, MainView.BOARD_DONT_SHOW.value, threshold=0.9):
            return True
        
        if exist(self.ctx.serial, MainView.CLOSE_BOARD.value, threshold=0.9):
            return True
        
        if exist(self.ctx.serial, MainView.BUFF_EVENT.value, threshold=0.9):
            return True
        
        if exist(self.ctx.serial, MainView.SPECIAL_OFFERS.value, threshold=0.99):
            return True
        
        if exist(self.ctx.serial, MainView.COMEBACK.value, threshold=0.99):
            return True
        
        return False
    
    def handle_skip(self) -> bool:
        if exist_click(self.ctx.serial, MainView.SKIP.value, threshold=0.85):
            if wait(self.ctx.serial, MainView.SKIP_CONFIRM_TEXT.value, threshold=0.9, timeout=2.0):
                wait_click(self.ctx.serial, Confirm.SMALL.value, timeout=3.0)
            return True
        
        if exist_click(self.ctx.serial, MainView.SKIP_2.value, threshold=0.9):
            return True
        
        return False
    
    def handle_board(self) -> MainViewState:
        if exist(self.ctx.serial, GameView.AUTH_FAILED.value, threshold=0.9):
            raise GameError("偵測到主介面授權失敗狀態。")
        
        if exist(self.ctx.serial, MainView.TO_DOWNLOAD_TEXT.value, threshold=0.9) or \
            exist(self.ctx.serial, MainView.TO_LOADING_PAGE_TEXT.value, threshold=0.9):
            return MainViewState.TO_DOWNLOAD
        
        if exist(self.ctx.serial, GameView.ERROR_TEXT.value, threshold=0.9):
            raise GameError("偵測到主介面錯誤狀態。")
        
        return MainViewState.UNKNOWN

    def handle_supported(self) -> bool:
        start_time = time.time()

        is_me = False
        cnt = 0
        while time.time() - start_time < 400.0:
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.9) or \
               exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.ctx.serial, Retry.BTN.value)
                continue

            if exist(self.ctx.serial, MainView.BOARD_DONT_SHOW.value, threshold=0.9):
                wait_click(self.ctx.serial, MainView.BOARD_DONT_SHOW.value)
                wait_click(self.ctx.serial, MainView.CLOSE_BOARD.value)
                is_me = True
                cnt = 0
                continue

            if exist(self.ctx.serial, MainView.CLOSE_BOARD.value, threshold=0.9):
                wait_click(self.ctx.serial, MainView.CLOSE_BOARD.value)
                is_me = True
                cnt = 0
                continue
            
            if exist(self.ctx.serial, MainView.COMEBACK.value, threshold=0.99) or \
                exist(self.ctx.serial, MainView.SPECIAL_OFFERS.value, threshold=0.99) or \
                exist(self.ctx.serial, MainView.BUFF_EVENT.value, threshold=0.9) or \
                exist(self.ctx.serial, MainView.POLICY_TEXT.value, threshold=0.99):
                wait_click(self.ctx.serial, MainView.CLOSE_BOARD.value)
                is_me = True
                cnt = 0
                continue
            
            if exist_click(self.ctx.serial, MainView.SKIP.value, threshold=0.85):
                if wait(self.ctx.serial, MainView.SKIP_CONFIRM_TEXT.value, threshold=0.9, timeout=3.0):
                    wait_click(self.ctx.serial, Confirm.SMALL.value)
                is_me = True
                cnt = 0
                continue
            
            if exist_click(self.ctx.serial, MainView.SKIP_2.value, threshold=0.9):
                is_me = True
                cnt = 0
                continue

            if exist(self.ctx.serial, SeasonPassImg.POP_DETAIL_TEXT.value, threshold=0.99):
                wait_click(self.ctx.serial, Confirm.CANCEL_SMALL.value)
                is_me = True
                cnt = 0
                continue

            if exist(self.ctx.serial, MainView.CLOSE_PVP.value, threshold=0.9): # change to detect text for better accuracy
                wait_click(self.ctx.serial, MainView.CLOSE_PVP.value)
                is_me = True
                cnt = 0
                continue

            cnt += 1
            if cnt >= 2:
                return is_me
        raise GameError("DimmedStrategy handling timeout.")
    