from enum import Enum, auto

class TutorialState(Enum):
    GUIDE_SKIP = auto()
    SKIP_TUTORIAL_TEXT = auto()
    SKIP_DIALOG = auto()
    UNKNOWN = auto()