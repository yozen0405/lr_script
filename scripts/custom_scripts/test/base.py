# from core.actions.vision.manager import exist
from core.actions.vision import VisionManager
import time

def normal_stage(serial):
    # 初始化 (這一步會花幾秒鐘建立連線)
    vm = VisionManager("127.0.0.1:16480") 

    start_time = time.time()
    
    # 連續抓 10 次圖
    for i in range(10):
        img = vm._capture_screen()
        # 這裡可以假裝做一點事，比如 img.shape
        if img is not None:
            _ = img.shape
            
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = (total_time / 10) * 1000

    print(f"跑了 10 次截圖")
    print(f"總耗時: {total_time:.4f} 秒")
    print(f"平均每次耗時: {avg_time:.2f} ms")