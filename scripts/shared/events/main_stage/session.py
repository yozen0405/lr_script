from dataclasses import dataclass

from scripts.shared.events.main_stage.custom_stages.base import MainStageCustomHookBase

@dataclass
class StageSession:
    stage_num: int = None
    custom_stage: int = None
    stage_cls: MainStageCustomHookBase = None

    is_first: bool = False
    is_low: bool = True
    on_interrupt: bool = False
    on_event: bool = False
    team_num: int = 1
    multiplier: int = 1
    has_auto: bool = False
    loop: int = 0
    max_loop: int = 1
    lose: bool = False