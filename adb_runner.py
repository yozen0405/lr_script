import subprocess
import os
import json

ADB_PATH = os.path.join("bin", "adb", "adb.exe")
CACHE_FILE = os.path.join("bin", "cache.json")

def try_adb_connect(port):
    address = f"127.0.0.1:{port}"
    try:
        result = subprocess.check_output([ADB_PATH, "connect", address], stderr=subprocess.STDOUT)
        return b"connected" in result or b"already connected" in result
    except subprocess.CalledProcessError:
        return False

def get_adb_devices():
    result = subprocess.run(
        [ADB_PATH, "devices"],
        capture_output=True,
        text=True
    )
    lines = result.stdout.strip().splitlines()[1:]
    return set(line.split()[0] for line in lines if "\tdevice" in line)

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_cache(connected_list):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(connected_list, f, ensure_ascii=False, indent=2)
        
def connect_all_mumu_instances(goal=1, max_attempts=10, base_port=16384):
    print(f"目標連線數: {goal}，最多嘗試組數: {max_attempts}")

    cached_ports = load_cache()
    current_devices = get_adb_devices()
    final_connected = []

    for addr in cached_ports:
        if addr in current_devices:
            print(f"快取中已在線: {addr}")
            final_connected.append(addr)
            if len(final_connected) >= goal:
                print("已達成目標，停止掃描")
                save_cache(final_connected)
                return final_connected

    for i in range(max_attempts):
        if i == 0:
            ports_to_try = [base_port, base_port + 1]
        else:
            ports_to_try = [base_port + i * 32]

        for port in ports_to_try:
            addr = f"127.0.0.1:{port}"
            if addr in final_connected:
                continue

            print(f"嘗試連線: {addr}...")
            if addr in current_devices:
                print(f"已在線: {addr}")
                final_connected.append(addr)
            elif try_adb_connect(port):
                print(f"連線成功: {addr}")
                final_connected.append(addr)
            else:
                print(f"連線失敗: {addr}")

            if len(final_connected) >= goal:
                print("已達成目標，停止掃描")
                save_cache(final_connected)
                return final_connected

    print(f"未達成目標，但已完成所有嘗試，共連線: {len(final_connected)} 台")
    save_cache(final_connected)
    return final_connected

def adb_cmd(serial, args):
    result = subprocess.run([ADB_PATH, "-s", serial] + args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠️ ADB 執行錯誤：{' '.join(args)}")
        print(f"stderr: {result.stderr.strip()}")
    return result
