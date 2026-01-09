from typing import Type, Dict
from .base import MainStageCustomHookBase
from .strategies import FirstStage, ThirdStage, AutoStage, FriendStage

class StageHookResolver:
    _MAPPING: Dict[int, Type[MainStageCustomHookBase]] = {
        1: FirstStage,
        3: ThirdStage,
        13: AutoStage,
        30: FriendStage,
    }

    @classmethod
    def get_hook(cls, stage_num: int, context) -> MainStageCustomHookBase:
        hook_class = cls._MAPPING.get(stage_num, MainStageCustomHookBase)
        return hook_class(context)
    