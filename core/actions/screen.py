import time
from core.system.adb import adb_cmd
from core.actions.image_utils import (
    find_template_position, IMG_DIR,
    get_image_path, get_temp_screen_path, store_screen
)
from core.system.logger import log_msg
import pytesseract
import os

TESSERACT_PATH = os.path.join("bin", "tesseract_ocr", "tesseract.exe")
TESSDATA_PATH = os.path.join("bin", "tesseract_ocr", "tessdata")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
os.environ["TESSDATA_PREFIX"] = TESSDATA_PATH

SIMILARITY=0.7
CHECK_INTERVAL=0.5
PACKAGE_NAME = "com.linecorp.LGRGS"
MAIN_ACTIVITY = "com.linecorp.LGRGS.LineRangersAdr"

def exist_click(serial, image_name, threshold=SIMILARITY, wait_time=0.0):
    template = get_image_path(image_name)
    screen_path = get_temp_screen_path(serial)
    store_screen(serial)

    pos = find_template_position(screen_path, template, threshold)
    if pos:
        log_msg(serial, f"找到 {image_name}，點擊 {pos}")
        adb_cmd(serial, ["shell", "input", "tap", str(pos[0]), str(pos[1])])
        time.sleep(wait_time)
        return True
    return False

def exist(serial, image_name, threshold=SIMILARITY, wait_time=0.0):
    template = get_image_path(image_name)
    screen_path = get_temp_screen_path(serial)

    store_screen(serial)

    pos = find_template_position(screen_path, template, threshold)
    if pos:
        log_msg(serial, f"找到 {image_name}，在 {pos}")
        time.sleep(wait_time)
        return True

    log_msg(serial, f"未找到 {image_name}")
    return False

def wait(serial, image_name, threshold=SIMILARITY, timeout=5.0, wait_time=0.1, region=None):
    template = get_image_path(image_name)
    screen_path = get_temp_screen_path(serial)
    start_time = time.time()
    while time.time() - start_time < timeout:
        store_screen(serial)
        pos = find_template_position(screen_path, template, threshold, region=region)
        if pos:
            log_msg(serial, f"找到 {image_name}，在 {pos}")
            time.sleep(wait_time)
            return True
        time.sleep(CHECK_INTERVAL)

    log_msg(serial, f"超時未找到 {image_name}")
    return False
    
def wait_click(serial, target, y=None, threshold=SIMILARITY, timeout=5.0, wait_time=0.5, region=None):
    if isinstance(target, tuple) and len(target) == 2:
        x, y = target
        adb_cmd(serial, ["shell", "input", "tap", str(x), str(y)])
        log_msg(serial, f"點擊座標 ({x}, {y})")
        time.sleep(wait_time)
        return True

    elif isinstance(target, (int, float)) and isinstance(y, (int, float)):
        x = target
        adb_cmd(serial, ["shell", "input", "tap", str(x), str(y)])
        log_msg(serial, f"點擊座標 ({x}, {y})")
        time.sleep(wait_time)
        return True

    elif isinstance(target, str):
        template = get_image_path(target)
        screen_path = get_temp_screen_path(serial)
        start_time = time.time()
        while time.time() - start_time < timeout:
            store_screen(serial)
            pos = find_template_position(screen_path, template, threshold, region=region)
            if pos:
                log_msg(serial, f"找到 {target}，點擊 {pos}")
                adb_cmd(serial, ["shell", "input", "tap", str(pos[0]), str(pos[1])])
                time.sleep(wait_time)
                return True
            time.sleep(CHECK_INTERVAL)

        log_msg(serial, f"超時未找到 {target}")
        return False

    else:
        raise ValueError("請提供圖片檔名、(x, y) tuple 或 x, y 座標")

def wait_vanish(serial, image_name, timeout=10.0, threshold=SIMILARITY, wait_time=0.5):
    template = get_image_path(image_name)
    screen_path = get_temp_screen_path(serial)

    start_time = time.time()
    while time.time() - start_time < timeout:
        store_screen(serial)
        pos = find_template_position(screen_path, template, threshold)
        if not pos:
            log_msg(serial, f"{image_name} 已從畫面中消失")
            time.sleep(wait_time)
            return True
        time.sleep(CHECK_INTERVAL)

    log_msg(serial, f"等待 {image_name} 消失超時")
    return False

def back(serial):
    adb_cmd(serial, ["shell", "input", "keyevent", "4"])

def get_pos(serial, image_name, threshold=SIMILARITY, region=None):
    if region is not None:
        assert isinstance(region, tuple) and len(region) == 4, "region 需為 (x1, y1, x2, y2)"

    template = get_image_path(image_name)
    screen_path = get_temp_screen_path(serial)
    store_screen(serial)

    pos = find_template_position(screen_path, template, threshold, region=region)
    if pos:
        log_msg(serial, f"找到 {image_name}，座標: {pos}" + (f"，region={region}" if region else ""))
    else:
        log_msg(serial, f"找不到 {image_name}" + (f"，region={region}" if region else ""))
    return pos


def drag(serial, *args, threshold=0.7, duration=300, wait_time=0.5, timeout=5.0, raise_error=True):
    if len(args) != 2:
        raise ValueError("drag() 需要兩個參數（兩個座標或兩個圖片名）")

    start_time = time.time()

    while time.time() - start_time < timeout:
        if isinstance(args[0], tuple) and isinstance(args[1], tuple):
            (x1, y1), (x2, y2) = args
            break
        elif isinstance(args[0], str) and isinstance(args[1], str):
            image1, image2 = args
            pos1 = get_pos(serial, image1, threshold)
            pos2 = get_pos(serial, image2, threshold)
            if pos1 and pos2:
                x1, y1 = pos1
                x2, y2 = pos2
                break
            else:
                log_msg(serial, f"等待圖片出現中：{image1} / {image2}")
                time.sleep(0.5)
        else:
            raise ValueError("drag() 傳入的參數類型錯誤")

    log_msg(serial, f"拖曳從 ({x1}, {y1}) 到 ({x2}, {y2})")
    adb_cmd(serial, ["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)])
    time.sleep(wait_time)
    return True
