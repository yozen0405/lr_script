from enum import Enum, auto

class NoAvatarState(Enum):
    BOARD_DONT_SHOW = auto()
    BOARD_END = auto()
    COMEBACK = auto()
    SPECIAL_OFFERS = auto()
    BUFF_EVENT = auto()
    UNKNOWN = auto()