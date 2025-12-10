from enum import Enum
from dataclasses import dataclass
from typing import Any

@dataclass
class GameContext:
    serial: str
    max_main_stage_num: int = None
    current_stage_num: int = None