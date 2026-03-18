import json
import os
import sys
from pathlib import Path


def _config_dir() -> Path:
    """Returns the FarmDash config directory, creating it if needed.

    Windows : %LOCALAPPDATA%\\FarmDash
    macOS   : ~/.config/FarmDash
    Linux   : $XDG_CONFIG_HOME/FarmDash  (fallback: ~/.config/FarmDash)
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    config_dir = base / "FarmDash"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


CONFIG_FILE = _config_dir() / "config.json"

DEFAULT_CONFIG = {
    "fs25_path": "",
    "refresh_interval": 60,
    "selected_save": None,
    "open_browser_on_start": False,
}


def read_config() -> dict:
    if not CONFIG_FILE.exists():
        write_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {**DEFAULT_CONFIG, **data}


def write_config(config: dict) -> dict:
    merged = {**DEFAULT_CONFIG, **config}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    return merged


def get_saves_dir(config: dict = None) -> Path | None:
    if config is None:
        config = read_config()
    fs25_path = config.get("fs25_path", "").strip()
    if not fs25_path:
        return None
    path = Path(fs25_path)
    if path.exists():
        return path
    return None
