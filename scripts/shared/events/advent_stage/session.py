from dataclasses import dataclass

@dataclass
class AdventStageSession:
    on_event: bool = False
    lose: bool = False
    repeat: int = 1
    team_num: int = 2