import xml.etree.ElementTree as ET
from pathlib import Path
import re


# Known building filename keywords → category key
_BUILDING_CATEGORIES = [
    ("greenhouse",      "greenhouse"),
    ("bakery",          "bakery"),
    ("flourmill",       "flourmill"),
    ("flour_mill",      "flourmill"),
    ("grainmill",       "flourmill"),
    ("grain_mill",      "flourmill"),
    ("windmill",        "flourmill"),
    ("sawmill",         "sawmill"),
    ("sawmill",         "sawmill"),
    ("spinnery",        "spinnery"),
    ("textile",         "spinnery"),
    ("bga",             "biogas"),
    ("biogas",          "biogas"),
    ("dairy",           "dairy"),
    ("cheese",          "dairy"),
    ("oilmill",         "oilmill"),
    ("oil_mill",        "oilmill"),
    ("winery",          "winery"),
    ("brewery",         "brewery"),
    ("distillery",      "brewery"),
    ("fishfarm",        "fishfarm"),
    ("fish_farm",       "fishfarm"),
    ("hatchery",        "fishfarm"),
    ("slaughterhouse",  "slaughterhouse"),
    ("butcher",         "slaughterhouse"),
    ("quarry",          "quarry"),
    ("coalmine",        "quarry"),
    ("mine",            "quarry"),
    ("soupfactory",     "factory"),
    ("factory",         "factory"),
    ("cannery",         "factory"),
    ("preserves",       "factory"),
]


def _get_category(filename: str) -> str:
    low = filename.lower().replace("_", "").replace("-", "")
    for keyword, cat in _BUILDING_CATEGORIES:
        if keyword.replace("_", "") in low:
            return cat
    return "other"


def _extract_name(filename: str) -> str:
    if not filename:
        return "Unknown"
    filename = filename.replace("$pdlcdir$", "").replace("$moddir$", "")
    parts = [p for p in filename.replace("\\", "/").split("/") if p]
    if not parts:
        return "Unknown"
    stem = parts[-1].replace(".xml", "").replace(".i3d", "")
    stem = re.sub(r'([a-z])([A-Z])', r'\1 \2', stem)
    stem = stem.replace("_", " ")
    return " ".join(w.capitalize() for w in stem.split()) or "Unknown"


def _production_id_to_label(prod_id: str) -> str:
    """Convert camelCase/underscore production ID to readable label."""
    label = re.sub(r'([a-z])([A-Z])', r'\1 \2', prod_id)
    label = label.replace("_", " ")
    return " ".join(w.capitalize() for w in label.split())


def _get_player_farm_ids(save_path: Path) -> set:
    """Return set of farmIds belonging to human players (non-zero)."""
    farms_file = save_path / "farms.xml"
    if not farms_file.exists():
        return {"1"}
    try:
        root = ET.parse(farms_file).getroot()
        return {f.get("farmId", "1") for f in root.findall("farm")
                if f.get("farmId") and f.get("farmId") != "0"}
    except Exception:
        return {"1"}


def parse_production(save_path: Path) -> dict:
    xml_file = save_path / "placeables.xml"
    if not xml_file.exists():
        return {"facilities": [], "summary": {}}

    player_farm_ids = _get_player_farm_ids(save_path)

    tree = ET.parse(xml_file)
    root = tree.getroot()

    facilities = []
    summary: dict[str, int] = {}   # category → count of active productions

    for p_el in root.findall("placeable"):
        pp = p_el.find("productionPoint")
        if pp is None:
            continue

        farm_id = p_el.get("farmId", "0")
        if farm_id == "0" or farm_id not in player_farm_ids:
            continue

        filename = p_el.get("filename", "")
        name = _extract_name(filename)
        category = _get_category(filename)
        price = float(p_el.get("price", 0))
        age = float(p_el.get("age", 0))

        productions = []
        for pr in pp.findall("production"):
            prod_id = pr.get("id", "")
            enabled = pr.get("isEnabled", "false").lower() == "true"
            productions.append({
                "id": prod_id,
                "label": _production_id_to_label(prod_id),
                "enabled": enabled,
            })

        enabled_count = sum(1 for pr in productions if pr["enabled"])
        total_count = len(productions)

        if total_count == 0:
            continue

        # Update summary
        summary[category] = summary.get(category, 0) + enabled_count

        facilities.append({
            "farmId": farm_id,
            "name": name,
            "filename": filename,
            "category": category,
            "price": round(price),
            "ageMonths": round(age, 1),
            "productions": productions,
            "enabledCount": enabled_count,
            "totalCount": total_count,
        })

    facilities.sort(key=lambda f: (f["category"], f["name"]))

    return {
        "facilities": facilities,
        "summary": summary,
        "totalFacilities": len(facilities),
        "totalActiveProductions": sum(summary.values()),
    }
