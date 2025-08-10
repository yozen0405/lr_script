from enum import Enum

class Battle(str, Enum):    
    NEXT = "next.png"
    START = "start.png"
    PAUSE = "pause.png"
    CYCLE = "pre_start_again.png"
    MAX_OFF = "pre_start_max_dark.png"
    MAX_ON = "pre_start_max_light.png"
    LOOP_END_TEXT = "loop_settlement_end_text.png"
    ANIME = "stage_anime.png"
    AUTO_BTN_OFF = "auto_btn_off.png"
    AUTO_BTN_OFF2 = "auto_btn_off2.png"
    NO_FEATHER = "no_feather_text.png"