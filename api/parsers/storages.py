import xml.etree.ElementTree as ET
from pathlib import Path

SKIP_TYPES = {
    'UNKNOWN', 'DIESEL', 'DEF', 'ADBLUE', 'PETROL',
    'ELECTRICCHARGE', 'METHANE', 'METHANOL', 'AIR',
    'WATER', 'DIGESTATE',
}

FILL_NAMES_PL = {
    'WHEAT': 'Pszenica', 'BARLEY': 'Jęczmień', 'OAT': 'Owies',
    'CANOLA': 'Rzepak', 'SORGHUM': 'Sorgo', 'SUNFLOWER': 'Słonecznik',
    'SOYBEAN': 'Soja', 'MAIZE': 'Kukurydza', 'POTATO': 'Ziemniaki',
    'SUGARBEET': 'Buraki cukrowe', 'BEETROOT': 'Buraczki',
    'CARROT': 'Marchew', 'PARSNIP': 'Pasternak',
    'SILAGE': 'Kiszonka', 'DRYGRASS_WINDROW': 'Siano',
    'GRASS_WINDROW': 'Trawa', 'STRAW': 'Słoma',
    'WOODCHIPS': 'Zrębki', 'WOOL': 'Wełna', 'MILK': 'Mleko',
    'FERTILIZER': 'Nawóz stały', 'LIQUIDFERTILIZER': 'Nawóz płynny',
    'HERBICIDE': 'Herbicyd', 'SEEDS': 'Nasiona',
    'LIQUIDMANURE': 'Gnojowica', 'MANURE': 'Obornik',
    'SLURRY': 'Gnojówka',
}

FILL_EMOJIS = {
    'WHEAT': '🌾', 'BARLEY': '🌾', 'OAT': '🌾', 'SORGHUM': '🌾',
    'MAIZE': '🌽', 'CANOLA': '🟡', 'SUNFLOWER': '🌻', 'SOYBEAN': '🫘',
    'POTATO': '🥔', 'SUGARBEET': '🟤', 'BEETROOT': '🟣',
    'CARROT': '🥕', 'PARSNIP': '🥕',
    'SILAGE': '🟫', 'DRYGRASS_WINDROW': '🌿', 'GRASS_WINDROW': '🌿',
    'STRAW': '🟨', 'WOOL': '🐑', 'MILK': '🥛',
    'FERTILIZER': '🧪', 'LIQUIDFERTILIZER': '🧪',
    'SEEDS': '🌱', 'LIQUIDMANURE': '💧', 'MANURE': '💩', 'SLURRY': '💧',
}

CATEGORY = {
    'WHEAT': 'crops', 'BARLEY': 'crops', 'OAT': 'crops', 'SORGHUM': 'crops',
    'MAIZE': 'crops', 'CANOLA': 'crops', 'SUNFLOWER': 'crops', 'SOYBEAN': 'crops',
    'POTATO': 'crops', 'SUGARBEET': 'crops', 'BEETROOT': 'crops',
    'CARROT': 'crops', 'PARSNIP': 'crops',
    'SILAGE': 'feed', 'DRYGRASS_WINDROW': 'feed', 'GRASS_WINDROW': 'feed', 'STRAW': 'feed',
    'WOOL': 'products', 'MILK': 'products', 'WOODCHIPS': 'products',
    'FERTILIZER': 'supplies', 'LIQUIDFERTILIZER': 'supplies',
    'HERBICIDE': 'supplies', 'SEEDS': 'supplies',
    'LIQUIDMANURE': 'manure', 'MANURE': 'manure', 'SLURRY': 'manure',
}


def parse_storages(save_path: Path, farm_id: int = 1) -> dict:
    totals = {}  # fill_type -> total_level

    _add_vehicle_cargo(save_path, farm_id, totals)
    _add_bales(save_path, farm_id, totals)
    _add_placeables(save_path, farm_id, totals)

    items = []
    for fill_type, level in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        if level < 1:
            continue
        items.append({
            "type": fill_type,
            "name": FILL_NAMES_PL.get(fill_type, fill_type),
            "emoji": FILL_EMOJIS.get(fill_type, '📦'),
            "level": round(level),
            "category": CATEGORY.get(fill_type, 'other'),
        })

    return {"items": items}


def _add_vehicle_cargo(save_path: Path, farm_id: int, totals: dict):
    xml_file = save_path / "vehicles.xml"
    if not xml_file.exists():
        return
    try:
        root = ET.parse(xml_file).getroot()
    except Exception:
        return

    farm_id_str = str(farm_id)
    for v_el in root.findall("vehicle"):
        if v_el.get("farmId") != farm_id_str:
            continue
        if v_el.get("propertyState") == "NONE":
            continue
        fu_el = v_el.find("fillUnit")
        if fu_el is None:
            continue
        for unit in fu_el.findall("unit"):
            ft = unit.get("fillType", "")
            if not ft or ft in SKIP_TYPES:
                continue
            level = float(unit.get("fillLevel", 0))
            if level < 1:
                continue
            totals[ft] = totals.get(ft, 0) + level


def _add_bales(save_path: Path, farm_id: int, totals: dict):
    xml_file = save_path / "items.xml"
    if not xml_file.exists():
        return
    try:
        root = ET.parse(xml_file).getroot()
    except Exception:
        return

    farm_id_str = str(farm_id)
    for item_el in root.findall("item"):
        if item_el.get("className") != "Bale":
            continue
        if item_el.get("farmId") != farm_id_str:
            continue
        ft = item_el.get("fillType", "")
        if not ft or ft in SKIP_TYPES:
            continue
        level = float(item_el.get("fillLevel", 0))
        if level < 1:
            continue
        totals[ft] = totals.get(ft, 0) + level


def _add_placeables(save_path: Path, farm_id: int, totals: dict):
    xml_file = save_path / "placeables.xml"
    if not xml_file.exists():
        return
    try:
        root = ET.parse(xml_file).getroot()
    except Exception:
        return

    farm_id_str = str(farm_id)
    for p_el in root.findall("placeable"):
        if p_el.get("farmId") != farm_id_str:
            continue

        # Bunker silos (kiszonka)
        for bs_el in p_el.findall("multiBunkerSilo/bunkerSilo"):
            level = float(bs_el.get("fillLevel", 0))
            if level > 1:
                totals["SILAGE"] = totals.get("SILAGE", 0) + level

        # Husbandry food (karma dla zwierząt)
        for fl_el in p_el.findall("husbandryFood/fillLevel"):
            ft = fl_el.get("fillType", "")
            if not ft or ft in SKIP_TYPES:
                continue
            level = float(fl_el.get("fillLevel", 0))
            if level > 1:
                totals[ft] = totals.get(ft, 0) + level
