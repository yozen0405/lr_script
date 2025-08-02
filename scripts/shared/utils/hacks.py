from core.system.adb import adb_cmd
from core.system.logger import log_msg
from scripts.shared.utils.retry import liapp_alert

MODES = {
    "main_stage": ["m1", "m2", "m8", "m10"],
    "pre_stage": ["m10"]
}


class BaseToggleCommand:
    def __init__(self, serial: str, binary_name: str):
        self.serial = serial
        self.binary_name = binary_name

    def run_command(self, *args: str):
        cmd = f"/data/local/tmp/{self.binary_name} " + " ".join(args)
        log_msg(self.serial, f"執行指令: {cmd}")
        return adb_cmd(self.serial, ["shell", f"su -c '{cmd}'"])

class ModManager(BaseToggleCommand):
    def __init__(self, serial: str):
        super().__init__(serial, "toggle_kong")

    def toggle_member(self, member_id: str, state: str):
        assert state in ["on", "off"], f"狀態必須為 'on' 或 'off'"
        return self.run_command(member_id, state, "1")

_instance_cache = {}

def toggle(serial: str, member_id: str, state: str):
    if serial not in _instance_cache:
        _instance_cache[serial] = ModManager(serial)
    return _instance_cache[serial].toggle_member(member_id, state)

def apply_mode(serial: str, mode_name: str, flag: bool, esc: bool = True):
    members = MODES.get(mode_name)
    if members is None:
        raise ValueError(f"模式「{mode_name}」不存在")

    log_msg(serial, f"套用模式：{mode_name}({'開啟' if flag else '關閉'})")
    state = "on" if flag else "off"
    for member_id in members:
        toggle(serial, member_id, state)
    # liapp_alert(serial, esc)
