import xml.etree.ElementTree as ET
from pathlib import Path


def parse_farms(save_path: Path) -> dict:
    xml_file = save_path / "farms.xml"
    if not xml_file.exists():
        return {}

    tree = ET.parse(xml_file)
    root = tree.getroot()

    farms = []
    for farm_el in root.findall("farm"):
        farm = {
            "farmId": farm_el.get("farmId"),
            "name": farm_el.get("name", "Gospodarstwo"),
            "money": _float_attr(farm_el, "money"),
            "loan": _float_attr(farm_el, "loan"),
        }

        stats_el = farm_el.find("statistics")
        if stats_el is not None:
            farm["statistics"] = {
                "playTime": _float_child(stats_el, "playTime"),
                "workedHectares": _float_child(stats_el, "workedHectares"),
                "threshedHectares": _float_child(stats_el, "threshedHectares"),
                "cultivatedHectares": _float_child(stats_el, "cultivatedHectares"),
                "sownHectares": _float_child(stats_el, "sownHectares"),
                "fuelUsage": _float_child(stats_el, "fuelUsage"),
                "traveledDistance": _float_child(stats_el, "traveledDistance"),
                "workedTime": _float_child(stats_el, "workedTime"),
                "baleCount": int(_float_child(stats_el, "baleCount")),
                "missionCount": int(_float_child(stats_el, "missionCount")),
            }

        finances_el = farm_el.find("finances")
        if finances_el is not None:
            finance_entries = []
            for stats_day in finances_el.findall("stats"):
                day = stats_day.get("day", "0")
                entry = {"day": day}
                for child in stats_day:
                    try:
                        entry[child.tag] = float(child.text) if child.text else 0.0
                    except ValueError:
                        entry[child.tag] = child.text
                finance_entries.append(entry)
            farm["finances"] = finance_entries

        farms.append(farm)

    return {"farms": farms}


def _float_attr(el, attr: str, default: float = 0.0) -> float:
    val = el.get(attr, "")
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _float_child(el, tag: str, default: float = 0.0) -> float:
    child = el.find(tag)
    if child is not None and child.text:
        try:
            return float(child.text)
        except ValueError:
            pass
    return default
