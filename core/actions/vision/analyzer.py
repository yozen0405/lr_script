import cv2
import numpy as np
from typing import List, Optional, Tuple, Union

from core.system.logging.logger import log_msg

class ImageAnalyzer:
    """純影像處理邏輯，不涉及設備操作"""

    @staticmethod
    def match_template(
        screen: np.ndarray, 
        template: np.ndarray, 
        threshold: float, 
        region: Tuple[int, int, int, int] = None, 
        return_center: bool = True
    ) -> Tuple[Optional[Union[Tuple[int, int], Tuple[int, int, int, int]]], float]:
        search_img = screen
        offset_x, offset_y = 0, 0

        if region:
            x1, y1, x2, y2 = region
            h, w = screen.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            search_img = screen[y1:y2, x1:x2]
            offset_x, offset_y = x1, y1

        try:
            res = cv2.matchTemplate(search_img, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if max_val >= threshold:
                h_t, w_t = template.shape[:2]
                tl_x = max_loc[0] + offset_x
                tl_y = max_loc[1] + offset_y

                if return_center:
                    result = (tl_x + w_t // 2, tl_y + h_t // 2)
                else:
                    result = (tl_x, tl_y, tl_x + w_t, tl_y + h_t)
                
                return (result, max_val)
            
            return (None, max_val)

        except Exception:
            return (None, 0.0)
        
    @staticmethod
    def match_template_all(
        screen: np.ndarray, 
        template: np.ndarray, 
        threshold: float, 
        region: Tuple[int, int, int, int] = None, 
        return_center: bool = True
    ) -> List[Union[Tuple[int, int], Tuple[int, int, int, int]]]:
        search_img = screen
        offset_x, offset_y = 0, 0

        if region:
            x1, y1, x2, y2 = region
            h, w = screen.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            search_img = screen[y1:y2, x1:x2]
            offset_x, offset_y = x1, y1

        results = []
        
        try:
            res = cv2.matchTemplate(search_img, template, cv2.TM_CCOEFF_NORMED)
            h_t, w_t = template.shape[:2]
            
            while True:
                _, max_val, _, max_loc = cv2.minMaxLoc(res)

                if max_val < threshold:
                    break

                tl_x = max_loc[0] + offset_x
                tl_y = max_loc[1] + offset_y

                if return_center:
                    point = (tl_x + w_t // 2, tl_y + h_t // 2)
                else:
                    point = (tl_x, tl_y, tl_x + w_t, tl_y + h_t)
                
                results.append(point)

                mask_x_start = max_loc[0] - w_t // 2
                mask_x_end = max_loc[0] + w_t // 2
                mask_y_start = max_loc[1] - h_t // 2
                mask_y_end = max_loc[1] + h_t // 2

                mask_x_start = max(0, mask_x_start)
                mask_y_start = max(0, mask_y_start)
                mask_x_end = min(res.shape[1], mask_x_end)
                mask_y_end = min(res.shape[0], mask_y_end)

                res[mask_y_start:mask_y_end, mask_x_start:mask_x_end] = -1.0

            results.sort()
            
            return results

        except Exception as e:
            return []

    @staticmethod
    def calculate_similarity(img1: np.ndarray, img2: np.ndarray) -> float:
        try:
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            res = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)
            return res[0][0]
        except Exception:
            return 0.0

    @staticmethod
    def get_brightness(img: np.ndarray, region: Tuple[int, int, int, int]) -> float:
        """計算區域平均亮度"""
        x1, y1, x2, y2 = region
        roi = img[y1:y2, x1:x2]
        if roi.size == 0: return 0.0
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        return cv2.mean(gray)[0]

    @staticmethod
    def find_spotlight(img: np.ndarray, region=None) -> Tuple[int, int, int]:
        """
        找出畫面中最亮的區域中心點
        
        :param img: Input image
        :type img: np.ndarray
        :param region: Region to search within (x1, y1, x2, y2)
        :type region: Optional[Tuple[int, int, int, int]]
        :return: (center_x, center_y, brightness)
        :rtype: Tuple[int, int, int]
        """
        offset_x, offset_y = 0, 0
        search_img = img

        if region:
            x1, y1, x2, y2 = region
            search_img = img[y1:y2, x1:x2]
            offset_x, offset_y = x1, y1

        gray = cv2.cvtColor(search_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (51, 51), 0)
        _, max_val, _, max_loc = cv2.minMaxLoc(blurred)

        final_x = max_loc[0] + offset_x
        final_y = max_loc[1] + offset_y
        return (final_x, final_y, max_val)