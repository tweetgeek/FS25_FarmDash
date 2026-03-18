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

SEASON_PL = {
    "SPRING": "Wiosna",
    "SUMMER": "Lato",
    "AUTUMN": "Jesień",
    "WINTER": "Zima",
}


def parse_environment(save_path: Path) -> dict:
    xml_file = save_path / "environment.xml"
    if not xml_file.exists():
        return {}

    tree = ET.parse(xml_file)
    root = tree.getroot()

    day_time_sec = float(root.findtext("dayTime", "0"))
    current_day = int(root.findtext("currentDay", "1"))

    time_str = _seconds_to_hhmm(day_time_sec)

    weather_el = root.find("weather")
    wetness = 0.0
    snow_height = 0.0
    current_weather = "SUN"
    forecast = []

    if weather_el is not None:
        time_since_rain = int(weather_el.get("timeSinceLastRain", 0))

        ground_el = weather_el.find("ground")
        if ground_el is not None:
            wetness = float(ground_el.get("wetness", 0))

        snow_el = weather_el.find("snow")
        if snow_el is not None:
            snow_height = float(snow_el.get("height", 0))

        forecast_el = weather_el.find("forecast")
        if forecast_el is not None:
            seen_days = {}
            for inst in forecast_el.findall("instance"):
                type_name = inst.get("typeName", "SUN")
                start_day = int(inst.get("startDay", current_day))
                start_day_time_ms = int(inst.get("startDayTime", 0))
                duration_ms = int(inst.get("duration", 0))
                season = inst.get("season", "")

                # Determine current weather (matches current day/time)
                start_day_time_sec = start_day_time_ms / 1000
                end_day_time_sec = (start_day_time_ms + duration_ms) / 1000

                if start_day == current_day:
                    if start_day_time_sec <= day_time_sec <= end_day_time_sec:
                        current_weather = type_name
                    elif start_day_time_sec <= day_time_sec and start_day == current_day:
                        # Check if this is the latest past entry
                        if not any(
                            f["startDay"] == current_day and f["startDayTimeSec"] <= day_time_sec and f["startDayTimeSec"] > start_day_time_sec
                            for f in forecast
                        ):
                            pass

                # Group by day - pick dominant weather per day
                if start_day not in seen_days:
                    seen_days[start_day] = {
                        "day": start_day,
                        "typeName": type_name,
                        "icon": WEATHER_ICONS.get(type_name, "🌤️"),
                        "season": season,
                        "seasonPl": SEASON_PL.get(season, season),
                        "startDayTimeSec": start_day_time_sec,
                    }

                forecast.append({
                    "day": start_day,
                    "typeName": type_name,
                    "icon": WEATHER_ICONS.get(type_name, "🌤️"),
                    "season": season,
                    "seasonPl": SEASON_PL.get(season, season),
                    "startDayTimeSec": start_day_time_sec,
                    "durationSec": duration_ms / 1000,
                })

    return {
        "currentDay": current_day,
        "dayTime": time_str,
        "dayTimeSec": day_time_sec,
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
