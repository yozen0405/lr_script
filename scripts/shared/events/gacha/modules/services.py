import time
from typing import Optional, List
from core.actions.vision import exist_click, drag
from core.system.logging.logger import log_msg, log_event
from core.actions.vision import match_string_from_region
from core.base.exceptions import GameError
from scripts.shared.controller.context import GameContext
from scripts.shared.events.gacha.config import PoolConfig, RangerTarget

class GachaOperations:
    def __init__(self, context: GameContext):
        self.ctx = context
        self.OCR_REGIONS = [(472, 162, 713, 225), (472, 172, 713, 225)]

    def find_pool(self, pool_img: str):
        log_msg(self.ctx.serial, "正在搜尋扭蛋池...")
        for _ in range(7):
            if exist_click(self.ctx.serial, pool_img, wait_time=1.5):
                return
            drag(self.ctx.serial, (752, 350), (752, 250), duration=800, wait_time=1.5)
        
        raise GameError("無法找到指定扭蛋池，請檢查圖片或活動狀態")

    def check_ranger_in_pool(self, config: PoolConfig) -> bool:
        target = self._match_from_region(config)
        if target:
            log_msg(self.ctx.serial, f"抽到目標: {target.full_name}")
            self.ctx.pulled_rangers.append(target.short_name)
            return True
        return False

    def log_summary(self):
        if len(self.ctx.pulled_rangers) == 0:    
            log_msg(self.ctx.serial, "本次抽取未獲得任何目標 ranger")
            return
            
        # for i, name in enumerate(self.ctx.pulled_rangers, 1):
        #     log_msg(self.ctx.serial, f"抽到 {name}")
        log_event(self.ctx.serial, f"本次共抽到 {len(self.ctx.pulled_rangers)} 隻目標 ranger: {', '.join(self.ctx.pulled_rangers)}")

    def _match_from_region(self, config: PoolConfig) -> Optional[RangerTarget]:
        for target in config.targets:
            for reg in self.OCR_REGIONS:
                if match_string_from_region(self.ctx.serial, target.full_name, region=reg, threshold=0.95):
                    return target
        return None