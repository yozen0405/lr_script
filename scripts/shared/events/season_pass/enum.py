from enum import Enum, auto

class SeasonPassImg(Enum):
    ICON = "season_pass_icon.png"
    TEXT = "season_pass_text.png"
    ON_DAILY_NAV = "season_pass_on_daily_nav.png"
    DAILY_NAV = "daily_quest_nav.png"
    CLAIM = "daily_quest_claim.png"
    WEELKY_NAV = "weekly_quest_nav.png"
    ON_WEEKLY_NAV = "season_pass_on_weekly_nav.png"
    PASS_NAV = "season_pass_nav.png"
    ON_PASS_NAV = "season_pass_on_pass_nav.png"
    CLAIMED_TEXT = "season_pass_claim_text.png"
    HISTORY_TEXT = "season_pass_history_text.png"
    CONGRATS = "season_pass_congrats_text.png"
    POP_TEXT = "season_pass_pop_text.png"
    POP_DETAIL_TEXT = "season_pass_pop_detail_text.png"
    EXP_UP_TEXT = "season_pass_exp_up_text.png"
    LVL1 = "season_pass_level1_text.png"
    TICKETS = "season_pass_tickets.png"

class SeasonPassState(Enum):
    NOT_ENTERED = auto()
    ANIME = auto()
    DAILY = auto()
    DAILY_DONE = auto()
    WEEKLY = auto()
    WEEKLY_DONE = auto()
    PASS = auto()
    PASS_DONE = auto()
    RETRY = auto()
    HISTORY = auto()
    EXP_UP = auto()
    CLAIM_POP = auto()
    POP_TEXT = auto()
    UNKNOWN = auto()