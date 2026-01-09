from abc import ABC, abstractmethod
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.system import force_close
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.events.login.sec import line_login, guest_login
from scripts.shared.utils.mainview.base import on_main_view
from scripts.shared.controller.lifecycle.manager import ensure_main_view
from core.actions.system import log_msg
from scripts.shared.controller.context import GameContext
import time

class BaseJob(ABC):
    def __init__(self, name, mode_name=None):
        """
        :param name: 任務名稱 (用於 log)
        :param mode_name: 對應 apply_mode 的名稱，如果不需要切換 mode 則為 None
        """
        self.name = name
        self.mode_name = mode_name

    def pre_execute(self, ctx: GameContext):
        log_msg(ctx.serial, f"[*] 準備執行任務: {self.name}")
        if self.mode_name:
            apply_mode(ctx.serial, mode_name=self.mode_name, state="on")

    @abstractmethod
    def run(self, ctx: GameContext):
        """子類別必須實作的具體邏輯"""
        pass

    def post_execute(self, ctx: GameContext):
        if self.mode_name:
            apply_mode(ctx.serial, mode_name=self.mode_name, state="off")
        
        log_msg(ctx.serial, f"[*] 任務完成: {self.name}")

class JobRunner:
    def __init__(self, serial):
        self.serial = serial
        self.ctx = GameContext(serial)
        self.jobs: list[BaseJob] = []
        self.max_retries = 0

    def start_game(self):
        log_msg(self.serial, "[System] 正在啟動遊戲...")
        ensure_main_view(self.ctx)

    def restart_game(self):
        log_msg(self.serial, "[System] 正在執行遊戲重啟流程...")
        force_close(self.serial)
        ensure_main_view(self.ctx)

    def add_job(self, job: BaseJob):
        self.jobs.append(job)

    def execute_all(self):
        log_msg(self.serial, f"開始執行工作佇列，共有 {len(self.jobs)} 個任務")
        
        for job in self.jobs:
            retry_count = 0
            
            while True:
                task_status = "pending"
                
                try:
                    job.pre_execute(self.ctx)
                    job.run(self.ctx)
                    
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
                            job.post_execute(self.ctx)
                        except:
                            pass
                        
                        if job.name != "Main Stage Farming":
                            wait_click(self.serial, "back.png")
                        ensure_main_view(self.ctx, timeout=30.0)