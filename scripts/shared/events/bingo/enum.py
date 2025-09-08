from enum import Enum
from scripts.shared.constants.base import Base

class Bingo(Base):
    BTN = "bingo_btn.png"
    TEXT = "bingo_text.png"
    RANDOM = "bingo_random.png"
    MISSION_ON = "bingo_mission_on.png"
    MISSION_TEXT = "bingo_mission_text.png"
    GET = "daily_quest_claim.png"
    CLOSE_AD = "bingo_close_ad_{num}.png"
    MISSION_CLAIMED_TEXT = "guild_quest_claimed_text.png"
    REDRAW = "bingo_redraw.png"
    GOT_NEW_TEXT = "bingo_get_new_text.png"
    NO_TICKETS_TEXT = "bingo_no_tickets_text.png"
    DUPLICATE_TEXT = "bingo_duplicate_text.png"

class BingoAdPositions(Enum):
    """
    the screen is 1280x720
    so i need the positon to be (x1, y1, x2, y2)
    each of them is a square(96 * 96) from four corners
    """
    TOP_LEFT = (0, 0, 96, 96)
    TOP_RIGHT = (1184, 0, 1280, 96)