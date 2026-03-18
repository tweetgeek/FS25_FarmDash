import xml.etree.ElementTree as ET
from pathlib import Path


def _load_ownership(save_path: Path) -> dict:
    """Returns {farmland_id: farm_id}. farm_id=0 means unowned."""
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


def _parse_counter(el) -> dict:
    if el is None:
        return {}
    def f(name): return round(float(el.get(name, 0)), 3)
    def i(name): return int(float(el.get(name, 0)))
    return {
        "numSoilSamples":           i("numSoilSamples"),
        "soilSampleCosts":          f("soilSampleCosts"),
        "usedLime":                 f("usedLime"),
        "usedMineralFertilizer":    f("usedMineralFertilizer"),
        "usedLiquidFertilizer":     f("usedLiquidFertilizer"),
        "usedManure":               f("usedManure"),
        "usedLiquidManure":         f("usedLiquidManure"),
        "usedSeeds":                f("usedSeeds"),
        "usedHerbicide":            f("usedHerbicide"),
        "yield":                    f("yield"),
        "yieldBestPrice":           f("yieldBestPrice"),
        "usedFuel":                 f("usedFuel"),
        "vehicleCosts":             f("vehicleCosts"),
        "helperCosts":              f("helperCosts"),
        "subsidies":                f("subsidies"),
    }


def parse_precision_farming(save_path: Path) -> dict:
    xml_file = save_path / "precisionFarming.xml"
    if not xml_file.exists():
        return {"available": False, "fields": [], "summary": {}}

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except Exception:
        return {"available": False, "fields": [], "summary": {}}

    ownership = _load_ownership(save_path)

    # ── farmlandStatistics ──────────────────────────────────────────────────
    stats_map: dict[int, dict] = {}
    stats_el = root.find("farmlandStatistics")
    if stats_el is not None:
        for fs in stats_el.findall("farmlandStatistic"):
            fid = int(fs.get("farmlandId", 0))
            stats_map[fid] = {
                "period": _parse_counter(fs.find("periodCounter")),
                "total":  _parse_counter(fs.find("totalCounter")),
            }

    # ── environmentalScore ─────────────────────────────────────────────────
    env_el = root.find("environmentalScore")

    nitrogen_map: dict[int, dict] = {}
    ph_map:       dict[int, dict] = {}
    herbicide_map:dict[int, dict] = {}
    soil_map:     dict[int, float] = {}
    tillage_map:  dict[int, dict] = {}
    harvested_set: set[int] = set()

    if env_el is not None:
        for fl in (env_el.find("nitrogen") or []).findall("farmland"):
            fid = int(fl.get("farmlandId", 0))
            ha  = float(fl.get("harvestedArea", 0))
            n   = float(fl.get("nOffsetSum", 0))
            nitrogen_map[fid] = {
                "harvestedAreaHa": round(ha, 3),
                "nOffsetSum":      round(n, 6),
                "perHa":           round(n / ha, 4) if ha > 0 else None,
            }

        for fl in (env_el.find("ph") or []).findall("farmland"):
            fid = int(fl.get("farmlandId", 0))
            ha  = float(fl.get("harvestedArea", 0))
            ph  = float(fl.get("phOffsetSum", 0))
            ph_map[fid] = {
                "harvestedAreaHa": round(ha, 3),
                "phOffsetSum":     round(ph, 6),
                "perHa":           round(ph / ha, 4) if ha > 0 else None,
            }

        for fl in (env_el.find("herbicide") or []).findall("farmland"):
            fid   = int(fl.get("farmlandId", 0))
            spot  = float(fl.get("spotSpray", 0))
            full  = float(fl.get("fullSpray", 0))
            mech  = float(fl.get("mechanical", 0))
            total = spot + full + mech
            herbicide_map[fid] = {
                "spotSpray":  round(spot, 1),
                "fullSpray":  round(full, 1),
                "mechanical": round(mech, 1),
                "spotPct":    round(spot / total * 100) if total > 0 else None,
                "fullPct":    round(full / total * 100) if total > 0 else None,
                "mechPct":    round(mech / total * 100) if total > 0 else None,
            }

        for fl in (env_el.find("soilSample") or []).findall("farmland"):
            fid = int(fl.get("farmlandId", 0))
            pct = float(fl.get("samplePercentage", -1))
            soil_map[fid] = pct  # -1 = no sample

        for fl in (env_el.find("tillage") or []).findall("farmland"):
            fid   = int(fl.get("farmlandId", 0))
            total = float(fl.get("totalFieldArea", 0))
            none_ = float(fl.get("workedAreaNone", 0))
            deep  = float(fl.get("workedAreaDeep", 0))
            flat  = float(fl.get("workedAreaFlat", 0))
            direct= float(fl.get("workedAreaDirect", 0))
            tillage_map[fid] = {
                "nonePct":   round(none_  / total * 100) if total > 0 else 0,
                "flatPct":   round(flat   / total * 100) if total > 0 else 0,
                "deepPct":   round(deep   / total * 100) if total > 0 else 0,
                "directPct": round(direct / total * 100) if total > 0 else 0,
            }

        for hs in (env_el.find("harvestedStates") or []).findall("harvestedState"):
            if int(hs.get("state", 0)) > 0:
                harvested_set.add(int(hs.get("farmlandId", 0)))

    # ── Build output for ALL farmlands in ownership ────────────────────────
    all_fids = sorted(ownership.keys())
    fields = []
    total_yield = 0.0
    total_revenue = 0.0
    total_costs = 0.0
    fields_with_sample = 0

    for fid in all_fids:
        farm_id = ownership[fid]
        owned = farm_id != 0

        st = stats_map.get(fid, {"period": {}, "total": {}})
        tc = st["total"]

        soil_pct = soil_map.get(fid, -1.0)

        fields.append({
            "id":          fid,
            "farmId":      farm_id,
            "owned":       owned,
            "harvested":   fid in harvested_set,
            "periodStats": st["period"],
            "totalStats":  tc,
            "soilSample":  round(soil_pct, 3),    # -1 = no sample, 0-1 = coverage
            "nitrogen":    nitrogen_map.get(fid),  # None if no data
            "ph":          ph_map.get(fid),        # None if no data
            "herbicide":   herbicide_map.get(fid), # None if no data
            "tillage":     tillage_map.get(fid),   # None if no data
        })

        if owned:
            y = tc.get("yield", 0)
            r = tc.get("yieldBestPrice", 0)
            c = tc.get("vehicleCosts", 0) + tc.get("helperCosts", 0)
            total_yield   += y
            total_revenue += r
            total_costs   += c
            if soil_pct >= 0:
                fields_with_sample += 1

    owned_fields = [f for f in fields if f["owned"]]

    return {
        "available": True,
        "fields": fields,
        "summary": {
            "ownedFieldCount":    len(owned_fields),
            "fieldsWithSample":   fields_with_sample,
            "totalYield":         round(total_yield, 1),
            "totalRevenue":       round(total_revenue, 1),
            "totalOperatingCosts":round(total_costs, 1),
        },
    }
