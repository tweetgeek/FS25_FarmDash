import xml.etree.ElementTree as ET
from pathlib import Path

PERIODS = [
    'EARLY_SPRING', 'MID_SPRING', 'LATE_SPRING',
    'EARLY_SUMMER', 'MID_SUMMER', 'LATE_SUMMER',
    'EARLY_AUTUMN', 'MID_AUTUMN', 'LATE_AUTUMN',
    'EARLY_WINTER', 'MID_WINTER', 'LATE_WINTER',
]

PERIOD_LABELS_PL = [
    'Pocz. wiosny', 'Śr. wiosny', 'Kon. wiosny',
    'Pocz. lata', 'Śr. lata', 'Kon. lata',
    'Pocz. jesieni', 'Śr. jesieni', 'Kon. jesieni',
    'Pocz. zimy', 'Śr. zimy', 'Kon. zimy',
]

MAIN_CROPS = [
    'WHEAT', 'BARLEY', 'OAT', 'CANOLA', 'SORGHUM',
    'SUNFLOWER', 'SOYBEAN', 'MAIZE', 'POTATO',
    'SUGARBEET', 'BEETROOT', 'CARROT', 'PARSNIP',
]

CROP_NAMES_PL = {
    'WHEAT': 'Pszenica',
    'BARLEY': 'Jęczmień',
    'OAT': 'Owies',
    'CANOLA': 'Rzepak',
    'SORGHUM': 'Sorgo',
    'SUNFLOWER': 'Słonecznik',
    'SOYBEAN': 'Soja',
    'MAIZE': 'Kukurydza',
    'POTATO': 'Ziemniaki',
    'SUGARBEET': 'Buraki cukrowe',
    'BEETROOT': 'Buraczki',
    'CARROT': 'Marchew',
    'PARSNIP': 'Pasternak',
}

CROP_EMOJIS = {
    'WHEAT': '🌾', 'BARLEY': '🌾', 'OAT': '🌾', 'SORGHUM': '🌾',
    'MAIZE': '🌽', 'CANOLA': '🟡', 'SUNFLOWER': '🌻', 'SOYBEAN': '🫘',
    'POTATO': '🥔', 'SUGARBEET': '🟤', 'BEETROOT': '🟣',
    'CARROT': '🥕', 'PARSNIP': '🥕',
}


def _get_current_period_idx(save_path: Path) -> int:
    env_file = save_path / "environment.xml"
    if not env_file.exists():
        return 0
    try:
        tree = ET.parse(env_file)
        root = tree.getroot()
        current_day = int(root.findtext("currentDay", "1"))
        days_per_period = int(root.findtext("daysPerPeriod", "3"))
        year_length = 12 * days_per_period
        return ((current_day - 1) % year_length) // days_per_period
    except Exception:
        return 0


def parse_economy(save_path: Path) -> dict:
    xml_file = save_path / "economy.xml"
    if not xml_file.exists():
        return {"crops": [], "currentPeriodIdx": 0, "periodLabels": PERIOD_LABELS_PL}

    current_period_idx = _get_current_period_idx(save_path)

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except Exception:
        return {"crops": [], "currentPeriodIdx": current_period_idx, "periodLabels": PERIOD_LABELS_PL}

    fill_types_el = root.find("fillTypes")
    if fill_types_el is None:
        return {"crops": [], "currentPeriodIdx": current_period_idx, "periodLabels": PERIOD_LABELS_PL}

    crops = []
    for ft_el in fill_types_el.findall("fillType"):
        fill_type = ft_el.get("fillType", "")
        if fill_type not in MAIN_CROPS:
            continue

        history_el = ft_el.find("history")
        if history_el is None:
            continue

        prices = []
        for period in PERIODS:
            p_el = history_el.find(f"period[@period='{period}']")
            prices.append(int(p_el.text) if p_el is not None and p_el.text else 0)

        if not any(prices):
            continue

        current_price = prices[current_period_idx]
        max_price = max(prices)
        min_price = min(prices)
        prev_idx = (current_period_idx - 1) % 12
        next_idx = (current_period_idx + 1) % 12

        if current_price > prices[prev_idx]:
            trend = 'up'
        elif current_price < prices[prev_idx]:
            trend = 'down'
        else:
            trend = 'flat'

        crops.append({
            "type": fill_type,
            "name": CROP_NAMES_PL.get(fill_type, fill_type),
            "emoji": CROP_EMOJIS.get(fill_type, '🌱'),
            "prices": prices,
            "currentPrice": current_price,
            "nextPrice": prices[next_idx],
            "maxPrice": max_price,
            "minPrice": min_price,
            "maxPeriodIdx": prices.index(max_price),
            "trend": trend,
        })

    crops.sort(key=lambda x: x["currentPrice"], reverse=True)

    return {
        "crops": crops,
        "currentPeriodIdx": current_period_idx,
        "currentPeriodLabel": PERIOD_LABELS_PL[current_period_idx],
        "periodLabels": PERIOD_LABELS_PL,
    }
