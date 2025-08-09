import time
from core.system.adb import adb_cmd
from core.actions.image_utils import (
    find_template_position, IMG_DIR,
    get_image_path, get_temp_screen_path, store_screen,
    safe_imread
)
from core.system.logger import log_msg
import pytesseract
from PIL import Image
import cv2
import os
from difflib import SequenceMatcher
import re
import subprocess
import numpy as np

TESSERACT_PATH = os.path.join("bin", "tesseract_ocr", "tesseract.exe")
TESSDATA_PATH = os.path.join("bin", "tesseract_ocr", "tessdata")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
os.environ["TESSDATA_PREFIX"] = TESSDATA_PATH

SIMILARITY=0.7

class ImageProcceser:
    def __init__(self, serial):
        self.serial = serial

    def _clean_ocr_text_basic(self, text: str):
        """原本的清理流程：保留字母、數字與空白"""
        text = text.strip()
        text = text.replace("\n", " ")
        text = re.sub(r"[^A-Za-z0-9 ]+", " ", text) 
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _clean_ocr_text_numerical(self, text: str) -> str:
        """僅保留數字；移除所有空白與非數字"""
        text = text.strip().replace("\n", "")
        text = re.sub(r"[^0-9]+", "", text)
        return text
        
    def _extract_text(self, region=None, threshold=0.8, mode="basic"):
        screen_path = get_temp_screen_path(self.serial)
        store_screen(self.serial)
        img = safe_imread(screen_path)

        if isinstance(region, tuple) and len(region) == 4: 
            x1, y1, x2, y2 = region
        else:
            raise ValueError("格式:(x1, y1, x2, y2)")
        region = img[y1:y2, x1:x2]

        if mode == "numerical":
            pre = self._preprocess_digit(region)
            config = "--psm 10 -c tessedit_char_whitelist=0123456789 --oem 1"
        else:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            adjusted = cv2.convertScaleAbs(gray, alpha=0.9, beta=10)
            _, thresh = cv2.threshold(adjusted, 0, 255, cv2.THRESH_TOZERO + cv2.THRESH_OTSU)

            scaled = cv2.resize(thresh, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
            pre = cv2.GaussianBlur(scaled, (3, 3), 0)
            config = "--psm 6"

        cv2.imwrite(f"debug_output.png", pre)

        pil = Image.fromarray(pre)
        text = pytesseract.image_to_string(pil, config=config, lang="eng")
        
        cleaned = self._clean_ocr_text_numerical(text) if mode == "numerical" else self._clean_ocr_text_basic(text)
        log_msg(self.serial, f"OCR 辨識結果: {cleaned}")
        
        return cleaned

    def match_string_from_region(
        self,
        target_text: str,
        region: tuple = None,
        threshold: float = 0.75
    ) -> bool:
        """
        從指定區域 OCR 並比對與目標文字的相似度是否達標。
        """
        result_text = self._extract_text(self.serial, region=region)

        result_cleaned = " ".join(result_text.strip().split())
        target_cleaned = " ".join(target_text.strip().split())
        score = SequenceMatcher(None, result_cleaned.lower(), target_cleaned.lower()).ratio()

        log_msg(self.serial, f"OCR: '{result_cleaned}' vs Target: '{target_cleaned}' => Score: {score:.2f}")
        return score >= threshold

    def get_main_stage_num(self, threshold=0.9):
        screen_path = get_temp_screen_path(self.serial)
        store_screen(self.serial)
        img = safe_imread(screen_path)
        
        x1 = 221
        y1 = 15
        x2 = 328
        y2 = 65
        region = img[y1:y2, x1:x2]
        cv2.imwrite("debug_output.png", region)

        number = ""
        bin_region = region 

        cursor = 0
        region_height, region_width, _ = bin_region.shape

        digit_templates = {}
        for i in range(10):
            path = os.path.join(IMG_DIR, f"num{i}.png")
            tmpl = safe_imread(path)
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
                # cv2.imwrite(f"debug_output_{cursor}.png", crop)
                res = cv2.matchTemplate(crop, tmpl, cv2.TM_CCOEFF_NORMED)
                score = cv2.minMaxLoc(res)[1]

                if score > best_score:
                    # print(f"[{cursor} th]: testing: {digit}, got score: {score}")
                    best_score = score
                    best_digit = digit
                    best_width = tw

            if best_score >= threshold:
                # print(best_score, cursor)
                number += best_digit
                cursor += best_width
            else:
                cursor += 1

        log_msg(self.serial, f"辨識結果: {number}")
        return number


def get_main_stage_num(serial):
    img_proccesser = ImageProcceser(serial)
    log_msg(serial, img_proccesser.get_main_stage_num())