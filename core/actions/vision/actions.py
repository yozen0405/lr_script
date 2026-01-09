from difflib import SequenceMatcher
import os
import cv2
import time
from typing import Union, Tuple, Optional, List
from core.system.logging.logger import log_msg
from .manager import VisionManager
from .config import DEFAULT_THRESHOLD, CHECK_INTERVAL, GAME_PACKAGE, TMP_DIR

# ============================
# 基礎查找與點擊 (Basic)
# ============================

def get_pos(
    serial: str, 
    image_name: str, 
    threshold=DEFAULT_THRESHOLD, 
    region=None, 
    return_center=True
) -> Optional[Union[Tuple[int, int], Tuple[int, int, int, int]]]:
    pos = VisionManager.get(serial).find(image_name, threshold, region, return_center)
    
    if pos:
        log_msg(serial, f"找到 {image_name}，座標: {pos}" + (f"，region={region}" if region else ""))
    else:
        log_msg(serial, f"找不到 {image_name}" + (f"，region={region}" if region else ""))
        
    return pos

def get_all_pos(
    serial: str, 
    image_name: str, 
    threshold=DEFAULT_THRESHOLD, 
    region=None, 
    return_center=True
) -> List[Union[Tuple[int, int], Tuple[int, int, int, int]]]:
    results = VisionManager.get(serial).find_all(image_name, threshold, region, return_center)
    
    if results:
        log_msg(serial, f"找到 {len(results)} 個 {image_name}，座標: {results}" + (f"，region={region}" if region else ""))
    else:
        log_msg(serial, f"找不到任何 {image_name}" + (f"，region={region}" if region else ""))
        
    return results

def exist(serial: str, image_name: str, threshold=DEFAULT_THRESHOLD, wait_time=0.0, region=None) -> bool:
    pos = VisionManager.get(serial).find(image_name, threshold, region)
    if pos:
        log_msg(serial, f"找到 {image_name}，座標: {pos}")
        if wait_time > 0: time.sleep(wait_time)
        return True
    log_msg(serial, f"未找到 {image_name}")
    return False

def exist_click(serial: str, image_name: str, threshold=DEFAULT_THRESHOLD, wait_time=0.0, region=None) -> bool:
    mgr = VisionManager.get(serial)
    pos = mgr.find(image_name, threshold, region)
    if pos:
        mgr.device.click(*pos)
        log_msg(serial, f"點擊 {image_name}，點擊 {pos}")
        if wait_time > 0: time.sleep(wait_time)
        return True
    log_msg(serial, f"未找到 {image_name}")
    return False

def wait(serial: str, image_name: str, threshold=DEFAULT_THRESHOLD, timeout=5.0, wait_time=0.1, region=None) -> bool:
    mgr = VisionManager.get(serial)
    start_time = time.time()
    while time.time() - start_time < timeout:
        pos = mgr.find(image_name, threshold, region)
        if pos:
            log_msg(serial, f"找到 {image_name}，在 {pos}")
            if wait_time > 0: time.sleep(wait_time)
            return True
        time.sleep(CHECK_INTERVAL)
    
    log_msg(serial, f"超時未找到 {image_name}")
    return False

def wait_click(serial: str, target: Union[str, Tuple[int, int]], 
               threshold=DEFAULT_THRESHOLD, timeout=5.0, wait_time=0.5, region=None) -> bool:
    mgr = VisionManager.get(serial)
    
    if isinstance(target, tuple):
        mgr.device.click(*target)
        log_msg(serial, f"點擊座標 ({target[0]}, {target[1]})")
        time.sleep(wait_time)
        return True

    start_time = time.time()
    while time.time() - start_time < timeout:
        pos = mgr.find(target, threshold, region)
        if pos:
            mgr.device.click(*pos)
            log_msg(serial, f"找到 {target}，點擊 {pos}")
            time.sleep(wait_time)
            return True
        time.sleep(CHECK_INTERVAL)
    
    log_msg(serial, f"超時未找到 {target}")
    return False

def wait_vanish(serial: str, image_name: str, threshold=DEFAULT_THRESHOLD, timeout=10.0, wait_time=0.5) -> bool:
    mgr = VisionManager.get(serial)
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if not mgr.find(image_name, threshold):
            log_msg(serial, f"{image_name} 已消失")
            if wait_time > 0: time.sleep(wait_time)
            return True
        time.sleep(CHECK_INTERVAL)

    log_msg(serial, f"等待 {image_name} 消失超時")
    return False

# ============================
# 操作與狀態 (Action & State)
# ============================

def drag(serial: str, start: Union[Tuple[int,int], str], end: Union[Tuple[int,int], str], duration=300, wait_time=0.5) -> bool:
    mgr = VisionManager.get(serial)
    
    def resolve_pos(target):
        if isinstance(target, tuple): return target
        return mgr.find(target)

    p1 = resolve_pos(start)
    p2 = resolve_pos(end)

    if p1 and p2:
        mgr.device.drag(p1[0], p1[1], p2[0], p2[1], duration)
        log_msg(serial, f"拖曳從 ({p1[0]}, {p1[1]}) 到 ({p2[0]}, {p2[1]})")
        time.sleep(wait_time)
        return True
    
    return False

def back(serial: str):
    VisionManager.get(serial).device.input_keyevent(4) 

def is_game_foreground(serial: str) -> bool:
    app_info = VisionManager.get(serial).device.get_current_app()
    return app_info.get('package') == GAME_PACKAGE

def check_freeze(serial: str, threshold=0.999, reset_time=600.0, timeout=120.0) -> bool:
    return VisionManager.get(serial).check_freeze(threshold, reset_time, timeout)

def save_screenshot(serial: str, path: str, region: Optional[Tuple[int, int, int, int]] = None):
    img = VisionManager.get(serial).capture(region)
    if img is not None:
        directory = os.path.dirname(path)
        
        if directory:
            os.makedirs(directory, exist_ok=True)
        else:
            path = os.path.join(TMP_DIR, path)

        cv2.imwrite(path, img)
        # log_msg(serial, f"截圖已儲存至: {path}")

def check_region_brightness(serial: str, region: Tuple[int, int, int, int], threshold=20) -> bool:
    return VisionManager.get(serial).check_region_brightness(region, threshold)

def find_spotlight_center(serial: str, region=None) -> Optional[Tuple[int, int]]:
    return VisionManager.get(serial).find_spotlight_center(region)
