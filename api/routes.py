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

router = APIRouter()


@router.get("/config")
def get_config():
    return read_config()


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
        if item.is_dir() and item.name.startswith("savegame"):
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


def _get_save_path(save_id: str) -> Path:
    config = read_config()
    saves_dir = get_saves_dir(config)
    if saves_dir is None:
        raise HTTPException(status_code=400, detail="Ścieżka FS25 nie jest skonfigurowana")

    save_path = saves_dir / save_id
    if not save_path.exists() or not save_path.is_dir():
        raise HTTPException(status_code=404, detail=f"Nie znaleziono save: {save_id}")

    return save_path
