from enum import Enum

class Guild(str, Enum):
    TEXT = "guild_text.png"
    RAID_TEXT = "guild_raid_text.png"
    TOUCH_SCREEN = "guild_touch_screen.png"
    BTN = "guild_btn.png"
    MEMBER_NAV_LIGHT = "guild_member_nav_light.png"
    SUPPORT_DARK = "guild_support_all_dark.png"
    SUPPORT_LIGHT = "guild_support_all_light.png"
    RAID_BTN = "guild_raid_btn.png"
    QUEST_BTN = "guild_quest_btn.png"
    RAID_ATTACK = "guild_raid_attack.png"
    COMPLETE = "guild_raid_settlement_complete.png"
    LVL_UP = "guild_raid_settlement_lvl_up.png"
    CLAIM = "daily_quest_claim.png"
    WAR_REWARD_POP = "guild_war_reward.png"
    ACCEPT_SUPPORT_POP = "guild_accept_support_text.png"
    AUTO_BTN_OFF = "guild_raid_auto_btn_off.png"
    PURCHASE_POP = "guild_purchase_pop_text.png"
    RAID_LIMITED = "guild_raid_limited_text.png"
    QUEST_CLAIMED_TEXT = "guild_quest_claimed_text.png"
    QUEST_FINISHED = "guild_quest_finished.png"
    RAID_OCCUPIED = "guild_raid_occupied_text.png"
    RAID_TRY_AGAIN = "guild_raid_error_try_again.png"

class GuildRaidSide(Enum):
    LEFT = (275, 469, 531, 539)
    RIGHT = (746, 469, 1013, 539)