from concurrent.futures import ThreadPoolExecutor
from core.system.adb import connect_all_mumu_instances
# from scripts.custom_scripts.new_acc.main import new_acc_farm
# from scripts.custom_scripts.main_stage_test.main import normal_stage
# from scripts.custom_scripts.special_stage_test.main import normal_stage
from scripts.custom_scripts.pvp_test.main import normal_stage

from core.system.config import Config

if __name__ == "__main__":
    cfg = Config()
    single_mode = cfg.is_single_mode()
    devices = connect_all_mumu_instances(goal=1)

    print("發現裝置:", devices)
    if not devices:
        print("未偵測到任何裝置，請確認裝置已連接並啟動。")

    elif single_mode:
        print("啟動單機模式")
        normal_stage(devices[0])

    else:
        print("啟動多執行緒模式")
        try:
            with ThreadPoolExecutor(max_workers=len(devices)) as executor:
                futures = [executor.submit(normal_stage, d) for d in devices]
                for future in futures:
                    future.result()

        except KeyboardInterrupt:
            print("\n偵測到中斷，正在關閉執行緒...")
            executor.shutdown(wait=False, cancel_futures=True)
            print("已停止所有任務。")
