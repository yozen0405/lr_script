from abc import ABC, abstractmethod
import logging
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.system import force_close
from scripts.shared.constants import Settlement, Confirm, Battle, Leonard, Retry, MainView, Positions
from scripts.shared.utils.retry import connection_retry
from scripts.shared.events.pvp.base import pvp_loop_battle
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.events.special_stage.selector import special_stage_single_game, special_stage_loop_game, special_stage_conquer_planet
from scripts.shared.events.special_stage.enum import Planet
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.special_stage.enum import SpecialStage
from scripts.shared.events.pvp.enum import PvP
from scripts.shared.events.guild.enum import Guild
from scripts.shared.events.advent_stage.enum import Advent
from scripts.shared.events.advent_stage.enum import AdventStageName
from scripts.shared.events.lab.enum import MakeMenu
from scripts.shared.events.dice.enum import DiceImg
from scripts.shared.events.teams.enum import Teams
from scripts.shared.events.guild.base import guild_raid_battle
from scripts.shared.events.main_stage.selector import main_stage_finish_custom
from scripts.shared.events.advent_stage.base import advent_stage_battle
from scripts.shared.events.bingo.base import bingo_attempt
from scripts.shared.events.login.sec import line_login
from scripts.shared.utils.mainview.base import on_main_view
from scripts.shared.events.lab.base import complete_lab_quest
from scripts.shared.events.season_pass.base import claim_season_pass
from scripts.shared.events.wheel.base import wheel_attempt
from scripts.shared.events.train.base import train_stage_battle
from scripts.shared.events.dice.base import dice_attempt
from scripts.shared.events.teams.base import upgrade_ranger
from core.actions.system import log_msg
import time

class BaseJob(ABC):
    def __init__(self, name, mode_name=None):
        """
        :param name: 任務名稱 (用於 log)
        :param mode_name: 對應 apply_mode 的名稱，如果不需要切換 mode 則為 None
        """
        self.name = name
        self.mode_name = mode_name

    def pre_execute(self, serial):
        log_msg(serial, f"[*] 準備執行任務: {self.name}")
        if self.mode_name:
            apply_mode(serial, mode_name=self.mode_name, state="on")

    @abstractmethod
    def run(self, serial):
        """子類別必須實作的具體邏輯"""
        pass

    def post_execute(self, serial):
        if self.mode_name:
            apply_mode(serial, mode_name=self.mode_name, state="off")
        
        log_msg(serial, f"[*] 任務完成: {self.name}")

class JobRunner:
    def __init__(self, serial):
        self.serial = serial
        self.jobs: list[BaseJob] = []
        self.max_retries = 1

    def restart_game(self):
        log_msg(self.serial, "[System] 正在執行遊戲重啟流程...")
        force_close(self.serial)
        line_login(self.serial, mode="")
        on_main_view(self.serial)

    def add_job(self, job: BaseJob):
        self.jobs.append(job)

    def execute_all(self):
        log_msg(self.serial, f"開始執行工作佇列，共有 {len(self.jobs)} 個任務")
        
        for job in self.jobs:
            retry_count = 0
            
            while True:
                task_status = "pending"
                
                try:
                    job.pre_execute(self.serial)
                    job.run(self.serial)
                    
                    task_status = "success"
                    break
                    
                except Exception as e:
                    log_msg(self.serial, f"[!] 任務 {job.name} 發生錯誤: {e}")
                    
                    if retry_count < self.max_retries:
                        retry_count += 1
                        log_msg(self.serial, f"[*] 準備重試任務 ({retry_count}/{self.max_retries})...")
                        
                        self.restart_game()
                        
                        task_status = "retrying"
                        continue 
                    else:
                        log_msg(self.serial, f"[X] 任務 {job.name} 重試次數已達上限。")
                        task_status = "failed"
                        raise e

                finally:
                    if task_status == "success":
                        try:
                            job.post_execute(self.serial)
                        except:
                            pass
                        
                        wait_click(self.serial, "back.png")
                        on_main_view(self.serial, timeout=30.0)