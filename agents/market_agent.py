"""
agents/market_agent.py
The Market Agent: combines live weather data with mandi price data to
give a simple, combined sell/hold + field-work recommendation.
"""

from config import DEFAULT_LAT, DEFAULT_LON
from tools.weather_tool import get_weather
from tools.market_tool import get_market_price
from utils.logger import AgentTrace

AGENT_NAME = "MarketAgent"


def run_market_check(crop: str, trace: AgentTrace,
                      latitude: float = DEFAULT_LAT, longitude: float = DEFAULT_LON) -> dict:
    trace.log(AGENT_NAME, "plan", f"Checking weather and mandi price for crop='{crop}'")

    trace.log(AGENT_NAME, "tool_call", "get_weather(latitude, longitude)")
    weather = get_weather(latitude, longitude)
    if weather.get("status") == "success":
        trace.log(
            AGENT_NAME, "tool_result",
            f"Current temp {weather['current']['temperature_c']}°C, "
            f"humidity {weather['current']['humidity_pct']}%"
        )
    else:
        trace.log(AGENT_NAME, "error", weather.get("message", "Weather lookup failed."))

    trace.log(AGENT_NAME, "tool_call", f"get_market_price('{crop}')")
    price = get_market_price(crop)
    if price.get("status") == "success":
        trace.log(
            AGENT_NAME, "tool_result",
            f"₹{price['price_inr_per_quintal']}/quintal — {price['recommendation']}"
        )
    else:
        trace.log(AGENT_NAME, "error", price.get("message", "Price lookup failed."))

    # Combine into one farmer-facing recommendation
    field_work_note = None
    if weather.get("status") == "success":
        upcoming_rain = any(
            (d.get("rain_probability_pct") or 0) >= 60
            for d in weather.get("forecast_3_day", [])
        )
        if upcoming_rain:
            field_work_note = (
                "Rain likely in the next 3 days — avoid spraying now; "
                "it will wash off. Plan any spraying for a dry window."
            )
        else:
            field_work_note = "No significant rain expected in the next 3 days — safe window for spraying if needed."

    trace.log(AGENT_NAME, "final", "Market + weather check complete.")

    return {
        "status": "success",
        "weather": weather,
        "price": price,
        "field_work_note": field_work_note,
    }
