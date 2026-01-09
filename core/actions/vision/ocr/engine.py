import os
import time
import pytesseract
from PIL import Image
import numpy as np
from core.base.exceptions import FatalError
from core.actions.vision.config import TESSERACT_BIN, TESSDATA_DIR, OCR_CONFIG_BASIC, OCR_CONFIG_NUMERICAL, TESSERACT_LANG, TMP_DIR
from core.actions.vision.ocr.filters import TextFilter
from core.actions.vision.ocr.enum import OCRMode
import cv2

if os.path.exists(TESSERACT_BIN):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_BIN
    os.environ["TESSDATA_PREFIX"] = TESSDATA_DIR

class TesseractEngine:

    @staticmethod
    def preprocess_for_ocr(img: np.ndarray, mode: OCRMode = OCRMode.BASIC, debug: bool = False) -> np.ndarray:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        result_img = gray

        if mode == OCRMode.NUMERICAL:
            gray = cv2.resize(gray, None, fx=6, fy=6, interpolation=cv2.INTER_CUBIC)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            if np.mean(bw) < 127:
                bw = 255 - bw

            kernel = np.ones((3, 3), np.uint8)
            bw = cv2.morphologyEx(bw, cv2.MORPH_OPEN, kernel, iterations=1)
            bw = cv2.copyMakeBorder(bw, 12, 12, 12, 12, cv2.BORDER_CONSTANT, value=255)
            result_img = bw

        else:
            adjusted = cv2.convertScaleAbs(gray, alpha=0.9, beta=10)
            _, thresh = cv2.threshold(adjusted, 0, 255, cv2.THRESH_TOZERO + cv2.THRESH_OTSU)
            
            scaled = cv2.resize(thresh, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
            result_img = cv2.GaussianBlur(scaled, (3, 3), 0)
            # scaled = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
            # scaled = cv2.GaussianBlur(scaled, (3, 3), 0)
            # adjusted = cv2.convertScaleAbs(scaled, alpha=1.2, beta=0)
            # _, bw = cv2.threshold(adjusted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # if np.mean(bw) < 127:
            #     bw = 255 - bw

            # kernel = np.ones((3, 3), np.uint8)
            # bw = cv2.morphologyEx(bw, cv2.MORPH_OPEN, kernel, iterations=1)
            # result_img = bw

        timestamp = int(time.time() * 1000)
        filename = f"{mode}_{timestamp}.png"
        path = os.path.join(TMP_DIR, filename)
        
        cv2.imwrite(path, result_img)

        return result_img

    @staticmethod
    def image_to_string(img: np.ndarray, mode=OCRMode.BASIC) -> str:
        if img is None: return ""

        processed_img = TesseractEngine.preprocess_for_ocr(img, mode)
        config = OCR_CONFIG_NUMERICAL if mode == OCRMode.NUMERICAL else OCR_CONFIG_BASIC
        
        try:
            pil_img = Image.fromarray(processed_img)
            raw_text = pytesseract.image_to_string(pil_img, config=config, lang=TESSERACT_LANG)
        except Exception:
            raise FatalError("Tesseract OCR 執行失敗")

        if mode == OCRMode.NUMERICAL:
            return TextFilter.numerical(raw_text)
        else:
            return TextFilter.basic(raw_text)