from enum import Enum

class LoginState(Enum):
    GAME_NOT_STARTED = 1
    ON_LOGIN_METHOD_PAGE = 2
    ON_TERMS_AGREEMENT_PAGE = 3
    ON_LINE_APP = 4
    ON_LOADING_PAGE = 5
    IN_GAME = 6

    def next(self):
        if self == LoginState.GAME_NOT_STARTED:
            return LoginState.ON_LOGIN_METHOD_PAGE
        elif self == LoginState.ON_LOGIN_METHOD_PAGE:
            return LoginState.ON_TERMS_AGREEMENT_PAGE
        elif self == LoginState.ON_TERMS_AGREEMENT_PAGE:
            return LoginState.ON_LINE_APP
        elif self == LoginState.ON_LINE_APP:
            return LoginState.ON_LOADING_PAGE
        elif self == LoginState.ON_LOADING_PAGE:
            return LoginState.IN_GAME
        else:
            return None
    
    
    