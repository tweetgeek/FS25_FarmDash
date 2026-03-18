import xml.etree.ElementTree as ET
from pathlib import Path


def parse_career(save_path: Path) -> dict:
    xml_file = save_path / "careerSavegame.xml"
    if not xml_file.exists():
        return {}

    tree = ET.parse(xml_file)
    root = tree.getroot()

    settings = root.find("settings")
    stats = root.find("statistics")

    result = {}

    if settings is not None:
        result["savegameName"] = _text(settings, "savegameName")
        result["mapTitle"] = _text(settings, "mapTitle")
        result["mapId"] = _text(settings, "mapId")
        result["creationDate"] = _text(settings, "creationDate")
        result["saveDate"] = _text(settings, "saveDate")
        result["saveDateFormatted"] = _text(settings, "saveDateFormatted")
        result["economicDifficulty"] = _text(settings, "economicDifficulty")
        result["growthMode"] = _text(settings, "growthMode")
        result["timeScale"] = _float(settings, "timeScale")
        result["weedsEnabled"] = _text(settings, "weedsEnabled") == "true"
        result["limeRequired"] = _text(settings, "limeRequired") == "true"
        result["stonesEnabled"] = _text(settings, "stonesEnabled") == "true"
        result["fuelUsage"] = _text(settings, "fuelUsage")

    if stats is not None:
        result["money"] = _float(stats, "money")
        result["playTime"] = _float(stats, "playTime")

    return result


def _text(el, tag: str, default: str = "") -> str:
    child = el.find(tag)
    if child is not None and child.text:
        return child.text.strip()
    return default


def _float(el, tag: str, default: float = 0.0) -> float:
    val = _text(el, tag)
    try:
        return float(val)
    except (ValueError, TypeError):
        return default
