import os
import sys
import platform
from pathlib import Path
from platformdirs import user_config_dir, user_data_dir

APP_NAME = "WireGuardGUI"
APP_AUTHOR = "OpenSource"

def get_config_dir() -> Path:
    """Returns the configuration directory for the application."""
    path = Path(user_config_dir(APP_NAME, APP_AUTHOR))
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_profiles_dir() -> Path:
    """Returns the directory where WireGuard profiles are stored."""
    if platform.system() == "Windows":
        # On Windows, we might want to store it in a restricted folder or standard AppData
        path = Path(user_data_dir(APP_NAME, APP_AUTHOR)) / "profiles"
    else:
        # On Linux, strictly user config
        path = Path(user_config_dir(APP_NAME, APP_AUTHOR)) / "profiles"

    path.mkdir(parents=True, exist_ok=True)
    return path

def get_assets_dir() -> Path:
    """Returns the assets directory."""
    # Assuming assets are in the root of the repo relative to this file
    # src/utils/paths.py -> assets/
    base_dir = Path(__file__).parent.parent.parent
    return base_dir / "assets"
