"""
tools/weather_tool.py
Fetches live weather data from Open-Meteo (free, no API key required).
Defaults to Madanapalle, AP coordinates from config.
"""

import requests
from typing import Dict, Any

from config import DEFAULT_LAT, DEFAULT_LON, DEFAULT_LOCATION


def get_weather(lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON) -> Dict[str, Any]:
    """
    Return a dict with current weather for the given coordinates.
    Keys: temperature_c, humidity_pct, rainfall_mm, windspeed_kmh,
          description, location, advice
    """
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,"
        "precipitation,windspeed_10m,weathercode"
        "&timezone=Asia%2FKolkata"
    )
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        c = data["current"]

        temp = c["temperature_2m"]
        humidity = c["relative_humidity_2m"]
        rain = c["precipitation"]
        wind = c["windspeed_10m"]
        code = c["weathercode"]

        description = _wmo_description(code)
        advice = _farming_advice(temp, humidity, rain)

        return {
            "location": DEFAULT_LOCATION,
            "temperature_c": temp,
            "humidity_pct": humidity,
            "rainfall_mm": rain,
            "windspeed_kmh": wind,
            "description": description,
            "farming_advice": advice,
        }
    except requests.RequestException as e:
        return {"error": f"Weather fetch failed: {e}"}


def _wmo_description(code: int) -> str:
    """Map WMO weather-code to a human-readable string."""
    wmo = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Icy fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall",
        80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail",
    }
    return wmo.get(code, f"Weather code {code}")


def _farming_advice(temp: float, humidity: float, rain: float) -> str:
    """Generate a simple farming advisory based on current conditions."""
    tips = []
    if rain > 5:
        tips.append("Heavy rain expected — delay pesticide/fertilizer application.")
    elif rain > 0:
        tips.append("Light rain — good natural irrigation, check for waterlogging.")
    else:
        tips.append("No rain today — ensure crops are adequately irrigated.")

    if humidity > 80:
        tips.append("High humidity increases fungal disease risk — monitor crops closely.")
    elif humidity < 40:
        tips.append("Low humidity — water stress possible, irrigate if needed.")

    if temp > 38:
        tips.append("Extreme heat — avoid field work during noon; mulch to retain moisture.")
    elif temp < 15:
        tips.append("Cool temperatures — watch for frost-sensitive crops.")

    return " ".join(tips)
