from .base import EmulatorController
from .mumu import MuMuController
from functools import lru_cache

@lru_cache(maxsize=1)
def get_emulator_controller() -> EmulatorController:
    return MuMuController()