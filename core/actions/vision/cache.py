import os
import cv2
import threading
import numpy as np
from typing import Dict, Optional
from core.base.exceptions import FatalError
from .config import IMG_DIR

class TemplateCache:
    _cache: Dict[str, np.ndarray] = {}
    _lock = threading.Lock()

    @classmethod
    def get(cls, image_name: str) -> np.ndarray:
        if image_name in cls._cache:
            return cls._cache[image_name]

        with cls._lock:
            if image_name in cls._cache:
                return cls._cache[image_name]

            path = os.path.join(IMG_DIR, image_name)
            if not os.path.exists(path):
                raise FatalError(f"[Vision] 找不到資源圖片: {path}")
            
            img = cv2.imread(path, cv2.IMREAD_COLOR)
            if img is None:
                raise FatalError(f"[Vision] 圖片格式錯誤或損毀: {path}")
                
            cls._cache[image_name] = img
            return img