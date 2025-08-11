from enum import Enum

class MainStage(str, Enum):
    TEXT = "main_stage_text.png"
    BTN = "main_stage_btn.png"
    NEXT_FEATURE = "main_stage_settlement_next_feature_text.png"
    PRE_START_TEXT = "main_stage_pre_start_text.png"
    METEOR = "meteor.png"
    JAMES_FRIEND = "james_friend_icon.png"
    
class Stages(str, Enum):
    LOCKED = "new_stage_locked.png"
    NEW_COMMON = "new_stage_common.png"
    NEW_EVENT = "new_stage_evt.png"
    NEW_SHINE = "new_stage.png"
    BOSS = "boss_stage.png"

class Treasure(str, Enum):
    ICON = "treasure_icon.png"
    ICON2 = "treasure_icon2.png"