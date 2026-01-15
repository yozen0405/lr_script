from enum import Enum

class Confirm(str, Enum):    
    SMALL = "shared/confirm/confirm_small.png"
    MID = "shared/confirm/confirm_mid.png"
    BIG1 = "shared/confirm/confirm_big1.png"
    BIG2 = "shared/confirm/confirm_big2.png"
    BIG3 = "shared/confirm/confirm_big3.png"
    CANCEL_SMALL = "shared/confirm/cancel_small.png"
    CANCEL_BIG = "shared/confirm/cancel_big.png"