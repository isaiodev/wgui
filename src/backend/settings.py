import json
from pathlib import Path
from src.utils.paths import get_config_dir

class SettingsManager:
    def __init__(self):
        self.config_dir = get_config_dir()
        self.settings_file = self.config_dir / "settings.json"
        self.default_settings = {
            "start_on_boot": False,
            "kill_switch": False,
            "dns_override": "",
            "language": "en_US"
        }
        self.settings = self.load_settings()

    def load_settings(self) -> dict:
        if not self.settings_file.exists():
            return self.default_settings.copy()

        try:
            with open(self.settings_file, "r") as f:
                return json.load(f)
        except Exception:
            return self.default_settings.copy()

    def save_settings(self):
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception:
            pass

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
