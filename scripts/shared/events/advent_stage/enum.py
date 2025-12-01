from enum import Enum
from scripts.shared.constants.base import Base

class Advent(Base):
    BTN = "advent_btn.png"           
    TEXT = "advent_text.png"      
    VERY_HARD = "advent_very_hard_btn.png"  
    NORMAL = "advent_normal_btn.png"
    EASY = "advent_easy_btn.png"
    TEAM_BTN = "advent_team_btn.png"
    TEAM_NUM_ON = "advent_team_num_on_{num}.png"
    TEAM_NUM_OFF = "advent_team_num_off_{num}.png"
    CYCLE = "advent_cycle_btn.png"
    PLUS = "advent_plus_btn.png"
    SCHEDULE = "advent_schedule.png"

class AdventStageName(Enum):
    CHERINA = "advent_cherina_stage.png"
    MONKEY = "advent_monkey_stage.png"
    HAM = "advent_ham_stage.png"
    DRAGON = "advent_dragon_stage.png"
    JACOB = "advent_jacob_stage.png"
    LIA = "advent_lia_stage.png"
    CLARA = "advent_clara_stage.png"
    SISI = "advent_sisi_stage.png"
    FRANKIE = "advent_frankie_stage.png"
    MANAGER = "advent_manager_stage.png"
    LUIS = "advent_luis_stage.png"
    BOSS = "advent_boss_stage.png"
    SIMON = "advent_simon_stage.png"
    
    