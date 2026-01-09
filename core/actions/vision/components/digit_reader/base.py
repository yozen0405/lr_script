import os
import cv2
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

from core.actions.vision.config import DIGIT_TEMPLATE_DIR, TMP_DIR, IMG_DIR
from core.actions.vision.manager import VisionManager
from core.system.logging.logger import log_msg
from core.base.exceptions import GameError


@dataclass
class DigitBox:
    x: int
    y: int
    w: int
    h: int
    area: int


class TemplateDigitOCR:
    def __init__(
        self,
        serial: str,
        template_dir: Optional[str] = None,
        debug: bool = False,
    ):
        self.serial = serial
        self.debug = debug
        self.template_dir = template_dir or DIGIT_TEMPLATE_DIR

        os.makedirs(TMP_DIR, exist_ok=True)

        self.templates_raw: Dict[str, np.ndarray] = self._load_templates(self.template_dir)

        self.tw = max(t.shape[1] for t in self.templates_raw.values())
        self.th = max(t.shape[0] for t in self.templates_raw.values())

        self.templates: Dict[str, np.ndarray] = {
            d: cv2.resize(t, (self.tw, self.th), interpolation=cv2.INTER_AREA)
            for d, t in self.templates_raw.items()
        }

        if self.debug:
            log_msg(self.serial, "Template sizes (raw -> resized)")
            for d, t in self.templates_raw.items():
                log_msg(self.serial, f"{d}: raw={t.shape} resized=({self.th},{self.tw})")
            for d, t in self.templates.items():
                cv2.imwrite(os.path.join(TMP_DIR, f"debug_template_{d}.png"), t)

    def _load_templates(self, template_dir: str) -> Dict[str, np.ndarray]:
        temps: Dict[str, np.ndarray] = {}
        for d in range(10):
            path = os.path.join(IMG_DIR, template_dir, f"{d}.png")
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing template: {path}")

            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise ValueError(f"Failed to read template: {path}")

            _, bw = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            bw = cv2.copyMakeBorder(bw, 6, 6, 6, 6, cv2.BORDER_CONSTANT, value=255)
            temps[str(d)] = bw

        return temps

    def _binarize_roi(self, roi_bgr: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if np.mean(bw) < 127:
            bw = 255 - bw

        kernel = np.ones((3, 3), np.uint8)
        bw = cv2.morphologyEx(bw, cv2.MORPH_OPEN, kernel, iterations=1)
        bw = cv2.copyMakeBorder(bw, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255)

        if self.debug:
            cv2.imwrite(os.path.join(TMP_DIR, "debug_roi_raw.png"), roi_bgr)
            cv2.imwrite(os.path.join(TMP_DIR, "debug_roi_binarized.png"), bw)
            log_msg(self.serial, f"bw unique={np.unique(bw)} shape={bw.shape}")

        return bw

    def _find_digit_boxes(self, bw: np.ndarray) -> List[DigitBox]:
        inv = 255 - bw
        num_labels, _, stats, _ = cv2.connectedComponentsWithStats(inv, connectivity=8)

        boxes: List[DigitBox] = []
        for i in range(1, num_labels):
            x, y, w, h, area = stats[i]
            if area < 80:
                continue
            if h < 12 or w < 4:
                continue
            aspect = w / float(h)
            if aspect < 0.05 or aspect > 1.2:
                continue
            boxes.append(DigitBox(x, y, w, h, area))

        boxes.sort(key=lambda b: b.x)

        if self.debug:
            log_msg(self.serial, f"Found {len(boxes)} digit boxes")
            for i, b in enumerate(boxes):
                log_msg(self.serial, f"box[{i}] x={b.x} y={b.y} w={b.w} h={b.h} area={b.area}")
            vis = cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR)
            for b in boxes:
                cv2.rectangle(vis, (b.x, b.y), (b.x + b.w, b.y + b.h), (0, 0, 255), 2)
            cv2.imwrite(os.path.join(TMP_DIR, "debug_boxes.png"), vis)

        return boxes

    def _crop_and_normalize(self, bw: np.ndarray, box: DigitBox, idx: int) -> np.ndarray:
        digit = bw[box.y:box.y + box.h, box.x:box.x + box.w]

        inv = 255 - digit
        ys, xs = np.where(inv > 0)
        if len(xs) and len(ys):
            digit = digit[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

        digit = cv2.copyMakeBorder(digit, 6, 6, 6, 6, cv2.BORDER_CONSTANT, value=255)

        canvas = np.full((self.th, self.tw), 255, dtype=np.uint8)
        dh, dw = digit.shape[:2]

        scale = min((self.tw - 2) / dw, (self.th - 2) / dh)
        nw, nh = max(1, int(dw * scale)), max(1, int(dh * scale))

        digit_rs = cv2.resize(digit, (nw, nh), interpolation=cv2.INTER_AREA)

        ox = (self.tw - nw) // 2
        oy = (self.th - nh) // 2
        canvas[oy:oy + nh, ox:ox + nw] = digit_rs

        if self.debug:
            cv2.imwrite(os.path.join(TMP_DIR, f"debug_digit_{idx}.png"), canvas)

        return canvas

    def _match_one(self, digit_img: np.ndarray) -> Tuple[str, float]:
        best_d, best_score = "?", -1.0

        for d, templ in self.templates.items():
            diff = cv2.bitwise_xor(digit_img, templ)
            score = 1.0 - float(np.mean(diff)) / 255.0
            if score > best_score:
                best_score = score
                best_d = d

        if self.debug:
            log_msg(self.serial, f"match -> {best_d} ({best_score:.3f})")

        return best_d, best_score

    def read_number(self, roi_bgr: np.ndarray, min_score: float = 0.7) -> int:
        bw = self._binarize_roi(roi_bgr)
        boxes = self._find_digit_boxes(bw)

        if not boxes:
            raise GameError("No digit boxes found")

        out = ""
        for idx, box in enumerate(boxes):
            digit_img = self._crop_and_normalize(bw, box, idx)
            d, score = self._match_one(digit_img)
            out += d if score >= min_score else "?"

        if self.debug:
            log_msg(self.serial, f"final='{out}'")

        if "?" in out:
            raise GameError(f"Unrecognized digits in '{out}'")
        return int(out)


def get_text_num(
    serial: str,
    region: Tuple[int, int, int, int],
    template_dir: Optional[str] = None,
    debug: bool = False,
) -> int:
    reader = TemplateDigitOCR(
        serial=serial,
        template_dir=template_dir,
        debug=debug,
    )

    mgr = VisionManager.get(serial)
    img = mgr.capture()
    if img is None:
        return -1

    x1, y1, x2, y2 = region
    h, w = img.shape[:2]

    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    roi = img[y1:y2, x1:x2]

    if debug:
        cv2.imwrite(os.path.join(TMP_DIR, "debug_full_capture.png"), img)
        log_msg(serial, f"ROI {region} size={roi.shape[:2]}")

    return reader.read_number(roi)
