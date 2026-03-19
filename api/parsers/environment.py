import xml.etree.ElementTree as ET
from pathlib import Path

WEATHER_ICONS = {
    "SUN": "☀️",
    "CLOUDY": "☁️",
    "RAIN": "🌧️",
    "HAIL": "🌨️",
    "SNOW": "❄️",
    "THUNDERSTORM": "⛈️",
    "FOG": "🌫️",
}

# Same order as in economy.py — index 0 = Marzec, 1 = Kwiecień, ...
PERIODS = [
    'EARLY_SPRING', 'MID_SPRING', 'LATE_SPRING',
    'EARLY_SUMMER', 'MID_SUMMER', 'LATE_SUMMER',
    'EARLY_AUTUMN', 'MID_AUTUMN', 'LATE_AUTUMN',
    'EARLY_WINTER', 'MID_WINTER', 'LATE_WINTER',
]


def _period_key(day: int, days_per_period: int) -> str:
    year_length = 12 * days_per_period
    idx = ((day - 1) % year_length) // days_per_period
    return PERIODS[idx]


def parse_environment(save_path: Path) -> dict:
    xml_file = save_path / "environment.xml"
    if not xml_file.exists():
        return {}

    tree = ET.parse(xml_file)
    root = tree.getroot()

    day_time_sec = float(root.findtext("dayTime", "0"))
    current_day = int(root.findtext("currentDay", "1"))
    days_per_period = int(root.findtext("daysPerPeriod", "3"))

    time_str = _seconds_to_hhmm(day_time_sec)
    current_period_key = _period_key(current_day, days_per_period)

    weather_el = root.find("weather")
    wetness = 0.0
    snow_height = 0.0
    current_weather = "SUN"
    forecast = []

    if weather_el is not None:
        ground_el = weather_el.find("ground")
        if ground_el is not None:
            wetness = float(ground_el.get("wetness", 0))

        snow_el = weather_el.find("snow")
        if snow_el is not None:
            snow_height = float(snow_el.get("height", 0))

        forecast_el = weather_el.find("forecast")
        if forecast_el is not None:
            instances = []
            for inst in forecast_el.findall("instance"):
                type_name = inst.get("typeName", "SUN")
                start_day = int(inst.get("startDay", current_day))
                start_ms = int(inst.get("startDayTime", 0))
                duration_ms = int(inst.get("duration", 0))
                start_sec = start_ms / 1000
                instances.append({
                    "day": start_day,
                    "typeName": type_name,
                    "startSec": start_sec,
                    "endSec": start_sec + duration_ms / 1000,
                    "durationSec": duration_ms / 1000,
                    "season": inst.get("season", ""),
                })

            # Determine current weather: last instance that has already started
            for inst in sorted(instances, key=lambda x: (x["day"], x["startSec"])):
                if inst["day"] < current_day:
                    current_weather = inst["typeName"]
                elif inst["day"] == current_day and inst["startSec"] <= day_time_sec:
                    current_weather = inst["typeName"]

            # Build per-day forecast (dominant weather by total duration)
            by_day: dict[int, list] = {}
            for inst in instances:
                by_day.setdefault(inst["day"], []).append(inst)

            for day in sorted(by_day.keys()):
                entries = by_day[day]
                counts: dict[str, float] = {}
                for e in entries:
                    counts[e["typeName"]] = counts.get(e["typeName"], 0) + e["durationSec"]
                dominant = max(counts, key=counts.get)
                forecast.append({
                    "day": day,
                    "typeName": dominant,
                    "icon": WEATHER_ICONS.get(dominant, "🌤️"),
                    "periodKey": _period_key(day, days_per_period),
                    "season": entries[0]["season"],
                })

    return {
        "currentDay": current_day,
        "dayTime": time_str,
        "dayTimeSec": day_time_sec,
        "daysPerPeriod": days_per_period,
        "currentPeriodKey": current_period_key,
        "currentWeather": current_weather,
        "currentWeatherIcon": WEATHER_ICONS.get(current_weather, "🌤️"),
        "wetness": round(wetness * 100, 1),
        "snowHeight": round(snow_height, 2),
        "forecast": forecast,
    }


def _seconds_to_hhmm(seconds: float) -> str:
    total = int(seconds)
    hours = (total // 3600) % 24
    minutes = (total % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"
