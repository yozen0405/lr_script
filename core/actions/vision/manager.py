import time
from typing import Any, Callable, Dict, List, Tuple, Optional, Union
from core.system.logging.logger import log_msg
from .device import DeviceController
from .cache import TemplateCache
from .analyzer import ImageAnalyzer
from .config import DEFAULT_THRESHOLD
import numpy as np

class VisionManager:
    _instances: Dict[str, 'VisionManager'] = {}

    def __init__(self, serial: str):
        self.serial = serial
        self.device = DeviceController(serial)
        
        self._last_freeze_frame = None
        self._last_freeze_time = 0

    @classmethod
    def get(cls, serial: str) -> 'VisionManager':
        if serial not in cls._instances:
            cls._instances[serial] = VisionManager(serial)
        return cls._instances[serial]

    def capture(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        result = self.device.screenshot()
        if region:
            (x1, y1, x2, y2) = region
            return result[y1:y2, x1:x2]
        return result

    def find(
        self, 
        image_name: str, 
        threshold: float = None, 
        region: Tuple[int, int, int, int] = None, 
        return_center: bool = True
    ) -> Optional[Union[Tuple[int, int], Tuple[int, int, int, int]]]:
        
        thresh = threshold or DEFAULT_THRESHOLD
        screen = self.device.screenshot()
        template = TemplateCache.get(image_name)
        
        result, confidence = ImageAnalyzer.match_template(screen, template, thresh, region, return_center)

        log_msg(self.serial, f"{confidence:.2f} >= {thresh}, region={region}" if region else f"{confidence:.2f} >= {thresh}")

        return result
    
    def find_all(
        self, 
        image_name: str, 
        threshold: float = None, 
        region: Tuple[int, int, int, int] = None, 
        return_center: bool = True
    ) -> List[Union[Tuple[int, int], Tuple[int, int, int, int]]]:
        
        thresh = threshold or DEFAULT_THRESHOLD
        screen = self.device.screenshot()
        template = TemplateCache.get(image_name)
        
        results = ImageAnalyzer.match_template_all(screen, template, thresh, region, return_center)

        # log_msg(self.serial, f"Found {len(results)} matches >= {thresh}")

        return results
    
    def check_freeze(self, threshold=0.999, reset_time=600.0, timeout=120.0) -> bool:
        current_frame = self.device.screenshot()
        now = time.time()

        if self._last_freeze_frame is None or (now - self._last_freeze_time > reset_time):
            self._last_freeze_frame = current_frame
            self._last_freeze_time = now
            return False

        if (now - self._last_freeze_time) < timeout:
            return False

        similarity = ImageAnalyzer.calculate_similarity(current_frame, self._last_freeze_frame)
        
        self._last_freeze_frame = current_frame
        self._last_freeze_time = now

        if similarity >= threshold:
            log_msg(self.serial, f"畫面凍結警告 (Sim: {similarity:.4f})")
            return True
        return False
    
    def check_region_brightness(self, region: Tuple[int, int, int, int], threshold: float) -> bool:
        screen = self.device.screenshot()
        if screen is None: return False
        
        val = ImageAnalyzer.get_brightness(screen, region)
        log_msg(self.serial, f"區域亮度: {val:.2f} (閾值: {threshold})")
        return val > threshold

    def find_spotlight_center(self, region=None) -> Optional[Tuple[int, int]]:
        screen = self.device.screenshot()
        if screen is None: return None
        
        (final_loc, max_val) = ImageAnalyzer.find_spotlight(screen, region)
        log_msg(self.serial, f"找到亮區中心: {final_loc}, 亮度: {max_val}")
        
        if max_val < 50:
            return None
        return final_loc