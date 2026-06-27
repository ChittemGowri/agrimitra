"""
agents/market_agent.py
Combines live weather and mandi price data, then uses the NVIDIA NIM
text model to give a sell/hold recommendation.
"""

from openai import OpenAI

from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, TEXT_MODEL
from tools.weather_tool import get_weather
from tools.market_tool import get_market_price
from utils.logger import AgentTrace


def run(crop: str, trace: AgentTrace | None = None) -> str:
    """
    Fetch weather + price for the given crop and synthesise a
    sell/hold/wait recommendation.
    """
    if not NVIDIA_API_KEY:
        return "⚠️ NVIDIA_API_KEY not set — Market Agent cannot run."

    if trace:
        trace.add("tool_call", "Market Agent → Weather API",
                  "Fetching live weather from Open-Meteo for Madanapalle…")

    weather = get_weather()

    if trace:
        if "error" in weather:
            trace.add("tool_result", "Weather", f"Error: {weather['error']}")
        else:
            trace.add("tool_result", "Weather",
                      f"🌡 {weather['temperature_c']}°C | 💧 {weather['humidity_pct']}% RH | "
                      f"🌧 {weather['rainfall_mm']} mm rain | {weather['description']}")

    if trace:
        trace.add("tool_call", "Market Agent → Price API",
                  f"Looking up mandi price for **{crop}**…")

    price = get_market_price(crop)

    if trace:
        src = price.get("source", "baseline")
        trace.add("tool_result", "Price Data",
                  f"Modal price: ₹{price.get('modal_price')} | "
                  f"Range: ₹{price.get('min_price')}–₹{price.get('max_price')} per quintal | "
                  f"Source: {src}")

    # Synthesise recommendation using the LLM
    weather_summary = (
        f"Temperature: {weather.get('temperature_c')}°C, "
        f"Humidity: {weather.get('humidity_pct')}%, "
        f"Rainfall: {weather.get('rainfall_mm')} mm, "
        f"Conditions: {weather.get('description')}. "
        f"Farming note: {weather.get('farming_advice', '')}"
        if "error" not in weather
        else f"Weather data unavailable: {weather.get('error')}"
    )

    price_summary = (
        f"{crop} price at {price.get('market')}: "
        f"₹{price.get('min_price')}–₹{price.get('max_price')} per quintal "
        f"(modal ₹{price.get('modal_price')}). "
        f"Trend: {price.get('trend')}. "
        f"Data as of {price.get('date')} [{price.get('source')}]."
    )

    system_prompt = (
        "You are AgriMitra's Market Agent — a practical commodity advisor for "
        "smallholder farmers in Andhra Pradesh. "
        "Given real-time weather and mandi price data, decide clearly whether "
        "the farmer should SELL NOW, HOLD for a better price, or WAIT for "
        "conditions to improve. Justify in 2-3 sentences. Be direct."
    )

    user_prompt = (
        f"Crop: {crop}\n"
        f"Weather: {weather_summary}\n"
        f"Price: {price_summary}\n\n"
        "Should the farmer sell now or wait? Give a clear recommendation."
    )

    client = OpenAI(base_url=NVIDIA_BASE_URL, api_key=NVIDIA_API_KEY)

    if trace:
        trace.add("tool_call", "Market Agent → LLM Synthesis",
                  f"Generating sell/hold recommendation with **{TEXT_MODEL}**…")

    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=200,
            temperature=0.3,
        )
        recommendation = response.choices[0].message.content.strip()
        if trace:
            trace.add("tool_result", "Market Recommendation", recommendation)
        return (
            f"📈 **Market & Weather Update for {crop}:**\n"
            f"- Modal price: ₹{price.get('modal_price')}/quintal "
            f"(₹{price.get('min_price')}–₹{price.get('max_price')})\n"
            f"- Weather: {weather.get('description', 'N/A')}, "
            f"{weather.get('temperature_c', '?')}°C\n\n"
            f"**Recommendation:** {recommendation}"
        )
    except Exception as e:
        return f"⚠️ Market Agent error: {e}"
