from enum import Enum
from scripts.shared.constants.base import Base

class MainStage(Base):
    TEXT = "main_stage_text.png"
    BTN = "main_stage_btn.png"
    NEXT_FEATURE = "main_stage_settlement_next_feature_text.png"
    PRE_START_TEXT = "main_stage_pre_start_text.png"
    METEOR = "meteor.png"
    JAMES_FRIEND = "james_friend_icon.png"
    STAGE_SELECTOR = "main_stage_selector.png"
    STAGE_NAV_1 = "main_stage_nav1.png"
    STAGE_NAV_100 = "main_stage_nav100.png"
    STAGE_NAV_200 = "main_stage_nav200.png"
    STAGE_NAV_300 = "main_stage_nav300.png"
    STAGE_NAV_400 = "main_stage_nav400.png"
    MULTIPLIER_LOW_BTN = "main_stage_multiplier_low_{times}.png"
    MULTIPLIER_HIGH_BTN = "main_stage_multiplier_high_{times}.png"
    TEAM_BTN_LOW = "main_stage_team_btn_low.png"
    TEAM_BTN_HIGH = "main_stage_team_btn_high.png"
    TEAM_NUM_LOW_OFF = "main_stage_team_num_low_off_{num}.png"
    TEAM_NUM_LOW_ON = "main_stage_team_num_low_on_{num}.png"
    TEAM_NUM_HIGH_OFF = "main_stage_team_num_high_off_{num}.png"
    TEAM_NUM_HIGH_ON = "main_stage_team_num_high_on_{num}.png"
    AUTO_BTN_LOW_OFF = "main_stage_auto_btn_low_off.png"
    AUTO_BTN_HIGH_OFF = "main_stage_auto_btn_high_off.png"
    NORMAL_NAV = "main_stage_normal_nav.png"
    HARD_NAV = "main_stage_hard_nav.png"
    METEOR_TEXT = "main_stage_stage_1_meteor_text.png"
    
class Stages(str, Enum):
    LOCKED = "new_stage_locked.png"
    NEW_COMMON = "new_stage_common.png"
    NEW_EVENT = "new_stage_evt.png"
    NEW_SHINE = "new_stage.png"
    BOSS = "boss_stage.png"

class Treasure(str, Enum):
    ICON = "treasure_icon.png"
    ICON2 = "treasure_icon2.png"
    TEXT = "treasure_text.png"