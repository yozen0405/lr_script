from dataclasses import dataclass
from typing import Optional

@dataclass
class SpecialStageSession:
    planet: str
    stage_num: int
    team_num: int = 2
    on_event: bool = False
    
    is_loop_mode: bool = False
    conquer_mode: bool = False

    stage_stop: bool = False
    stage_complete: bool = False