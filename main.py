from concurrent.futures import ThreadPoolExecutor
from adb_runner import connect_all_mumu_instances
from task_runner import new_acc_farm

if __name__ == "__main__":
    devices = connect_all_mumu_instances()
    print("發現裝置:", devices)

    if not devices:
        print("未偵測到任何裝置，請確認裝置已連接並啟動。")
    else:
        try:
            with ThreadPoolExecutor(max_workers=len(devices)) as executor:
                futures = [executor.submit(new_acc_farm, d) for d in devices]
                for future in futures:
                    future.result()

        except KeyboardInterrupt:
            print("\n偵測到中斷，正在關閉執行緒...")
            executor.shutdown(wait=False, cancel_futures=True)
            print("已停止所有任務。")
