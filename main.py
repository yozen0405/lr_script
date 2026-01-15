from concurrent.futures import ThreadPoolExecutor
import os
import signal
import sys
import threading
import time
from core.system.adb import connect_all_mumu_instances
# from scripts.custom_scripts.new_acc_test.base import normal_stage
# from scripts.custom_scripts.fast_acc.sec import normal_stage
from scripts.custom_scripts.pvp_test.main import normal_stage
# from scripts.custom_scripts.test.base import normal_stage

if __name__ == "__main__":    
    try:
        devices = connect_all_mumu_instances(goal=1)

        print("發現裝置:", devices)
        if not devices:
            print("未偵測到任何裝置，請確認裝置已連接並啟動。")
        elif len(devices) == 1:
            print("啟動單機模式")
            normal_stage(devices[0])
        else:
            threads = []
            for d in devices:
                t = threading.Thread(target=normal_stage, args=(d,))
                t.daemon = True 
                t.start()
                threads.append(t)

            
            for t in threads:
                while t.is_alive():
                    t.join(timeout=1)
                    
    except KeyboardInterrupt:
        print("\n所有模擬器將立刻停止！")
        os._exit(0)

