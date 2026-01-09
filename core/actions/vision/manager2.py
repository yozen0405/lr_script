import os
import cv2
import time
import numpy as np
import threading
from typing import Dict, Optional, Tuple, Union
from core.system.adb import adb_cmd
from core.system.logging.logger import log_msg
import uiautomator2 as u2
import atexit
import concurrent.futures
from core.base.exceptions import FatalError, AdbError

IMG_DIR = os.path.join("bin", "img")

SIMILARITY = 0.7
CHECK_INTERVAL = 0.3
GAME_PACKAGE = "com.linecorp.LGRGS"

# ==============================================================================
# 1. Template Cache Layer (必要！這是所有 Serial 共用的資源)
# ==============================================================================
class TemplateCache:
    """
    靜態快取層：負責將硬碟的圖片讀入 RAM。
    因為所有模擬器用的圖片都一樣，所以只要一份 Cache 就夠了。
    """
    _cache: Dict[str, np.ndarray] = {}
    _lock = threading.Lock() # 確保多執行緒同時讀取時不會打架

    @classmethod
    def get(cls, image_name: str) -> Optional[np.ndarray]:
        # 先檢查記憶體有沒有
        if image_name in cls._cache:
            return cls._cache[image_name]

        # 記憶體沒有，才去讀硬碟 (加鎖防止重複讀取)
        with cls._lock:
            if image_name in cls._cache:
                return cls._cache[image_name]

            path = os.path.join(IMG_DIR, image_name)
            if not os.path.exists(path):
                # log_msg("SYSTEM", f"⚠️ 找不到資源圖片: {path}") # 視需求開啟
                raise FatalError(f"找不到資源圖片: {path}")
            
            # 讀取並存入 Cache
            img = cv2.imread(path, cv2.IMREAD_COLOR)
            if img is not None:
                cls._cache[image_name] = img
                return img
            
            return None

# ==============================================================================
# 2. Vision Manager (Serial Singleton 核心邏輯)
# ==============================================================================
class VisionManager:
    """
    每個 Serial 擁有一份獨立的 Manager 實例。
    負責該 Serial 的截圖與邏輯判斷。
    """
    def __init__(self, serial: str):
        self.serial = serial
        self.default_threshold = 0.7

        self._last_freeze_frame = None
        self._last_freeze_time = 0
        self._click_history: Dict[str, float] = {}

        self.d = u2.connect(serial)
        self.d.implicitly_wait(0.0)

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        atexit.register(self.close)

    def close(self):
        self.executor.shutdown(wait=False)

    def _capture_screen_fast(self):
        return self.d.screenshot(format='opencv')

    def _capture_screen_fallback(self):
        try:
            result = adb_cmd(
                self.serial, 
                ["exec-out", "screencap", "-p"], 
                timeout=3,
                silent=True, 
                binary=True
            )

            if not result or not result.stdout:
                return None

            image_buffer = np.frombuffer(result.stdout, np.uint8)
            return cv2.imdecode(image_buffer, cv2.IMREAD_COLOR)

        except Exception as e:
            log_msg(self.serial, f"ADB 備援截圖也失敗: {e}")
            return None
        
    def _connect_worker(self):
        d = u2.connect(self.serial)
        d.implicitly_wait(0.0)
        return d

    def _reconnect_u2(self):
        log_msg(self.serial, "偵測到連線中斷，嘗試重新連接 u2...")
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as temp_executor:
                future = temp_executor.submit(self._connect_worker)
                
                self.d = future.result(timeout=5.0)
                
            log_msg(self.serial, "u2 重新連接成功！")

        except concurrent.futures.TimeoutError:
            log_msg(self.serial, "u2 重連超時 (5s)，放棄重連，繼續使用 ADB 備援")
        except Exception as reconnect_err:
            log_msg(self.serial, f"u2 重連失敗: {reconnect_err}")

    def _capture_screen(self):
        try:
            future = self.executor.submit(self._capture_screen_fast)
            image = future.result(timeout=3.0)
            if image is not None:
                return image
            
        except KeyboardInterrupt:
            raise
                
        except (concurrent.futures.TimeoutError, Exception) as e:
            log_msg(self.serial, f"高速截圖失效 ({e})，切換至 ADB 備援模式...")
            self._reconnect_u2()

        image = self._capture_screen_fallback()
        
        if image is not None:
            return image

        log_msg(self.serial, "所有截圖手段皆失效")
        raise AdbError("截圖超時，與模擬器連線不穩")

    # --------------------------------------------------------------------------
    # 核心辨識功能 (Core Vision)
    # --------------------------------------------------------------------------
    
    def find_pos(self, image_name: str, threshold=None, region=None, return_center=True) -> Optional[Union[Tuple[int, int], Tuple[int, int, int, int]]]:
        thresh = threshold or self.default_threshold
        
        screen = self._capture_screen()
        if screen is None: return None

        template = TemplateCache.get(image_name)
        if template is None: return None

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

            log_msg(self.serial, f"{max_val} >= {thresh}, region={region}" if region else f"{max_val} >= {thresh}")

            if max_val >= thresh:
                h_t, w_t = template.shape[:2]
                
                if return_center:
                    center_x = max_loc[0] + offset_x + w_t // 2
                    center_y = max_loc[1] + offset_y + h_t // 2
                    return (center_x, center_y)
                else:
                    x1 = max_loc[0] + offset_x
                    y1 = max_loc[1] + offset_y
                    return (x1, y1, x1 + w_t, y1 + h_t)
        except Exception:
            pass

        return None

    # --------------------------------------------------------------------------
    # 進階視覺功能 (Advanced Vision Features)
    # --------------------------------------------------------------------------

    def check_freeze(self, threshold=0.999, reset_time=600.0, timeout=120.0) -> bool:
        current_frame = self._capture_screen()
        if current_frame is None:
            return False

        now = time.time()

        if self._last_freeze_frame is None or (now - self._last_freeze_time > reset_time):
            self._last_freeze_frame = current_frame
            self._last_freeze_time = now
            return False

        if (now - self._last_freeze_time) < timeout:
            return False

        try:
            img_cur_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
            img_old_gray = cv2.cvtColor(self._last_freeze_frame, cv2.COLOR_BGR2GRAY)

            res = cv2.matchTemplate(img_cur_gray, img_old_gray, cv2.TM_CCOEFF_NORMED)
            similarity = res[0][0]

            self._last_freeze_frame = current_frame
            self._last_freeze_time = now

            if similarity >= threshold:
                log_msg(self.serial, f"檢測到畫面凍結 (相似度: {similarity:.4f})")
                return True
            else:
                return False

        except Exception as e:
            log_msg(self.serial, f"Freeze Check Error: {e}")
            self._last_freeze_frame = current_frame
            return False

    def find_spotlight_center(self, region=None) -> Optional[Tuple[int, int]]:
        img = self._capture_screen()
        if img is None: return None

        offset_x, offset_y = 0, 0
        if region:
            x1, y1, x2, y2 = region
            img = img[y1:y2, x1:x2]
            offset_x, offset_y = x1, y1

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (51, 51), 0)
        
        _, max_val, _, max_loc = cv2.minMaxLoc(blurred)

        if max_val < 50:
            # log_msg(self.serial, f"未偵測到明顯亮區 (Max: {max_val})")
            return None

        final_loc = (max_loc[0] + offset_x, max_loc[1] + offset_y)
        # log_msg(self.serial, f"找到亮區中心: {final_loc}, 亮度: {max_val}")
        return final_loc

    def check_region_brightness(self, region: Tuple[int, int, int, int], threshold=20) -> bool:
        """檢查指定區域平均亮度"""
        img = self._capture_screen()
        if img is None: return False

        x1, y1, x2, y2 = region
        roi = img[y1:y2, x1:x2]

        if roi.size == 0:
            return False

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        avg_brightness = cv2.mean(gray)[0]

        log_msg(self.serial, f"區域亮度: {avg_brightness:.2f} (閾值: {threshold})")
        return avg_brightness > threshold

    def save_screenshot(self, save_path: str):
        """將當前畫面存檔"""
        img = self._capture_screen()
        if img is not None:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cv2.imwrite(save_path, img)

    def click(self, x: int, y: int) -> bool:
        try:
            self.d.click(x, y)
        except Exception:
            adb_cmd(self.serial, ["shell", "input", "tap", str(x), str(y)], silent=True)

    def get_app_current(self) -> Dict[str, str]:
        """
        獲取當前前台的 App 資訊。
        Return: {'package':Str, 'activity':Str, 'pid':Int}
        """
        try:
            return self.d.app_current()
        except Exception as e:
            return {'package': None, 'activity': None}
            
    
_instances: Dict[str, VisionManager] = {}

def get_manager(serial: str) -> VisionManager:
    if serial not in _instances:
        _instances[serial] = VisionManager(serial)
    return _instances[serial]

def get_pos(serial: str, image_name: str, threshold=SIMILARITY, region=None, return_center=True) -> Optional[Tuple[int, int]]:
    """保留舊接口：尋找座標並 Log"""
    if region is not None:
        assert isinstance(region, tuple) and len(region) == 4, "region 需為 (x1, y1, x2, y2)"
    
    pos = get_manager(serial).find_pos(image_name, threshold, region, return_center)
    if pos:
        log_msg(serial, f"找到 {image_name}，座標: {pos}" + (f"，region={region}" if region else ""))
    else:
        log_msg(serial, f"找不到 {image_name}" + (f"，region={region}" if region else ""))
    return pos

def exist(serial: str, image_name: str, threshold=SIMILARITY, wait_time=0.0, region=None) -> bool:
    if get_manager(serial).find_pos(image_name, threshold, region):
        log_msg(serial, f"找到 {image_name}")
        if wait_time > 0: time.sleep(wait_time)
        return True
    log_msg(serial, f"未找到 {image_name}")
    return False

def exist_click(serial: str, image_name: str, threshold=SIMILARITY, wait_time=0.0, region=None) -> bool:
    mgr = get_manager(serial)
    pos = mgr.find_pos(image_name, threshold, region)
    if pos:
        mgr.click(pos[0], pos[1])
        log_msg(serial, f"找到 {image_name}，點擊 {pos}")
        if wait_time > 0: time.sleep(wait_time)
        return True
    log_msg(serial, f"未找到 {image_name}")
    return False

def wait(serial: str, image_name: str, threshold=SIMILARITY, timeout=5.0, wait_time=0.1, region=None) -> bool:
    mgr = get_manager(serial)
    start_time = time.time()
    while time.time() - start_time < timeout:
        pos = mgr.find_pos(image_name, threshold, region)
        if pos:
            log_msg(serial, f"找到 {image_name}，在 {pos}")
            time.sleep(wait_time)
            return True
        time.sleep(CHECK_INTERVAL)
    
    log_msg(serial, f"超時未找到 {image_name}")
    return False

def wait_click(serial: str, target: Union[str, Tuple[int, int]], 
               threshold=SIMILARITY, timeout=5.0, wait_time=0.5, region=None) -> bool:
    mgr = get_manager(serial)
    if isinstance(target, tuple) and len(target) == 2:
        x, y = target
        mgr.click(x, y)  
        log_msg(serial, f"點擊座標 ({x}, {y})")
        time.sleep(wait_time)
        return True

    elif isinstance(target, str):
        start_time = time.time()
        while time.time() - start_time < timeout:
            pos = mgr.find_pos(target, threshold, region)
            if pos:
                mgr.click(pos[0], pos[1])
                log_msg(serial, f"找到 {target}，點擊 {pos}")
                time.sleep(wait_time)
                return True
            time.sleep(CHECK_INTERVAL)
        
        log_msg(serial, f"超時未找到 {target}")
        return False

    else:
        raise ValueError("wait_click 參數錯誤：需為圖片檔名、(x, y) tuple 或 x, y 座標")

def wait_vanish(serial: str, image_name: str, timeout=10.0, threshold=SIMILARITY, wait_time=0.5) -> bool:
    mgr = get_manager(serial)
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not mgr.find_pos(image_name, threshold):
            log_msg(serial, f"{image_name} 已從畫面中消失")
            time.sleep(wait_time)
            return True
        time.sleep(CHECK_INTERVAL)

    log_msg(serial, f"等待 {image_name} 消失超時")
    return False

def back(serial: str):
    adb_cmd(serial, ["shell", "input", "keyevent", "4"], silent=True)

def drag(serial: str, *args, threshold=0.7, duration=300, wait_time=0.5, timeout=5.0) -> bool:
    """
    支援：
    1. drag(serial, (x1, y1), (x2, y2))
    2. drag(serial, "img1.png", "img2.png")
    """
    if len(args) != 2:
        raise ValueError("drag() 需要兩個參數（兩個座標或兩個圖片名）")

    mgr = get_manager(serial)
    start_time = time.time()
    x1, y1, x2, y2 = 0, 0, 0, 0
    ready = False

    while time.time() - start_time < timeout:
        if isinstance(args[0], tuple) and isinstance(args[1], tuple):
            (x1, y1), (x2, y2) = args
            ready = True
            break
        
        elif isinstance(args[0], str) and isinstance(args[1], str):
            image1, image2 = args
            pos1 = mgr.find_pos(image1, threshold)
            pos2 = mgr.find_pos(image2, threshold)
            
            if pos1 and pos2:
                x1, y1 = pos1
                x2, y2 = pos2
                ready = True
                break
            else:
                time.sleep(CHECK_INTERVAL)
        else:
            raise ValueError("drag() 參數類型錯誤")

    if ready:
        log_msg(serial, f"拖曳從 ({x1}, {y1}) 到 ({x2}, {y2})")
        adb_cmd(serial, ["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)], silent=True)
        time.sleep(wait_time)
        return True
    
    log_msg(serial, "拖曳失敗：找不到目標座標")
    return False

def save_screenshot(serial: str, path: str):
    get_manager(serial).save_screenshot(path)

def check_freeze(serial: str, threshold=0.999, reset_time=600.0, timeout=120.0) -> bool:
    return get_manager(serial).check_freeze(threshold=threshold, reset_time=reset_time, timeout=timeout)

def find_spotlight_center(serial: str, region=None) -> Optional[Tuple[int, int]]:
    return get_manager(serial).find_spotlight_center(region=region)

def check_region_brightness(serial: str, region: Tuple[int, int, int, int], threshold=20) -> bool:
    return get_manager(serial).check_region_brightness(region=region, threshold=threshold)

def is_game_foreground(serial: str) -> bool:
    current = get_manager(serial).get_app_current()
    pkg = current.get('package')
        
    return pkg == GAME_PACKAGE