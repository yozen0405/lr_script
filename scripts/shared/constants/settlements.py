from enum import Enum

class Settlement(str, Enum):
    SILVER_BOX = "reward_box_silver.png"
    BRONZE_BOX = "shared/settlement/bronze_box.png"
    ACQUIRED = "acquired.png"
    ONE_REWARD = "shared/settlement/one_reward.png"
    STOP = "shared/settlement/stop.png"
    TEXT = "main_stage/settlement/edge.png"
    PUZZLE_FOUND_TEXT = "shared/settlement/puzzle_found_text.png"
    LEVEL_UP_TEXT = "shared/settlement/level_up_text.png"
    LOSE_TEXT = "shared/settlement/lose_text.png"