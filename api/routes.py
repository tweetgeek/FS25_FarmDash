from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from api.config import read_config, write_config, get_saves_dir
from api.parsers.career import parse_career
from api.parsers.farms import parse_farms
from api.parsers.fields import parse_fields
from api.parsers.vehicles import parse_vehicles
from api.parsers.environment import parse_environment
from api.parsers.missions import parse_missions
from api.parsers.economy import parse_economy
from api.parsers.storages import parse_storages
from api.parsers.precision_farming import parse_precision_farming
from api.parsers.animals import parse_animals

router = APIRouter()

PORT = 9988


def _get_local_ip() -> str:
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def _is_savegame_dir(name: str) -> bool:
    """Matches savegame1, savegame2, ... but not savegameBackup etc."""
    prefix = "savegame"
    return name.startswith(prefix) and name[len(prefix):].isdigit() and len(name) > len(prefix)


@router.get("/config")
def get_config():
    return read_config()


@router.get("/local-address")
def get_local_address():
    return {"url": f"http://{_get_local_ip()}:{PORT}"}


@router.get("/detect-saves-path")
def detect_saves_path():
    home = Path.home()
    candidates = [
        home / "Documents" / "My Games" / "FarmingSimulator2025",
        home / "OneDrive" / "Documents" / "My Games" / "FarmingSimulator2025",
        home / "Moje dokumenty" / "My Games" / "FarmingSimulator2025",
    ]
    for path in candidates:
        if path.exists() and any(_is_savegame_dir(p.name) for p in path.iterdir() if p.is_dir()):
            return {"path": str(path)}
    # Return first existing directory even without savegames yet
    for path in candidates:
        if path.exists():
            return {"path": str(path)}
    return {"path": None}


@router.get("/browse-folder")
def browse_folder():
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", True)
        path = filedialog.askdirectory(
            parent=root,
            title="Wybierz katalog z zapisami FS25",
        )
        root.destroy()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nie można otworzyć okna wyboru folderu: {e}")
    if not path:
        return {"path": None}
    return {"path": path}


@router.post("/config")
def post_config(body: dict):
    updated = write_config(body)
    return updated


@router.get("/saves")
def list_saves():
    config = read_config()
    saves_dir = get_saves_dir(config)
    if saves_dir is None:
        raise HTTPException(status_code=400, detail="Ścieżka FS25 nie jest ustawiona lub nieprawidłowa")

    saves = []
    for item in sorted(saves_dir.iterdir()):
        if item.is_dir() and _is_savegame_dir(item.name):
            career_file = item / "careerSavegame.xml"
            farms_file = item / "farms.xml"

            save_info = {
                "id": item.name,
                "path": str(item),
                "name": item.name,
                "mapTitle": "",
                "savegameName": "",
                "saveDate": "",
                "money": 0,
            }

            if career_file.exists():
                career = parse_career(item)
                save_info["savegameName"] = career.get("savegameName", "")
                save_info["mapTitle"] = career.get("mapTitle", "")
                save_info["saveDate"] = career.get("saveDateFormatted", career.get("saveDate", ""))

            if farms_file.exists():
                farms_data = parse_farms(item)
                farms_list = farms_data.get("farms", [])
                if farms_list:
                    save_info["money"] = farms_list[0].get("money", 0)

            saves.append(save_info)

    return {"saves": saves}


@router.get("/save/{save_id}/summary")
def get_summary(save_id: str):
    save_path = _get_save_path(save_id)
    career = parse_career(save_path)
    farms_data = parse_farms(save_path)
    env = parse_environment(save_path)

    farms_list = farms_data.get("farms", [])
    farm = farms_list[0] if farms_list else {}

    return {
        "career": career,
        "farm": farm,
        "environment": {
            "currentDay": env.get("currentDay"),
            "dayTime": env.get("dayTime"),
            "currentWeather": env.get("currentWeather"),
            "currentWeatherIcon": env.get("currentWeatherIcon"),
        }
    }


@router.get("/save/{save_id}/fields")
def get_fields(save_id: str):
    save_path = _get_save_path(save_id)
    return parse_fields(save_path)


@router.get("/save/{save_id}/vehicles")
def get_vehicles(save_id: str):
    save_path = _get_save_path(save_id)
    return parse_vehicles(save_path)


@router.get("/save/{save_id}/weather")
def get_weather(save_id: str):
    save_path = _get_save_path(save_id)
    return parse_environment(save_path)


@router.get("/save/{save_id}/missions")
def get_missions(save_id: str):
    save_path = _get_save_path(save_id)
    return parse_missions(save_path)


@router.get("/save/{save_id}/economy")
def get_economy(save_id: str):
    save_path = _get_save_path(save_id)
    return parse_economy(save_path)


@router.get("/save/{save_id}/storage")
def get_storage(save_id: str):
    save_path = _get_save_path(save_id)
    return parse_storages(save_path)


@router.get("/save/{save_id}/precision")
def get_precision_farming(save_id: str):
    save_path = _get_save_path(save_id)
    return parse_precision_farming(save_path)


@router.get("/save/{save_id}/animals")
def get_animals(save_id: str):
    save_path = _get_save_path(save_id)
    return parse_animals(save_path)


def _get_save_path(save_id: str) -> Path:
    config = read_config()
    saves_dir = get_saves_dir(config)
    if saves_dir is None:
        raise HTTPException(status_code=400, detail="Ścieżka FS25 nie jest skonfigurowana")

    save_path = saves_dir / save_id
    if not save_path.exists() or not save_path.is_dir():
        raise HTTPException(status_code=404, detail=f"Nie znaleziono save: {save_id}")

    return save_path
