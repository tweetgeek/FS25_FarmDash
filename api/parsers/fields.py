import xml.etree.ElementTree as ET
from pathlib import Path

FRUIT_EMOJI = {
    "WHEAT": "🌾", "BARLEY": "🌾", "OAT": "🌾", "SORGHUM": "🌾",
    "MAIZE": "🌽", "CANOLA": "🟡", "SUNFLOWER": "🌻", "SOYBEAN": "🫘",
    "POTATO": "🥔", "SUGARBEET": "🟤", "BEETROOT": "🟣",
    "CARROT": "🥕", "PARSNIP": "🥕", "ONION": "🧅",
    "PEA": "🟢", "GREENBEAN": "🟢", "SPINACH": "🥬",
    "COTTON": "⚪", "GRASS": "🌿",
    "UNKNOWN": "❓", "FALLOW": "⬜",
}

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


def parse_fields(save_path: Path) -> dict:
    xml_file = save_path / "fields.xml"
    if not xml_file.exists():
        return {"fields": []}

    tree = ET.parse(xml_file)
    root = tree.getroot()

    fields = []
    ready = []
    growing = []
    empty = []

    for field_el in root.findall("field"):
        field_id = int(field_el.get("id", 0))
        fruit_type = field_el.get("fruitType", "UNKNOWN")
        ground_type = field_el.get("groundType", "")
        growth_state = int(field_el.get("growthState", 0))
        weed_state = int(field_el.get("weedState", 0))
        spray_level = int(field_el.get("sprayLevel", 0))
        lime_level = int(field_el.get("limeLevel", 0))
        spray_type = field_el.get("sprayType", "NONE")

        status = _get_status(fruit_type, ground_type, growth_state)
        emoji = FRUIT_EMOJI.get(fruit_type, "🌱")

        field = {
            "id": field_id,
            "fruitType": fruit_type,
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
        elif status == "growing":
            growing.append(field_id)
        else:
            empty.append(field_id)

    fields.sort(key=lambda f: f["id"])

    return {
        "fields": fields,
        "summary": {
            "total": len(fields),
            "ready": len(ready),
            "growing": len(growing),
            "empty": len(empty),
            "readyIds": ready,
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
