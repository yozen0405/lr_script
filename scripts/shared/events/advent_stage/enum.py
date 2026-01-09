from enum import Enum
from scripts.shared.constants.base import Base

class AdventImg(Base):
    BTN = "advent/btn.png"           
    TEXT = "advent/text.png"      
    VERY_HARD = "advent/preperation_page/difficulty/very_hard.png"  
    NORMAL = "advent_normal_btn.png"
    EASY = "advent_easy_btn.png"
    TEAM_BTN = "advent_team_btn.png"
    TEAM_NUM_ON = "advent_team_num_on_{num}.png"
    TEAM_NUM_OFF = "advent_team_num_off_{num}.png"
    AUTO_BTN_ON = "advent/preperation_page/auto_btn/on.png"
    AUTO_BTN_OFF = "advent/preperation_page/auto_btn/off.png"
    CYCLE = "advent_cycle_btn.png"
    PLUS = "advent_plus_btn.png"
    SCHEDULE = "advent_schedule.png"
    NOT_OPEN_TEXT = "advent/preperation_page/pop_ups/not_open_text.png"
    FROG = "advent/menu_page/frog.png"
    DIGIT_DIR = "advent/menu_page/digits/"

class AdventStageName(Enum):
    LIA = "advent/menu_page/names/lia.png"
    ALICE = "advent/menu_page/names/alice.png"
    SOL = "advent/menu_page/names/sol.png"
    SISI = "advent/menu_page/names/sisi.png"
    HAMMY = "advent/menu_page/names/hammy.png"
    MANAGER = "advent/menu_page/names/manager.png"
    SIMON = "advent/menu_page/names/simon.png"
    JACOB = "advent/menu_page/names/jacob.png"
    FRANKIE = "advent/menu_page/names/frankie.png"
    CLARA = "advent/menu_page/names/clara.png"

    # LUIS = "advent_luis_stage.png"
    # BOSS = "advent_boss_stage.png"
    # SIMON = "advent_simon_stage.png"
    # JACOB = "advent_jacob_stage.png"
    # SISI = "advent_sisi_stage.png"
    # FRANKIE = "advent_frankie_stage.png"
    # CLARA = "advent_clara_stage.png"
    # 
    # CHERINA = "advent_cherina_stage.png"
    # MONKEY = "advent_monkey_stage.png"
    # HAM = "advent_ham_stage.png"
    # DRAGON = "advent_dragon_stage.png"
    
    
    