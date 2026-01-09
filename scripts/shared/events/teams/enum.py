from enum import Enum

class TeamsImg(Enum):
    TEXT = "teams/teams_page/text.png"
    BTN = "teams/teams_page/btn.png"
    SAVE = "teams/teams_page/save_btn.png"
    UPGRADE_BTN = "teams/upgrade_page/btn.png"
    UPGRADE_LVL_BTN = "teams/upgrade_page/level_up_btn.png"
    UPGRADE_SUCCESS = "teams/upgrade_page/success_text.png"
    FILTER_BTN = "teams/teams_page/filter_page/btn.png"
    FILTER_SIX_STARS = "teams/teams_page/filter_page/six_stars_off.png"
    FILTER_EIGHT_STARS = "teams/teams_page/filter_page/eight_stars_off.png"
    FILTER_RANGER = "teams/teams_page/filter_page/unit_ranger_off.png"
    LVL_UP_PAGE_TEXT = "teams/upgrade_page/text.png"
    SELECTOR_FINGER = "teams/interrupt/switch_team/finger.png"
    SWITCH_TEXT = "teams/teams_page/switch_text.png"
    LVL_UP_POP_TEXT = "teams/teams_page/confirm_text.png"
    SORT_BY_BTN = "teams/teams_page/sort_by_btn.png"
    LVL_DESC = "teams/teams_page/sort_page/level_desc.png"
    LVL_ASC = "teams/teams_page/sort_page/level_asc.png"
    SORT_LATEST = "teams/teams_page/sort_page/latest.png"
    RESET = "teams/teams_page/filter_page/reset_btn.png"
    POP_UP_BASIC_NAV_LIGHT = "teams/info_page/text_light.png"
    POP_UP_BASIC_NAV_DARK = "teams/info_page/text_dark.png"
    ARRANGE_DIALOGUE_UP = "teams/interrupt/jessica/arrange_dialogue_up.png"
    ARRANGE_DIALOGUE_DOWN = "teams/interrupt/jessica/arrange_dialogue_down.png"
    SELL_BTN = "teams/teams_page/sell_btn.png"
    RENE_MAINVIEW = "rene.png"
    SHEEP_MAINVIEW = "sheep.png"
    RENE_UPGRADE_TEXT = "rene_level_up_text.png"
    TOTAL_TEXT = "teams/teams_page/total_text.png"

class GearImg(Enum):
    BTN = "rene_go_equip.png"
    TEXT = "equip_text.png"
    EQUIP_BTN = "go_equip_shirt.png"
    FILTER_LIGHT = "equip_filter_light_btn.png"
    FILTER_GRADE_DESC = "gear_filter_grade_desc.png"
    MAIN_PAGE_SWITCH_BTN = "gear_main_page_switch_btn.png"
    EQUIP_CONFIRM_TEXT = "gear_equip_confirm_text.png"

class EnhancePageImg(Enum):
    TEXT = "enhance_page_text.png"
    BTN = "equip_go_upgrade.png"
    SUCCESS_TEXT = "equip_upgrade_finish.png"
    ENHANCE = "equip_upgrade.png"
    CHECKED = "enhance_page_checked.png"
    UPGRADE_TEXT = "enhance_page_upgrade_text.png"

class WeaponType(Enum):
    WAND = "weapon_wand.png"
    CLOVER = "weapon_clover.png"    
    
class ArmorType(Enum):
    SHIRT = "equip_shirt.png"
    SHIELD = "equip_shield_icon.png"


class EnhancePagePos(Enum):
    GEAR1 = (1095, 240)