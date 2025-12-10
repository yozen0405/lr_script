import os
import cv2
from core.system.adb import adb_cmd
import time
import shutil

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


def safe_imread(path: str, serial: str = None, retries: int = 5, delay: float = 0.3):
    """
    安全地讀取圖片，如果圖片是 screen 開頭，且讀取失敗，會自動重拍。
    :param path: 圖片路徑
    :param serial: 設備序號，用於呼叫 store_screen
    :param retries: 最大重試次數
    :param delay: 每次重試等待時間
    :return: 圖片或 None
    """
    path = os.path.abspath(path)

    for i in range(retries):
        if os.path.exists(path):
            try:
                img = cv2.imread(path)
                if img is not None:
                    return img
                else:
                    if os.path.basename(path).startswith("screen"):
                        store_screen(serial)
            except Exception as e:
                print(f"imread 錯誤：{e}")

        time.sleep(delay)

    print(f"safe_imread 失敗：{path}")
    return None

def find_template_position(screen_path, template_path, threshold=0.8, region=None, return_center=True):
    screen = safe_imread(screen_path)
    template = safe_imread(template_path)

    if screen is None or template is None:
        return None

    if region:
        x1, y1, x2, y2 = region
        screen = screen[y1:y2, x1:x2]
        debug_path = os.path.join(TMP_DIR, "region_debug.png")
        cv2.imwrite(debug_path, screen)

    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    print(f"{max_val} >= {threshold}")

    if max_val >= threshold:
        h, w = template.shape[:2]
        offset_x, offset_y = (region[0], region[1]) if region else (0, 0)
        
        tx = max_loc[0] + offset_x
        ty = max_loc[1] + offset_y

        if return_center:
            return (tx + w // 2, ty + h // 2)
        else:
            return (tx, ty, tx + w, ty + h)
    else:
        return None

def check_freeze(serial, threshold=0.98, reset_time=600.0, minimum_interval=15.0):
    current_path = store_screen(serial)
    
    old_path = current_path.replace(".png", "_old.png")
    
    need_reset = False
    if not os.path.exists(old_path):
        need_reset = True
    else:
        file_age = time.time() - os.path.getmtime(old_path)
        if file_age > reset_time:
            need_reset = True
        elif file_age < minimum_interval:
            return False

    if need_reset:
        shutil.copy2(current_path, old_path)
        return False
    
    img_cur = safe_imread(current_path, serial)
    img_old = safe_imread(old_path, serial)

    if img_cur is None or img_old is None:
        print("讀取圖片失敗，無法比對 Freeze")
        return False

    try:
        img_cur_gray = cv2.cvtColor(img_cur, cv2.COLOR_BGR2GRAY)
        img_old_gray = cv2.cvtColor(img_old, cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(img_cur_gray, img_old_gray, cv2.TM_CCOEFF_NORMED)
        similarity = res[0][0]

        if similarity >= threshold:
            return True
        else:
            shutil.copy2(current_path, old_path)
            return False
            
    except Exception as e:
        print(f"比對過程發生錯誤: {e}")
        shutil.copy2(current_path, old_path)
        return False
    
def find_spotlight_center(serial):
    current_path = store_screen(serial)

    img = safe_imread(current_path, serial)
    if img is None:
        print(f"讀取圖片失敗")
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ksize = (51, 51) 
    blurred = cv2.GaussianBlur(gray, ksize, 0)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(blurred)

    if max_val < 50:
        print(f"未偵測到明顯亮區 (Max val: {max_val})")
        return None

    print(f"找到亮區中心: {max_loc}, 亮度值: {max_val}")

    # debug_img = img.copy()
    # cv2.circle(debug_img, max_loc, 40, (0, 0, 255), 3)
    # cv2.putText(debug_img, f"Val:{max_val:.0f}", (max_loc[0]-20, max_loc[1]-50), 
    #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    # result_path = os.path.join(TMP_DIR, "debug_result.png")
    # cv2.imwrite(result_path, debug_img)
    # print(f"-> 已儲存最終判定圖: {result_path}")
    
    return max_loc

def check_region_brightness(serial, region, threshold=20):
    """
    檢查指定區域的平均亮度是否大於閾值
    一般來說，有 dimmeer 的區域亮度 threshold = 18.81

    :param serial: 裝置序號 (用於 store_screen)
    :param region: tuple (x1, y1, x2, y2) 
    :param threshold: 亮度閾值 (0~255)
    :return: Boolean (True if bright enough)
    """
    current_path = store_screen(serial)
    img = safe_imread(current_path, serial)
    
    if img is None:
        print(f"讀取圖片失敗")
        return False

    x1, y1, x2, y2 = region
    roi = img[y1:y2, x1:x2]

    if roi.size == 0:
        print(f"錯誤: 指定的區域無效或大小為 0: {region}")
        return False

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    avg_brightness = cv2.mean(gray)[0]

    print(f"區域 {region} 平均亮度: {avg_brightness:.2f} (閾值: {threshold})")

    debug_path = os.path.join(TMP_DIR, "debug_brightness_region.png")
    cv2.imwrite(debug_path, roi)

    return avg_brightness > threshold