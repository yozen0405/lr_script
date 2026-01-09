from enum import Enum

class Positions(Enum):
    FRIEND  = (33, 41)
    DIAMOND = (812, 487)
    MEMBER5 = (683, 505)
    MEMBER4 = (585, 505)
    MEMBER3 = (486, 505)
    MEMBER2 = (380, 505)
    MEMBER1 = (274, 505)
    MISSILE = (141, 507)
    THOMSON = (480, 193)
    METEOR = (33, 41)

    @staticmethod
    def is_in_region(pos: tuple, region: tuple) -> bool:
        x, y = pos
        x1, y1, x2, y2 = region
        return x1 <= x <= x2 and y1 <= y <= y2