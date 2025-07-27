import os
from adb_runner import adb_cmd

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