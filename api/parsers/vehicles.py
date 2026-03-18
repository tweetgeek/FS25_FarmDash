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
            "farmId": farm_id,
            "propertyState": property_state,
            "age": round(age, 1),
            "price": round(price),
            "operatingTime": round(operating_time, 1),
            "position": position,
            "damage": round(damage * 100, 1),
            "dirt": round(dirt * 100, 1),
            "fillUnits": fuel_units,
            "modName": mod_name,
        })

    vehicles.sort(key=lambda v: (v["farmId"], v["name"]))

    return {"vehicles": vehicles, "total": len(vehicles)}


def _extract_name(filename: str) -> str:
    if not filename:
        return "Nieznany pojazd"

    # Remove path prefix like $pdlcdir$... or data/vehicles/...
    filename = filename.replace("$pdlcdir$", "").replace("$moddir$", "")

    # Get last path segment without extension
    parts = filename.replace("\\", "/").split("/")
    # Take the second-to-last part (folder name is usually vehicle name)
    if len(parts) >= 2:
        name = parts[-2]
    else:
        name = parts[-1].replace(".xml", "")

    # Convert camelCase/underscores to readable
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    name = name.replace("_", " ")
    name = " ".join(word.capitalize() for word in name.split())

    return name or "Pojazd"
