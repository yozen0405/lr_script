from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from typing import List, Optional

@dataclass
class GameContext:
    serial: str
    is_guest: bool = False

    # --- 關卡與任務進度 ---
    max_main_stage_num: int = 1
    current_stage_num: Optional[int] = None
    complete_special_stage: bool = False
    
    # --- 跑號進度 Flag ---
    complete_stage_1: bool = False
    seven_days_done: bool = False
    gift_box_done: bool = False
    gacha_done: bool = False
    done: bool = False
    
    # --- 統計與結果 (供 Reporter 紀錄) ---
    pulled_rangers: List[str] = field(default_factory=list)
    retry_count: int = 0
    last_error_msg: str = ""
    start_time: datetime = field(default_factory=datetime.now)