"""
tools/weather_tool.py
Live weather lookup using Open-Meteo (https://open-meteo.com/) -- a free,
no-API-key-required weather API. This makes the project "ready to work"
out of the box without forcing you to sign up for anything just to demo it.

If you later want OpenWeatherMap instead, swap the implementation but
keep the function signature the same so the agent layer doesn't change.
"""

import requests
from config import DEFAULT_LAT, DEFAULT_LON


def get_weather(latitude: float = DEFAULT_LAT, longitude: float = DEFAULT_LON) -> dict:
    """
    Fetch current weather and a 3-day forecast for a given location.

    Args:
        latitude: Latitude of the farm location.
        longitude: Longitude of the farm location.

    Returns:
        dict with current conditions and a short forecast, in a format
        that's easy for both the LLM and the UI to consume.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": 3,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        raw = resp.json()

        current = raw.get("current", {})
        daily = raw.get("daily", {})

        forecast = []
        dates = daily.get("time", [])
        tmax = daily.get("temperature_2m_max", [])
        tmin = daily.get("temperature_2m_min", [])
        rain_prob = daily.get("precipitation_probability_max", [])

        for i in range(len(dates)):
            forecast.append({
                "date": dates[i],
                "max_temp_c": tmax[i] if i < len(tmax) else None,
                "min_temp_c": tmin[i] if i < len(tmin) else None,
                "rain_probability_pct": rain_prob[i] if i < len(rain_prob) else None,
            })

        return {
            "status": "success",
            "current": {
                "temperature_c": current.get("temperature_2m"),
                "humidity_pct": current.get("relative_humidity_2m"),
                "precipitation_mm": current.get("precipitation"),
                "wind_speed_kmh": current.get("wind_speed_10m"),
            },
            "forecast_3_day": forecast,
        }
    except requests.RequestException as e:
        return {"status": "error", "message": f"Weather lookup failed: {e}"}
