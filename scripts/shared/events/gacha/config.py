from dataclasses import dataclass
from typing import List, Dict

from scripts.shared.events.gacha.enum import GachaImg, GachaPool

@dataclass
class GachaSession:
    on_event: bool = False
    
@dataclass
class RangerTarget:
    full_name: str
    short_name: str

@dataclass
class PoolConfig:
    name: str     
    pool_img: str         
    targets: List[RangerTarget]
    attempts: int = 5
    tickets_only: bool = False
    
BROWN_TARGETS = [
    RangerTarget("Radish Brown", "Carrot"),
    RangerTarget("New Soldier Brown", "Elephant"),
]

GACHA_PLAYBOOK = [
    PoolConfig(
        name="雄大池",
        pool_img=GachaPool.BROWN.value,
        targets=BROWN_TARGETS,
        attempts=6,
        tickets_only=False
    )
]