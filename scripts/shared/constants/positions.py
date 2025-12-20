from enum import Enum

class Positions(Enum):
    FRIEND  = (75, 75)
    FIRE    = (150, 75)
    DIAMOND = (1080, 700)
    MEMBER5 = (910, 700)
    MEMBER4 = (780, 700)
    MEMBER3 = (640, 700)
    MEMBER2 = (515, 700)
    MEMBER1 = (370, 700)
    MISSILE = (200, 700)
    THOMSON = (640, 190)
    METEOR = (75, 75)

    @staticmethod
    def is_in_region(pos: tuple, region: tuple) -> bool:
        x, y = pos
        x1, y1, x2, y2 = region
        return x1 <= x <= x2 and y1 <= y <= y2