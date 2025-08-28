from enum import Enum

class PreStage(Enum):
    NICKNAME = "nickname_setup.png"
    TEXT = "pre_stage_text.png"

class Phase1UI(Enum):
    LVL1_TEXT = "phase1_lvl1_text.png"
    LVL2_TEXT = "phase1_lvl2_text.png"
    
class Phase2UI(Enum):
    SHEEP = "sheep.png"
    SHEEP_UPGRADE_TEXT = "sheep_upgrade_text.png"

class Phase3UI(Enum):
    RENE = "rene.png"
    EQUIP_SHIRT = "equip_shirt.png"

class Phase4UI(Enum):
    SHIELD = "equip_shield_icon.png"

class Phase5UI(Enum):
    STAGE_30 = "main_stage_stage_30.png"
    JESSICA = "jessica_upgrade_ranger.png"
    SEASON_PASS_LVL1 = "season_pass_level1_text.png"
    SEASON_PASS_TICKETS = "season_pass_tickets.png"
    CIRCLE = "leonard_teacher_circle.png"

class Phase6UI(Enum):
    GIFT = "gift_btn.png"
    ACCEPT_ALL = "accept_all.png"

class Diamond(Enum):
    ICON = "diamond_upgrade_icon.png"
    UPGRADE_TEXT = "diamond_upgrade_text.png"
    MAX = "diamond_upgrade_max.png"
    SUCCESS = "diamond_upgrade_success.png"
    MINUS = "diamond_upgrade_minus.png"

class Gear(Enum):
    TEXT = "equip_text.png"
    EQUIP = "go_equip_shirt.png"
    UPGRADE = "equip_go_upgrade.png"
    ENHANCE_SUCCESS = "equip_upgrade_finish.png"
    ENHANCE = "equip_upgrade.png"
    GO_ENHANCE = "equip_go_upgrade.png"
    ARROW = "rene_go_equip.png"

class Quests(Enum):
    LONG = "long_quest.png"

class SeasonPass(Enum):
    ICON = "season_pass_icon.png"
    TEXT = "season_pass_text.png"
    DAILY_NAV = "daily_quest_nav.png"
    CLAIM = "daily_quest_claim.png"
    WEELKY_NAV = "weekly_quest_nav.png"
    PASS_NAV = "season_pass_nav.png"
    CLAIMED_TEXT = "season_pass_claim_text"

class SevenDays(Enum):
    ICON = "7days.png"
    INFO = "7days_info.png"
    QUEST_REWARD = "7day_quest_reward.png"
    DAILY_REWARD = "7day_daily_reward.png"
    CLAIM = "daily_quest_claim.png"
    TEXT = "7days_text.png"
    
