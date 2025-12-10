from enum import Enum, auto

class LoginState(Enum):
    GAME_NOT_STARTED = auto()
    LOGIN_METHOD_PAGE = auto()
    TERMS_AGREEMENT_PAGE = auto()
    LINE_APP_PAGE = auto()
    LOADING_PAGE = auto()
    IN_GAME = auto()
    RETRY = auto()
    POPUP = auto()
    UNKNOWN = auto()
    