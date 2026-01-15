from enum import Enum
from scripts.shared.constants.base import Base

class Planet(str, Enum):
    EVO_MINE = "special_stage/planets/evo_mine.png"
    WIZARD_CUBE = "special_stage_wizard_cube.png"
    IMMORTAL_SKULL = "special_stage_immortal_skull.png"
    COLLAB = "special_stage_collab_planet.png"
    LIBRARY = "special_stage_library.png"
    LEONARD = "special_stage_leonard_planet.png"
    CHRISTMAS = "special_stage_christmas_planet.png"

class SpecialStage(Base):
    TEXT = "special_stage/text.png"
    BTN = "special_stage/btn.png"
    ENTER = "special_stage/menu/enter.png"
    STAGE = "special_stage/stages/{stage}.png"
    LIMITED = "special_stage/menu/limit_text.png"
    LAB = "special_stage/menu/lab.png"