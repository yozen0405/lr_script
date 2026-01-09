from typing import Tuple, Optional, Union
from difflib import SequenceMatcher
from core.actions.vision.manager import VisionManager
from core.actions.vision.ocr.engine import TesseractEngine
from core.system.logging.logger import log_msg
from core.actions.vision.ocr.enum import OCRMode

def get_text(serial: str, region: Tuple[int, int, int, int], mode=OCRMode.BASIC) -> str:
    mgr = VisionManager.get(serial)
    
    img = mgr.capture()
    if img is None: return ""
    
    x1, y1, x2, y2 = region
    roi = img[y1:y2, x1:x2]
    
    text = TesseractEngine.image_to_string(roi, mode)
    log_msg(serial, f"OCR Result: '{text}' (Region: {region})")
    return text

def match_string_from_region(serial: str, target: str, region: Tuple[int, int, int, int], threshold=0.75) -> bool:
    detected = get_text(serial, region, mode=OCRMode.BASIC)
    def clean(s): return " ".join(s.strip().lower().split())
    
    score = SequenceMatcher(None, clean(detected), clean(target)).ratio()
    log_msg(serial, f"Text Match: '{detected}' vs '{target}' ({score:.2f})")
    
    return score >= threshold
