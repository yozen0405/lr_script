import os
import threading
import time
import zipfile
import shutil
import glob
import subprocess
from typing import Optional, List, Dict
from dataclasses import dataclass
from core.system.adb import adb_cmd
from core.system.logging.logger import log_msg
from core.env.exceptions import ModFrameworkError
from core.base.exceptions import AdbError

@dataclass
class GameConfig:
    PACKAGE_NAME: str = "com.linecorp.LGRGS"
    BINARY_NAME: str = "lrg"
    LOCAL_BIN_PATH: str = os.path.join("bin", "tmp", "lrg")
    LOCAL_MOD_APK_PATH: str = os.path.join("bin", "game", "mod.apk")
    LOCAL_XAPK_PATH: str = os.path.join("bin", "game", "game.apks")
    REMOTE_TMP_PATH: str = "/data/local/tmp"
    REMOTE_BINARY: str = f"{REMOTE_TMP_PATH}/{BINARY_NAME}"
    INTERNAL_BINARY_PATH: str = "assets/CPP/lrg"

MODES_CONFIG = {
    "main_stage": ["strongAtk", "noCooldown", "killEnemie", "speedX4"],
    "guild_raid": ["strongAtk", "noCooldown", "speedX4"],
    "advent": ["strongAtk", "noCooldown", "speedX4"],
    "tower_normal": ["strongAtk", "tower", "killEnemie", "speedX4"],
    "tower_boss": ["strongAtk", "tower", "speedX2"],
    "special_stage": ["strongAtk", "noCooldown", "killEnemie", "speedX4"],
    "pvp": ["tower", "rocket", "report", "killEnemie", "speedX4"],
    "pre_stage": ["speedX2"],
    "train": ["speedX6"],
    "nc": ["noCooldown"],
    "ka": ["killEnemie"],
    "tw": ["tower"],
    "a1": ["a1"],
    "speedx2": ["speedX2"],
    "speedx4": ["speedX4"],
    "speedx6": ["speedX6"],
}

class EnvironmentManager:
    def __init__(self, serial: str, config: GameConfig = GameConfig()):
        self.serial = serial
        self.cfg = config
        self.base_dir: Optional[str] = None
        self.split_apks: Dict[str, str] = {} 

    def _shell(self, cmd: str, use_su: bool = False, silent: bool = True) -> str:
        final_cmd = f"su -c '{cmd}'" if use_su else cmd
        res = adb_cmd(self.serial, ["shell", final_cmd], silent=silent)
        return res.stdout.strip() if res and res.stdout else ""

    def initialize(self):
        if not self._check_root_access():
            raise ModFrameworkError("設備未 Root 或無法授予 su 權限")

        try:
            self._check_game_integrity()
        except ModFrameworkError as e:
            log_msg(self.serial, f"檢測到環境異常: {e}")
            log_msg(self.serial, "啟動自動修復程序: 重裝遊戲...")
            self._reinstall_game()
            self._check_game_integrity()

        if not self._ensure_libs_extracted("armeabi-v7a"):
            raise ModFrameworkError("Libs 初始化失敗，無法從 APK 提取 .so 檔")

        if not self._ensure_binary_installed():
            raise ModFrameworkError("Binary 推送失敗或權限設定錯誤")

        log_msg(self.serial, "環境初始化完成")

    def _check_root_access(self) -> bool:
        output = self._shell("id", use_su=True, silent=True)
        
        if "uid=0(root)" in output.lower():
            return True
            
        log_msg(self.serial, "檢測失敗: 無法取得 Root 權限")
        return False

    def _check_game_integrity(self):
        self.base_dir = None
        self.split_apks = {}

        if not self._parse_game_paths():
            raise ModFrameworkError(f"未安裝遊戲: {self.cfg.PACKAGE_NAME}")

        if "armeabi-v7a" not in self.split_apks:
            raise ModFrameworkError(f"偵測不到 armeabi-v7a 架構，當前架構可能為純 64-bit")

    def _reinstall_game(self):
        """ 解除安裝並重新安裝本地的 XAPK """
        xapk_path = self.cfg.LOCAL_XAPK_PATH
        if not os.path.exists(xapk_path):
            raise ModFrameworkError(f"找不到本地安裝檔: {xapk_path}")

        log_msg(self.serial, f"正在解除安裝: {self.cfg.PACKAGE_NAME}")
        try:
            self._shell(f"pm uninstall {self.cfg.PACKAGE_NAME}")
        except AdbError:
            pass

        safe_serial = self.serial.replace(":", "_").replace(".", "_")
        tmp_extract_dir = os.path.join("bin", "tmp", f"xapk_{safe_serial}")
        if os.path.exists(tmp_extract_dir):
            shutil.rmtree(tmp_extract_dir)
        os.makedirs(tmp_extract_dir)

        try:
            log_msg(self.serial, "正在解壓縮 XAPK...")
            with zipfile.ZipFile(xapk_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_extract_dir)

            apk_files = glob.glob(os.path.join(tmp_extract_dir, "*.apk"))
            if not apk_files:
                raise ModFrameworkError("XAPK 解壓後找不到任何 .apk 檔案")

            log_msg(self.serial, f"正在安裝 {len(apk_files)} 個 APK 檔案...")
            
            install_args = ["install-multiple", "-r"] + apk_files
            
            adb_cmd(self.serial, install_args, timeout=300, silent=False)
            log_msg(self.serial, "安裝成功！")

        finally:
            if os.path.exists(tmp_extract_dir):
                shutil.rmtree(tmp_extract_dir)

    def _parse_game_paths(self) -> bool:
        try:
            output = self._shell(f"pm path {self.cfg.PACKAGE_NAME}")
            if not output:
                return False
        except AdbError:
            return False

        for line in output.splitlines():
            path = line.replace("package:", "").strip()
            if not path: continue
            if not self.base_dir:
                self.base_dir = os.path.dirname(path)
            
            if "split_config.armeabi_v7a.apk" in path:
                self.split_apks["armeabi-v7a"] = path
            elif "split_config.arm64_v8a.apk" in path:
                self.split_apks["arm64-v8a"] = path
        
        return bool(self.base_dir)

    def _ensure_libs_extracted(self, arch: str) -> bool:
        if not self.base_dir: return False
        target_lib_folder_name = "arm" if arch == "armeabi-v7a" else "arm64"
        
        dst_dir = f"{self.base_dir}/lib/{target_lib_folder_name}"
        apk_path = self.split_apks.get(arch)

        if not apk_path:
            return False

        try:
            check_res = adb_cmd(self.serial, ["shell", f"ls {dst_dir}/*.so"], silent=True)
            if check_res.returncode == 0 and ".so" in check_res.stdout:
                return True
        except Exception:
            pass

        log_msg(self.serial, f"Lib check: {arch} 缺失，從 APK 解壓...")
        
        tmp_unzip_path = "/sdcard/tmp_so_extract"
        self._shell(f"rm -rf {tmp_unzip_path}", use_su=True)
        self._shell(f"mkdir -p {tmp_unzip_path}", use_su=True)
        self._shell(f"unzip -o {apk_path} -d {tmp_unzip_path}", use_su=True)

        src_lib_path = f"{tmp_unzip_path}/lib/{arch}"
        
        self._shell(f"mkdir -p {dst_dir}", use_su=True)
        self._shell(f"cp {src_lib_path}/*.so {dst_dir}/", use_su=True)
        self._shell(f"chmod 755 {dst_dir}/*.so", use_su=True)
        self._shell(f"rm -rf {tmp_unzip_path}", use_su=True)
        
        final_check = self._shell(f"ls {dst_dir}/*.so 2>/dev/null", use_su=True)
        return ".so" in final_check

    def _extract_binary_from_mod_apk(self):
        apk_path = self.cfg.LOCAL_MOD_APK_PATH
        target_bin_path = self.cfg.LOCAL_BIN_PATH
        internal_path = self.cfg.INTERNAL_BINARY_PATH

        if not os.path.exists(apk_path):
            raise ModFrameworkError(f"找不到 Mod APK 檔案: {apk_path}")

        try:
            os.makedirs(os.path.dirname(target_bin_path), exist_ok=True)

            # log_msg(self.serial, f"正在從 Mod APK 提取 binary ({internal_path})...")
            
            with zipfile.ZipFile(apk_path, 'r') as z:
                if internal_path not in z.namelist():
                    possible_matches = [n for n in z.namelist() if "lrg" in n and "CPP" in n]
                    if not possible_matches:
                        raise ModFrameworkError(f"Mod APK 中找不到 {internal_path}")
                    internal_path = possible_matches[0]

                with z.open(internal_path) as source, open(target_bin_path, "wb") as target:
                    shutil.copyfileobj(source, target)
                
            # log_msg(self.serial, f"Binary 提取成功: {target_bin_path}")

        except zipfile.BadZipFile:
            raise ModFrameworkError(f"Mod APK 檔案損毀，無法讀取: {apk_path}")
        except Exception as e:
            raise ModFrameworkError(f"提取 Binary 失敗: {str(e)}")

    def _ensure_binary_installed(self) -> bool:
        local_path = self.cfg.LOCAL_BIN_PATH
        remote_path = self.cfg.REMOTE_BINARY

        try:
            self._extract_binary_from_mod_apk()

            if not os.path.exists(local_path):
                raise ModFrameworkError(f"無法產生本地 Binary: {local_path}")

            adb_cmd(self.serial, ["push", local_path, remote_path], timeout=60, silent=True)

            self._shell(f"chmod 777 {remote_path}", use_su=True)
            
            check = self._shell(f"ls {remote_path}", use_su=True)
            return self.cfg.BINARY_NAME in check

        finally:
            if os.path.exists(local_path):
                os.remove(local_path)


class ModController(EnvironmentManager):
    def __init__(self, serial: str):
        super().__init__(serial)
        self._lock = threading.Lock()

    def ensure_ready(self):
        with self._lock:
            self.initialize()

    def _run_lrg_cmd(self, *args: str):
        args_str = " ".join(args)
        cmd = f"{self.cfg.REMOTE_BINARY} {args_str}"
        log_msg(self.serial, f"執行: {cmd}")
        
        self._shell(cmd, use_su=True)

    def toggle(self, member_id: str, state: str):
        if state not in ["on", "off"]:
            log_msg(self.serial, f"狀態錯誤: {state}")
            return
        self._run_lrg_cmd(member_id, state, "1")

    def apply_mode(self, mode_name: str, state: str = "on"):
        if mode_name not in MODES_CONFIG:
            log_msg(self.serial, f"未知模式: {mode_name}")
            return

        log_msg(self.serial, f"套用模式: {mode_name} -> {state}")
        members = MODES_CONFIG[mode_name]
        for member in members:
            self.toggle(member, state)

_controllers: Dict[str, ModController] = {}

def get_controller(serial: str) -> ModController:
    if serial not in _controllers:
        _controllers[serial] = ModController(serial)
    return _controllers[serial]

def initialize_environment(serial: str) -> bool:
    return get_controller(serial).ensure_ready()

def apply_mode(serial: str, mode_name: str, state: str):
    get_controller(serial).apply_mode(mode_name, state)