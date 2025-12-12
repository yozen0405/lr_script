from enum import Enum

class TeamsImg(Enum):
    TEXT = "team_text.png"
    BTN = "team_icon.png"
    ICON_LIGHT = "team_icon.png"
    ICON_DARK = "team_icon_dark.png"
    SAVE = "save_team.png"
    UPGRADE_BTN = "upgrade_btn.png"
    UPGRADE_LVL_BTN = "upgrade_lvl_btn.png"
    UPGRADE_SUCCESS = "upgrade_success.png"
    FILTER_BTN = "team_filter_btn.png"
    FILTER_SIX_STARS = "team_filter_6_stars.png"
    FILTER_EIGHT_STARS = "team_filter_8_stars.png"
    FILTER_RANGER = "team_filter_ranger.png"
    LVL_UP_PAGE_TEXT = "team_level_up_page_text.png"
    SELECTOR_FINGER = "team_selector_finger.png"
    SWITCH_TEXT = "team_switch_text.png"
    LVL_UP_POP_TEXT = "team_lvl_up_page_pop_text.png"
    SORT_BY_BTN = "team_sort_by_btn.png"
    LVL_DESC = "team_level_descending.png"
    SORT_LATEST = "team_sort_latest.png"
    RESET = "team_filter_reset_btn.png"
    POP_UP_BASIC_NAV_LIGHT = "team_pop_up_basic_nav_light.png"
    POP_UP_BASIC_NAV_DARK = "team_pop_up_basic_nav_dark.png"
    ARRANGE_DIALOGUE_UP = "team_arrange_dialogue_up.png"
    ARRANGE_DIALOGUE_DOWN = "team_arrange_dialogue_down.png"
    SELL_BTN = "team_sell_btn.png"
    UPGRADE_PAGE_RENE = "team_upgrade_page_rene.png"
    RENE_MAINVIEW = "rene.png"
    SHEEP_MAINVIEW = "sheep.png"
    RENE_UPGRADE_TEXT = "rene_level_up_text.png"

class GearImg(Enum):
    BTN = "rene_go_equip.png"
    TEXT = "equip_text.png"
    EQUIP_BTN = "go_equip_shirt.png"
    FILTER_LIGHT = "equip_filter_light_btn.png"
    FILTER_GRADE_DESC = "gear_filter_grade_desc.png"
    MAIN_PAGE_SWITCH_BTN = "gear_main_page_switch_btn.png"

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