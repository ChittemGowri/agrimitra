"""
tools/market_tool.py
Mandi (market) price lookup for the Market Agent.

NOTE ON DATA SOURCE: India has government mandi price data via the
data.gov.in "Variety-wise Daily Market Prices" API, but it requires a
free API key and the schema changes occasionally. To keep this project
"clone-and-run" without forcing a sign-up just to see it work, this
tool ships with a realistic LOCAL price model for crops common to the
Madanapalle / Chittoor region, clearly labeled as simulated baseline
data with realistic seasonal variation.

TO USE REAL LIVE DATA (recommended before a final demo/judging):
1. Get a free key at https://data.gov.in/
2. Set DATA_GOV_API_KEY in your .env
3. Set USE_LIVE_MANDI_DATA = True below
The fetch_live_mandi_price() function is already wired up for this --
just supply the key and flip the flag.
"""

import os
import random
import datetime
import requests

USE_LIVE_MANDI_DATA = bool(os.getenv("DATA_GOV_API_KEY", ""))

# Baseline prices (INR per quintal) representative of Chittoor district
# mandis as of mid-2026, with typical seasonal volatility ranges.
_BASELINE_PRICES = {
    "Tomato":     {"min": 800,  "max": 2800, "typical": 1500, "volatility": "high"},
    "Groundnut":  {"min": 5200, "max": 6800, "typical": 5900, "volatility": "medium"},
    "Mango":      {"min": 1200, "max": 4500, "typical": 2600, "volatility": "high"},
    "Tamarind":   {"min": 7000, "max": 11000, "typical": 9000, "volatility": "low"},
    "Ragi":       {"min": 3200, "max": 3800, "typical": 3450, "volatility": "low"},
}


def fetch_live_mandi_price(crop: str) -> dict | None:
    """Queries the official data.gov.in API for live Mandi price data in Andhra Pradesh."""
    api_key = os.getenv("DATA_GOV_API_KEY", "")
    if not api_key:
        return None

    url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    params = {
        "api-key": api_key,
        "format": "json",
        "limit": 50,
        "filters[state]": "Andhra Pradesh",
        "filters[commodity]": crop,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        records = data.get("records", [])
        if not records:
            return None

        # Filter for Chittoor district if available, otherwise use any AP record
        local_records = [r for r in records if r.get("district", "").lower() == "chittoor"]
        if not local_records:
            local_records = records

        record = local_records[0]
        min_p = int(record.get("min_price", 0))
        max_p = int(record.get("max_price", 0))
        modal_p = int(record.get("modal_price", 0))
        market = record.get("market", "AP Mandi")
        variety = record.get("variety", "Standard")

        span = max_p - min_p
        position = (modal_p - min_p) / span if span else 0.5

        if position >= 0.7:
            recommendation = f"SELL — price at {market} Mandi is in the upper range of the recent season."
        elif position <= 0.3:
            recommendation = f"HOLD if possible — price at {market} Mandi is low; consider waiting."
        else:
            recommendation = f"NEUTRAL — price at {market} Mandi is near typical average."

        return {
            "status": "success",
            "source": f"data.gov.in API ({market} Mandi - {variety})",
            "crop": crop,
            "date": record.get("arrival_date", datetime.date.today().isoformat()),
            "price_inr_per_quintal": modal_p,
            "typical_range": {"min": min_p, "max": max_p},
            "volatility": "live",
            "recommendation": recommendation,
        }
    except Exception:
        # Fallback to simulation if network or API error occurs
        return None



def get_market_price(crop: str) -> dict:
    """
    Get current mandi (market) price information for a crop, plus a
    simple sell/hold recommendation based on where today's simulated
    price sits within the crop's typical seasonal range.

    Args:
        crop: Crop name, e.g. "Tomato", "Groundnut", "Mango".

    Returns:
        dict with price info and a recommendation the agent can reason over.
    """
    crop_key = crop.strip().title()
    if crop_key not in _BASELINE_PRICES:
        return {
            "status": "error",
            "message": f"No price data available for '{crop}'. "
                       f"Tracked crops: {list(_BASELINE_PRICES.keys())}",
        }

    live = fetch_live_mandi_price(crop_key)
    if live:
        return live

    info = _BASELINE_PRICES[crop_key]
    # Deterministic-ish daily variation seeded by date so price doesn't
    # jump randomly on every single call within the same day.
    seed = int(datetime.date.today().strftime("%Y%m%d")) + hash(crop_key) % 1000
    rng = random.Random(seed)
    today_price = rng.randint(info["min"], info["max"])

    span = info["max"] - info["min"]
    position = (today_price - info["min"]) / span if span else 0.5

    if position >= 0.7:
        recommendation = "SELL — price is in the upper range of the recent season."
    elif position <= 0.3:
        recommendation = "HOLD if possible — price is on the lower end; consider waiting."
    else:
        recommendation = "NEUTRAL — price is near typical seasonal average."

    return {
        "status": "success",
        "source": "simulated_baseline (set DATA_GOV_API_KEY for live data)",
        "crop": crop_key,
        "date": datetime.date.today().isoformat(),
        "price_inr_per_quintal": today_price,
        "typical_range": {"min": info["min"], "max": info["max"]},
        "volatility": info["volatility"],
        "recommendation": recommendation,
    }
