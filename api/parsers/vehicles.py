import xml.etree.ElementTree as ET
from pathlib import Path
import re


def parse_vehicles(save_path: Path) -> dict:
    xml_file = save_path / "vehicles.xml"
    if not xml_file.exists():
        return {"vehicles": []}

    tree = ET.parse(xml_file)
    root = tree.getroot()

    vehicles = []
    for v_el in root.findall("vehicle"):
        filename = v_el.get("filename", "")
        farm_id = v_el.get("farmId", "0")
        property_state = v_el.get("propertyState", "NONE")
        type_name = v_el.get("typeName", "")

        # Skip vehicles not owned by a farm
        if property_state == "NONE":
            continue

        name = _extract_name(filename)
        age = float(v_el.get("age", 0))
        price = float(v_el.get("price", 0))
        operating_time = float(v_el.get("operatingTime", 0))

        position = None
        comp = v_el.find("component")
        if comp is not None:
            pos_str = comp.get("position", "")
            parts = pos_str.split()
            if len(parts) == 3:
                try:
                    position = {
                        "x": float(parts[0]),
                        "y": float(parts[1]),
                        "z": float(parts[2]),
                    }
                except ValueError:
                    pass

        damage = 0.0
        wearable = v_el.find("wearable")
        if wearable is None and operating_time == 0:
            # Not a real vehicle/implement — likely a seed pallet, fertilizer bag, etc.
            continue
        if wearable is not None:
            damage = float(wearable.get("damage", 0))

        dirt = 0.0
        washable = v_el.find("washable")
        if washable is not None:
            dirt_node = washable.find("dirtNode")
            if dirt_node is not None:
                dirt = float(dirt_node.get("amount", 0))

        fuel_units = []
        fill_unit = v_el.find("fillUnit")
        if fill_unit is not None:
            for unit in fill_unit.findall("unit"):
                fill_type = unit.get("fillType", "")
                fill_level = float(unit.get("fillLevel", 0))
                fuel_units.append({"type": fill_type, "level": fill_level})

        mod_name = v_el.get("modName", "")

        vehicles.append({
            "filename": filename,
            "name": name,
            "typeName": type_name,
            "farmId": farm_id,
            "propertyState": property_state,
            "age": round(age, 1),
            "price": round(price),
            "operatingTime": round(operating_time / 3600, 1),
            "position": position,
            "damage": round(damage * 100, 1),
            "dirt": round(dirt * 100, 1),
            "fillUnits": fuel_units,
            "modName": mod_name,
        })

    vehicles.sort(key=lambda v: (v["farmId"], v["name"]))

    return {"vehicles": vehicles, "total": len(vehicles)}


# Generic/meaningless path segment names that shouldn't be used as vehicle names
_BAD_SEGMENTS = {
    'xml', 'vehicles', 'data', 'objects', 'mods', 'mod', 'pdlc', 'dlc',
    'content', 'base', 'res', 'shared', 'assets', 'misc',
}


def _extract_name(filename: str) -> str:
    if not filename:
        return "Unknown"

    filename = filename.replace("$pdlcdir$", "").replace("$moddir$", "")
    parts = [p for p in filename.replace("\\", "/").split("/") if p]

    if not parts:
        return "Unknown"

    # Build candidate list: folder (parts[-2]), filename stem, parent folder (parts[-3])
    candidates = []
    if len(parts) >= 2:
        candidates.append(parts[-2])
    candidates.append(parts[-1].replace(".xml", "").replace(".i3d", ""))
    if len(parts) >= 3:
        candidates.append(parts[-3])

    # Pick first candidate that isn't a generic path segment
    name = next(
        (c for c in candidates if c.lower() not in _BAD_SEGMENTS and len(c) > 2),
        candidates[0] if candidates else "Unknown",
    )

    # Convert camelCase / underscores to readable
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    name = name.replace("_", " ")
    name = " ".join(word.capitalize() for word in name.split())

    return name or "Unknown"
