from enum import Enum

class MainViewState(Enum):
    TUTORIALS = 1
    SKIP = 2
    PVP_OPENED = 3
    SPECIAL_OFFERS = 4
    POLICY = 5
    BUFF_EVENT = 6
    COMEBACK = 7
    DONT_SHOW_AGAIN = 8
    BOARD_END = 9
    SEASON_PASS = 10
    SPECIAL_STAGE = 11
    RETRY = 12
    CLEAR = 13 # No popups
    UNKNOWN = 14