from enum import Enum
from scripts.shared.constants.base import Base

class Planet(str, Enum):
    EVO_MINE = "special_stage_evo_mine.png"
    WIZARD_CUBE = "special_stage_wizard_cube.png"
    IMMORTAL_SKULL = "special_stage_immortal_skull.png"
    COLLAB = "special_stage_collab_planet.png"
    LIBRARY = "special_stage_library.png"
    LEONARD = "special_stage_leonard_planet.png"

class SpecialStage(Base):
    TEXT = "special_stage_text.png"
    BTN = "special_stage_btn.png"
    ENTER = "enter_special_stage.png"
    CIRCLE = "leonard_teacher_circle_special_stage.png"
    STAGE = "special_stage_num{stage}.png"
    LIMITED = "special_stage_limited_text.png"
    LAB = "special_stage_lab_icon.png"
    