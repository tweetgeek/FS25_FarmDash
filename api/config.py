import json
import os
from pathlib import Path

CONFIG_FILE = Path(__file__).parent.parent / "config.json"

DEFAULT_CONFIG = {
    "fs25_path": "",
    "refresh_interval": 30,
    "selected_save": None
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
