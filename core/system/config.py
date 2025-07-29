# core/system/config.py
from configparser import ConfigParser
import os

class Config:
    _instance = None

    def __new__(cls, config_path="./bin/config.ini"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_config(config_path)
        return cls._instance

    def _init_config(self, config_path):
        self.config_path = config_path
        if not os.path.isfile(self.config_path):
            raise FileNotFoundError(f"找不到設定檔: {self.config_path}")

        self._config = ConfigParser()
        self._config.read(self.config_path, encoding="utf-8")
        self.settings = dict(self._config["SETTINGS"]) if "SETTINGS" in self._config else {}

        self._bool_keys = {"single_mode"}
        self._int_keys = {"herowant"}

        self.target_count, self.expected_names, self.name_map = self._parse_gacha_settings()

    def get(self, key, fallback=None):
        if key not in self.settings:
            return fallback
        value = self.settings[key]

        if key in self._bool_keys:
            return value.lower() in ("1", "true", "yes", "on")
        if key in self._int_keys:
            try:
                return int(value)
            except ValueError:
                return fallback
        return value

    def is_single_mode(self):
        return self.get("single_mode", fallback=True)

    def _parse_gacha_settings(self):
        target_count = self.get("herowant", fallback=1)
        expected_names = []
        name_map = {}

        for key, raw in self.settings.items():
            if key.startswith("name"):
                try:
                    candidates, display_name = raw.split("=")
                    full_name = " ".join(candidates.split("+"))
                    expected_names.append(full_name)
                    name_map[full_name] = display_name
                except ValueError:
                    print(f"[WARNING] 無法解析設定 `{key}={raw}`，格式應為 A+B=Nickname")
                    continue

        return target_count, expected_names, name_map
