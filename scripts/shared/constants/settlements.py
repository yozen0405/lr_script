from enum import Enum

class Settlement(str, Enum):
    SILVER_BOX = "reward_box_silver.png"
    BRONZE_BOX = "reward_box_bronze.png"
    ACQUIRED = "acquired.png"
    ONE_REWARD = "oneReward.png"
    STOP = "stop.png"
    TEXT = "main_stage_settlement_text.png"
    CANCEL_LOSE = "cancel_lose.png"
    CLOSE_LOSE_TIPS = "close_lose_tips.png"
    AGAIN = "main_stage_settlement_again.png"
    NEXT = "main_stage_settlement_next.png"
    NEXT_FEATURE_TEXT = "main_stage_settlement_next_feature_text.png"