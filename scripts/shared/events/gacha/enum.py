from enum import Enum

class GachaImg(Enum):
    BTN = "gacha/btn.png"
    TEXT = "gacha/text.png"
    GEAR_NAV = "gacha/gear/btn.png"
    GEAR_SHIRT_PULL =  "gacha_equip_shirt_pull.png"
    SHOP = "gacha/shared/shop.png"
    TICKET_PULL = "gacha/shared/tickets_pull.png"
    DIAMOND_PULL = "gacha/ranger/rubbies_pull.png"
    SKIP = "gacha/ranger/skip.png"
    CONFIRM = "gacha/shared/confirm.png"
    JESSICA_PULL_BTN = "gacha/interrupt/jessica/pull_btn.png"
    JESSICA_POOL_TEXT = "gacha/interrupt/jessica/pool_text.png"
    SUCCESS_TEXT = "gacha/ranger/success_text.png"
    GUARANTEE_TEXT = "gacha_guarantee_text.png"
    GEAR_SUCCESS_TEXT = "gacha/gear/success_text.png"
    GEAR_SKIP = "gacha/gear/skip.png"
    READY_PULL_TEXT = "gacha/shared/ready_pull_text.png"
    NO_DIAMOND_TEXT = "gacha/shared/no_diamond_text.png"
    SHOP_TEXT = "real_money_shop/text.png"

class GachaPool(Enum):
    SPECIAL = "gacha_pool_special.png"
    REGULAR = "gacha_pool_regular.png"
    COLLAB = "gacha_pool_collab.png"
    BROWN = "gacha/ranger/pool/brown.png"

class GachaPullState(Enum):
    PULLED = 1
    NOT_FOUND = 2
    NO_DIAMOND = 3
    UNKNOWN = 4