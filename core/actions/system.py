import time
from core.system.adb import adb_cmd
from core.system.logger import log_msg
import os
import subprocess

SIMILARITY=0.7
CHECK_INTERVAL=0.5
PACKAGE_NAME = "com.linecorp.LGRGS"
MAIN_ACTIVITY = "com.linecorp.LGRGS.LineRangersAdr"

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
