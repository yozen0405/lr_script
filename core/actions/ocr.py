import os
import re
import cv2
import numpy as np
import pytesseract
from PIL import Image
from difflib import SequenceMatcher

from core.system.logging.logger import log_msg
from core.actions.vision import get_manager, TemplateCache

TESSERACT_PATH = os.path.join("bin", "tesseract_ocr", "tesseract.exe")
TESSDATA_PATH = os.path.join("bin", "tesseract_ocr", "tessdata")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
os.environ["TESSDATA_PREFIX"] = TESSDATA_PATH

class ImageProcessor:
    def __init__(self, serial):
        self.serial = serial
        # 取得該 Serial 專屬的 VisionManager 實例
        self.vm = get_manager(serial)

    def _clean_ocr_text_basic(self, text: str):
        """保留字母、數字與空白"""
        text = text.strip().replace("\n", " ")
        text = re.sub(r"[^A-Za-z0-9 ]+", " ", text) 
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _clean_ocr_text_numerical(self, text: str) -> str:
        """僅保留數字"""
        text = text.strip().replace("\n", "")
        text = re.sub(r"[^0-9]+", "", text)
        return text
        
    def _extract_text(self, region=None, threshold=0.8, mode="basic"):
        img = self.vm._capture_screen()

        if img is None:
            log_msg(self.serial, "OCR 錯誤: 無法獲取截圖")
            return ""

        if isinstance(region, tuple) and len(region) == 4: 
            x1, y1, x2, y2 = region
            h, w = img.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            roi = img[y1:y2, x1:x2]
        else:
            raise ValueError("OCR 需指定 region: (x1, y1, x2, y2)")

        if mode == "numerical":
            pre = self._preprocess_digit(roi) 
            config = "--psm 10 -c tessedit_char_whitelist=0123456789 --oem 1"
        else:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            adjusted = cv2.convertScaleAbs(gray, alpha=0.9, beta=10)
            _, thresh = cv2.threshold(adjusted, 0, 255, cv2.THRESH_TOZERO + cv2.THRESH_OTSU)

            scaled = cv2.resize(thresh, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
            pre = cv2.GaussianBlur(scaled, (3, 3), 0)
            config = "--psm 6"

        # 直接將 numpy array 轉為 PIL Image，不需要存檔再讀檔
        pil = Image.fromarray(pre)
        text = pytesseract.image_to_string(pil, config=config, lang="eng")
        
        cleaned = self._clean_ocr_text_numerical(text) if mode == "numerical" else self._clean_ocr_text_basic(text)
        log_msg(self.serial, f"OCR 結果: {cleaned}")
        
        return cleaned

    def _preprocess_digit(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    def match_string_from_region(self, target_text: str, region: tuple = None, threshold: float = 0.75) -> bool:
        result_text = self._extract_text(region=region)
        
        result_cleaned = " ".join(result_text.strip().split())
        target_cleaned = " ".join(target_text.strip().split())
        score = SequenceMatcher(None, result_cleaned.lower(), target_cleaned.lower()).ratio()

        # log_msg(self.serial, f"比對: '{result_cleaned}' vs '{target_cleaned}' ({score:.2f})")
        return score >= threshold
    
    def get_device_uid(self):
        region = (396, 243, 627, 289)
        uid = self._extract_text(region=region)
        return uid

    def get_main_stage_num(self, threshold=0.9):
        img = self.vm._capture_screen()
        if img is None: return -1
        
        x1, y1, x2, y2 = 163, 8, 292, 46
        region = img[y1:y2, x1:x2]
        cv2.imwrite("bin/tmp/debug_stage_num_region.png", region)

        number = ""
        bin_region = region 
        cursor = 0
        region_height, region_width, _ = bin_region.shape

        digit_templates = {}
        for i in range(10):
            tmpl = TemplateCache.get(f"main_stage/preperation_page/stage_num/{i}.png")
            if tmpl is not None:
                digit_templates[str(i)] = tmpl

        while cursor < region_width:
            best_digit = None
            best_score = -1
            best_width = 0

            for digit, tmpl in digit_templates.items():
                th, tw, _ = tmpl.shape
                if cursor + tw > region_width or th > region_height:
                    continue

                crop = bin_region[0:region_height, cursor:cursor+tw]
                
                res = cv2.matchTemplate(crop, tmpl, cv2.TM_CCOEFF_NORMED)
                score = cv2.minMaxLoc(res)[1]

                if score > best_score:
                    best_score = score
                    best_digit = digit
                    best_width = tw

            if best_score >= threshold:
                number += best_digit
                cursor += best_width
            else:
                cursor += 1

        try:
            val = int(number)
            log_msg(self.serial, f"正在第 {val} 關")
            return val
        except ValueError:
            return -1

def get_device_uid(serial):
    return ImageProcessor(serial).get_device_uid()

def get_main_stage_num(serial):
    return ImageProcessor(serial).get_main_stage_num()

def match_string_from_region(serial, target_text: str, region: tuple = None, threshold: float = 0.75):
    return ImageProcessor(serial).match_string_from_region(target_text, region, threshold)