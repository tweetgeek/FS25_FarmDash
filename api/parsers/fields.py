import xml.etree.ElementTree as ET
from pathlib import Path

FRUIT_INFO: dict[str, tuple[str, str]] = {
    # (Polish name, emoji)
    "WHEAT":        ("Pszenica",            "🌾"),
    "BARLEY":       ("Jęczmień",            "🌾"),
    "OAT":          ("Owies",               "🌾"),
    "SORGHUM":      ("Sorgo",               "🌾"),
    "MAIZE":        ("Kukurydza",           "🌽"),
    "CANOLA":       ("Rzepak",              "🟡"),
    "SUNFLOWER":    ("Słonecznik",          "🌻"),
    "SOYBEAN":      ("Soja",               "🫘"),
    "POTATO":       ("Ziemniaki",           "🥔"),
    "SUGARBEET":    ("Buraki cukrowe",      "🟤"),
    "SUGARCANE":    ("Trzcina cukrowa",     "🎋"),
    "BEETROOT":     ("Buraczki",            "🟣"),
    "CARROT":       ("Marchew",             "🥕"),
    "PARSNIP":      ("Pasternak",           "🥕"),
    "ONION":        ("Cebula",              "🧅"),
    "PEA":          ("Groch",               "🟢"),
    "GREENBEAN":    ("Fasolka szparagowa",  "🫘"),
    "SPINACH":      ("Szpinak",             "🥬"),
    "COTTON":       ("Bawełna",             "⚪"),
    "GRASS":        ("Trawa",               "🌿"),
    "MEADOW":       ("Łąka",                "🌿"),
    "OILSEEDRADISH":("Rzodkiew oleista",    "🌱"),
    "LETTUCE":      ("Sałata",              "🥬"),
    "CHILLI":       ("Chili",               "🌶️"),
    "TOMATO":       ("Pomidor",             "🍅"),
    "STRAWBERRY":   ("Truskawka",           "🍓"),
    "GARLIC":       ("Czosnek",             "🧄"),
    "NAPACABBAGE":  ("Kapusta pekińska",    "🥬"),
    "GRAPE":        ("Winogrona",           "🍇"),
    "OLIVE":        ("Oliwki",              "🫒"),
    "SPRING_ONION": ("Szczypiorek",         "🌱"),
    "RICE":         ("Ryż",                 "🌾"),
    "POPLAR":       ("Topola",              "🌳"),
    "UNKNOWN":      ("Nieznana",            "❓"),
    "FALLOW":       ("Ugór",                "⬜"),
}

# Keep backward-compatible alias used elsewhere
FRUIT_EMOJI = {k: v[1] for k, v in FRUIT_INFO.items()}

GROUND_STATUS = {
    "HARVEST_READY": "ready",
    "HARVEST_READY_OTHER": "ready",
    "SOWN": "growing",
    "CULTIVATED": "empty",
    "PLOWED": "empty",
    "GRASS": "growing",
    "STUBBLE_TILLAGE": "empty",
    "ROLLED": "growing",
}


def _load_ownership(save_path: Path) -> dict:
    """Returns {field_id: farm_id} from farmland.xml. farm_id=0 means unowned."""
    xml_file = save_path / "farmland.xml"
    if not xml_file.exists():
        return {}
    try:
        tree = ET.parse(xml_file)
        return {
            int(el.get("id", 0)): int(el.get("farmId", 0))
            for el in tree.getroot().findall("farmland")
        }
    except Exception:
        return {}


def parse_fields(save_path: Path) -> dict:
    xml_file = save_path / "fields.xml"
    if not xml_file.exists():
        return {"fields": []}

    tree = ET.parse(xml_file)
    root = tree.getroot()

    ownership = _load_ownership(save_path)

    fields = []
    ready = []
    growing = []
    empty = []
    owned_ready = []

    for field_el in root.findall("field"):
        field_id = int(field_el.get("id", 0))
        fruit_type = field_el.get("fruitType", "UNKNOWN")
        ground_type = field_el.get("groundType", "")
        growth_state = int(field_el.get("growthState", 0))
        weed_state = int(field_el.get("weedState", 0))
        spray_level = int(field_el.get("sprayLevel", 0))
        lime_level = int(field_el.get("limeLevel", 0))
        spray_type = field_el.get("sprayType", "NONE")
        farm_id = ownership.get(field_id, 0)

        status = _get_status(fruit_type, ground_type, growth_state)
        info = FRUIT_INFO.get(fruit_type)
        fruit_name = info[0] if info else fruit_type.replace("_", " ").title()
        emoji = info[1] if info else "🌱"

        field = {
            "id": field_id,
            "farmId": farm_id,
            "owned": farm_id != 0,
            "fruitType": fruit_type,
            "fruitName": fruit_name,
            "fruitEmoji": emoji,
            "groundType": ground_type,
            "growthState": growth_state,
            "weedState": weed_state,
            "sprayLevel": spray_level,
            "limeLevel": lime_level,
            "sprayType": spray_type,
            "status": status,
        }
        fields.append(field)

        if status == "ready":
            ready.append(field_id)
            if farm_id != 0:
                owned_ready.append(field_id)
        elif status == "growing":
            growing.append(field_id)
        else:
            empty.append(field_id)

    fields.sort(key=lambda f: f["id"])
    owned_fields = [f for f in fields if f["owned"]]

    return {
        "fields": fields,
        "summary": {
            "total": len(fields),
            "owned": len(owned_fields),
            "ready": len(ready),
            "growing": len(growing),
            "empty": len(empty),
            "readyIds": ready,
            "ownedReadyIds": owned_ready,
        }
    }


def _get_status(fruit_type: str, ground_type: str, growth_state: int) -> str:
    if ground_type in ("HARVEST_READY", "HARVEST_READY_OTHER"):
        return "ready"
    if fruit_type in ("UNKNOWN", "FALLOW") or ground_type in ("PLOWED", "CULTIVATED", "STUBBLE_TILLAGE"):
        return "empty"
    if fruit_type == "GRASS" and growth_state > 0:
        return "growing"
    if growth_state > 0:
        return "growing"
    return "empty"
