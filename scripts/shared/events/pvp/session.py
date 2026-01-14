from dataclasses import dataclass

@dataclass
class StageSession:
    on_event: bool = False
    loop: int = 0
    max_loop: int = 1
    lose: bool = False
    end: bool = False