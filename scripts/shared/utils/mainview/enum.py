from enum import Enum, auto

class MainViewState(Enum):
    GAME_NOT_STARTED = "game_not_started"
    SPECIAL_STAGE = "special_stage"
    MAIN_STAGE = "main_stage"
    GACHA = "gacha"
    TEAM = "team"
    UPGRADE = "upgrade"
    SEVEN_DAYS = "seven_days"
    SPECIAL_QUEST = "special_quest"
    TO_DOWNLOAD = "to_download"
    PRE_STAGE = "pre_stage"
    NONE = "none"
    PENDING = "pending"
    UNKNOWN = "unknown"
    AUTH_FAILED = "auth_failed"
    ERROR = "error"
