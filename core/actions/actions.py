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


def force_close(serial):
    log_msg(serial, f"強制關閉 {PACKAGE_NAME}")
    result = adb_cmd(serial, ["shell", "am", "force-stop", PACKAGE_NAME])
    if result.returncode == 0:
        log_msg(serial, f"已成功關閉 {PACKAGE_NAME}")
    else:
        log_msg(serial, f"關閉失敗：{result.stderr.decode().strip()}")

def force_close_all_apps(serial, timeout: float = 10.0, delay: float = 0.5):
    start = time.time()
    closed_total = 0

    allow_list = {
        "com.android.browser",
        "com.android.vending",
        "com.linecorp.LGRGS"
    }

    while time.time() - start < timeout:
        for pkg in allow_list:
            r = adb_cmd(serial, ["shell", "am", "force-stop", pkg])
            if r.returncode == 0:
                log_msg(serial, f"已關閉：{pkg}")
                closed_total += 1
            else:
                log_msg(serial, f"無法關閉：{pkg}")
            time.sleep(delay)

    log_msg(serial, f"共關閉 {closed_total} 個 App")

def force_close_line(serial, timeout: float = 5.0, delay: float = 0.5):
    target_pkg = "jp.naver.line.android"
    start = time.time()
    closed = False

    while time.time() - start < timeout:
        r = adb_cmd(serial, ["shell", "am", "force-stop", target_pkg])
        if r.returncode == 0:
            log_msg(serial, f"已關閉 LINE：{target_pkg}")
            closed = True
        else:
            log_msg(serial, f"無法關閉 LINE：{target_pkg}")
        time.sleep(delay)

    if not closed:
        log_msg(serial, "未發現 LINE 或已經關閉")
    return closed

def launch_game(serial, wait_time=1.0):
    log_msg(serial, f"啟動遊戲 {PACKAGE_NAME}")
    result = adb_cmd(serial, [
        "shell", "am", "start", "-n", f"{PACKAGE_NAME}/{MAIN_ACTIVITY}"
    ])
    if result.returncode == 0:
        log_msg(serial, f"已成功啟動 {PACKAGE_NAME}")
        time.sleep(wait_time)
    else:
        log_msg(serial, f"啟動失敗：{result.stderr.decode().strip()}")

def pull_account_file(serial: str, uid: str, ranger_list: list, local_path="./bin/acc/"):
    remote_src = f"/data/data/{PACKAGE_NAME}/shared_prefs/_LINE_COCOS_PREF_KEY.xml"
    remote_tmp = f"/sdcard/{uid}_temp.xml"
    local_tmp = os.path.join(local_path, "temp.xml")

    adb_cmd(serial, ["shell", "su", "-c", f"cp {remote_src} {remote_tmp}"])

    os.makedirs(local_path, exist_ok=True)
    result = adb_cmd(serial, ["pull", remote_tmp, local_tmp])

    if result.returncode == 0:
        adb_cmd(serial, ["shell", "su", "-c", f"rm {remote_tmp}"])
        hero_str = "+".join(ranger_list)
        final_path = os.path.join(local_path, f"{uid}_{hero_str}.xml")
        os.rename(local_tmp, final_path)
        log_msg(serial, f"檔案已儲存為 {final_path}")
        return True
    else:
        log_msg(serial, f"拉取失敗: {result.stderr.strip()}")
        return False

def get_clipboard_text(serial: str, cooldown: float = 1.5) -> str:
    time.sleep(cooldown)

    try:
        return subprocess.check_output("powershell Get-Clipboard", universal_newlines=True).strip()
    except Exception as e:
        print(f"無法讀取剪貼簿：{e}")
        return "unknown_uid"

def clear_game_storage(serial: str):
    log_msg(serial, f"清除 {PACKAGE_NAME} 的儲存空間")

    result = adb_cmd(serial, ["shell", "pm", "clear", PACKAGE_NAME])
    if result.returncode == 0 and "Success" in result.stdout:
        log_msg(serial, "成功清除儲存空間")
    else:
        log_msg(serial, f"清除失敗：{result.stderr.strip()}")

def open_external_url(serial: str, url: str, wait_time: float = 3.0):
    log_msg(serial, f"嘗試開啟外部網址：{url}")
    result = adb_cmd(serial, [
        "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url
    ])

    if result.returncode == 0:
        log_msg(serial, f"已成功打開網址 {url}")
        time.sleep(wait_time)
        return True
    else:
        log_msg(serial, f"打開網址失敗：{result.stderr.strip()}")
        return False
