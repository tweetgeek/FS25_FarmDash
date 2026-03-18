import xml.etree.ElementTree as ET
from pathlib import Path


def parse_missions(save_path: Path) -> dict:
    xml_file = save_path / "missions.xml"
    if not xml_file.exists():
        return {"missions": []}

    tree = ET.parse(xml_file)
    root = tree.getroot()

    missions = []
    for child in root:
        tag = child.tag
        if tag == "meta":
            continue

        unique_id = child.get("uniqueId", "")
        status = child.get("status", "")
        finish_state = child.get("finishState", "")

        info_el = child.find("info")
        reward = 0
        completion = 0.0
        if info_el is not None:
            reward = int(float(info_el.get("reward", 0)))
            completion = float(info_el.get("completion", 0))

        end_date_el = child.find("endDate")
        end_day = None
        if end_date_el is not None:
            end_day = int(end_date_el.get("endDay", 0))

        field_el = child.find("field")
        field_id = None
        if field_el is not None:
            field_id = int(field_el.get("id", 0))

        fruit_type = child.get("fruitType", "")
        num_trees = child.get("numTrees")

        missions.append({
            "id": unique_id[:16] if unique_id else "",
            "type": tag,
            "status": status,
            "finishState": finish_state,
            "reward": reward,
            "completion": round(completion * 100, 1),
            "endDay": end_day,
            "fieldId": field_id,
            "fruitType": fruit_type or None,
            "numTrees": int(num_trees) if num_trees else None,
        })

    return {
        "missions": missions,
        "total": len(missions),
        "active": sum(1 for m in missions if m["status"] in ("CREATED", "RUNNING")),
    }
