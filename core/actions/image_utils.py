import os
import cv2
from core.system.adb import adb_cmd

IMG_DIR = os.path.join("bin", "img")
TMP_DIR = os.path.join("bin", "tmp")

def get_image_path(image_name):
    """取得圖片完整路徑"""
    return os.path.join(IMG_DIR, image_name)

def get_temp_screen_path(serial):
    """統一暫存螢幕截圖路徑"""
    display = serial.split(":")[1] if ":" in serial else serial
    filename = f"screen_{display}.png"
    return os.path.join(TMP_DIR, filename)

def store_screen(serial):
    """擷取畫面並儲存為乾淨檔名，回傳本地檔案路徑"""
    path = get_temp_screen_path(serial)
    adb_cmd(serial, ["shell", "screencap", "-p", "/sdcard/screen.png"])
    adb_cmd(serial, ["pull", "/sdcard/screen.png", path])
    return path

def find_template_position(screen_path, template_path, threshold=0.8, region=None):
    """OpenCV 圖像比對，找出模板位置"""
    screen = cv2.imread(screen_path)
    template = cv2.imread(template_path)

    if screen is None or template is None:
        return None

    if region:
        x1, y1, x2, y2 = region
        screen = screen[y1:y2, x1:x2]

    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    if max_val >= threshold:
        h, w = template.shape[:2]
        offset_x, offset_y = (region[0], region[1]) if region else (0, 0)
        return (max_loc[0] + w // 2 + offset_x, max_loc[1] + h // 2 + offset_y)
    else:
        return None
