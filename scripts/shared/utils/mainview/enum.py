from enum import Enum, auto

class MainViewState(Enum):
    NO_AVATAR = auto()
    RETRY = auto()
    DIMMED = auto()
    CLEAR = auto()
    UNKNOWN = auto()

class MainViewEventType(Enum):
    TEAM = auto()
    GACHA = auto()
    MAIN_STAGE = auto()
    
