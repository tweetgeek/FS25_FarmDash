import xml.etree.ElementTree as ET
from pathlib import Path
import re


_MAIN_TYPE_PREFIXES = [
    ("sheep",   "sheep"),
    ("cow",     "cow"),
    ("chicken", "chicken"),
    ("hen",     "chicken"),
    ("pig",     "pig"),
    ("horse",   "horse"),
    ("goat",    "goat"),
    ("donkey",  "donkey"),
    ("bee",     "bee"),
    ("deer",    "deer"),
    ("rabbit",  "rabbit"),
    ("ostrich", "ostrich"),
]


def _get_main_type(sub_type: str) -> str:
    low = sub_type.lower()
    for prefix, main in _MAIN_TYPE_PREFIXES:
        if low.startswith(prefix):
            return main
    return low


def _extract_building_name(filename: str) -> str:
    if not filename:
        return ""
    parts = filename.replace("\\", "/").split("/")
    stem = parts[-1].replace(".xml", "").replace(".i3d", "")
    stem = re.sub(r'([a-z])([A-Z])', r'\1 \2', stem)
    stem = stem.replace("_", " ")
    return " ".join(w.capitalize() for w in stem.split())


def parse_animals(save_path: Path) -> dict:
    xml_file = save_path / "placeables.xml"
    if not xml_file.exists():
        return {"pens": [], "summary": {}, "totalAnimals": 0}

    tree = ET.parse(xml_file)
    root = tree.getroot()

    pens = []
    summary: dict[str, int] = {}

    for p_el in root.findall("placeable"):
        animals_el = p_el.find("husbandryAnimals")
        if animals_el is None:
            continue

        farm_id = p_el.get("farmId", "0")
        filename = p_el.get("filename", "")
        building_name = _extract_building_name(filename)

        # ── Animal clusters ──────────────────────────────────────────────
        by_sub: dict[str, dict] = {}
        for cl_el in animals_el.findall("clusters/animal"):
            sub_type = cl_el.get("subType", "UNKNOWN")
            num = int(cl_el.get("numAnimals", 0))
            if num == 0:
                continue
            age = int(cl_el.get("age", 0))
            health = int(cl_el.get("health", 0))
            repro = int(cl_el.get("reproduction", 0))

            if sub_type not in by_sub:
                by_sub[sub_type] = {
                    "subType": sub_type,
                    "mainType": _get_main_type(sub_type),
                    "count": 0,
                    "totalHealth": 0,
                    "totalAge": 0,
                    "totalRepro": 0,
                }
            by_sub[sub_type]["count"] += num
            by_sub[sub_type]["totalHealth"] += health * num
            by_sub[sub_type]["totalAge"] += age * num
            by_sub[sub_type]["totalRepro"] += repro * num

        if not by_sub:
            continue

        animal_groups = []
        total_animals = 0
        health_sum = 0
        health_n = 0
        main_type = None

        for s in by_sub.values():
            n = s["count"]
            avg_health = round(s["totalHealth"] / n, 1)
            avg_age = round(s["totalAge"] / n, 1)
            avg_repro = round(s["totalRepro"] / n, 1)
            animal_groups.append({
                "subType": s["subType"],
                "mainType": s["mainType"],
                "count": n,
                "avgHealth": avg_health,
                "avgAgeMonths": avg_age,
                "avgReproduction": avg_repro,
            })
            total_animals += n
            health_sum += s["totalHealth"]
            health_n += n
            if main_type is None:
                main_type = s["mainType"]

        avg_health_pen = round(health_sum / health_n, 1) if health_n else 0

        # ── Food ────────────────────────────────────────────────────────
        food = []
        for fl_el in p_el.findall("husbandryFood/fillLevel"):
            ft = fl_el.get("fillType", "")
            level = float(fl_el.get("fillLevel", 0))
            if level > 0:
                food.append({"type": ft, "liters": round(level, 1)})

        # ── Pending products ─────────────────────────────────────────────
        products = []
        for pp_el in p_el.findall("husbandryPallets/pendingLiters"):
            ft = pp_el.get("fillType", "")
            liters = float(pp_el.get("liters", 0))
            if liters > 0:
                products.append({"type": ft, "liters": round(liters, 2)})

        # ── Production factor ────────────────────────────────────────────
        prod_el = p_el.find("husbandry")
        production_factor = float(prod_el.get("productionFactor", 0)) if prod_el is not None else 0.0

        # ── Summary ──────────────────────────────────────────────────────
        if main_type:
            summary[main_type] = summary.get(main_type, 0) + total_animals

        pens.append({
            "farmId": farm_id,
            "buildingName": building_name,
            "mainType": main_type,
            "totalAnimals": total_animals,
            "avgHealth": avg_health_pen,
            "productionFactor": round(production_factor * 100, 1),
            "animalGroups": animal_groups,
            "food": food,
            "products": products,
        })

    pens.sort(key=lambda p: (p["mainType"] or "", p["buildingName"]))

    return {
        "pens": pens,
        "summary": summary,
        "totalAnimals": sum(summary.values()),
    }
