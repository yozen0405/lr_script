import cv2
import numpy as np
from typing import Dict, Optional, Tuple

from core.actions.vision.manager import VisionManager
from core.actions.vision.cache import TemplateCache
from core.system.logging.logger import log_msg

from scripts.shared.constants.base import Base
from scripts.shared.events.main_stage.enum import MainStageImg

STAGE_NUM_REGION: Tuple[int, int, int, int] = (163, 8, 292, 46)
STAGE_IMG_SOURCE = MainStageImg.STAGE_NUM_DIGIT

class _ScanningDigitReader:
    def __init__(self, path_template: Base):
        self.templates: Dict[str, np.ndarray] = {}
        self._load_templates(path_template)

    def _load_templates(self, path_template: Base):
        for i in range(10):
            path = path_template(digit=i)
            tmpl = TemplateCache.get(path)
            
            if tmpl is not None:
                self.templates[str(i)] = tmpl

    def read(self, img_region: np.ndarray, threshold=0.9) -> int:
        if img_region is None or not self.templates:
            return -1

        number_str = ""
        cursor = 0
        h, w = img_region.shape[:2]

        max_loop = w 
        loop_count = 0

        while cursor < w and loop_count < max_loop:
            loop_count += 1
            best_digit = None
            best_score = -1
            best_width = 0

            for digit, tmpl in self.templates.items():
                th, tw = tmpl.shape[:2]
                
                if cursor + tw > w or th > h:
                    continue

                crop = img_region[0:h, cursor:cursor+tw]
                
                try:
                    res = cv2.matchTemplate(crop, tmpl, cv2.TM_CCOEFF_NORMED)
                    _, score, _, _ = cv2.minMaxLoc(res)

                    if score > best_score:
                        best_score = score
                        best_digit = digit
                        best_width = tw
                except Exception:
                    continue

            if best_score >= threshold:
                number_str += best_digit
                cursor += best_width
            else:
                cursor += 1

        try:
            return int(number_str) if number_str else -1
        except ValueError:
            return -1

_shared_instance: Optional[_ScanningDigitReader] = None

def _get_reader() -> _ScanningDigitReader:
    global _shared_instance
    if _shared_instance is None:
        _shared_instance = _ScanningDigitReader(STAGE_IMG_SOURCE)
    return _shared_instance

def get_main_stage_num(serial: str) -> int:
    reader = _get_reader()
    
    mgr = VisionManager.get(serial)
    img = mgr.capture()
    
    if img is None:
        return -1
    
    x1, y1, x2, y2 = STAGE_NUM_REGION
    h, w = img.shape[:2]
    
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    
    roi = img[y1:y2, x1:x2]
    
    stage = reader.read(roi)
    
    if stage != -1:
        log_msg(serial, f"目前關卡: {stage}")
    
    return stage