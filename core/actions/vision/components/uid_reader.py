from typing import Callable, Tuple
from core.actions.vision.ocr.actions import get_text

UID_REGION_COORDINATES: Tuple[int, int, int, int] = (396, 243, 627, 289)

def get_device_uid(serial: str) -> str:
    uid = get_text(serial, UID_REGION_COORDINATES)
    
    return uid.strip()