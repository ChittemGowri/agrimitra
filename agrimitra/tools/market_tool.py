"""
tools/market_tool.py
Returns current mandi (wholesale market) prices for tracked crops.

Strategy (tiered):
  1. Try the data.gov.in Agmarknet API (live, free, no key needed for
     commodity search).
  2. If that fails (network, quota, etc.), fall back to a curated
     baseline table that reflects realistic Madanapalle-region prices.

Returns a dict suitable for the Market Agent to narrate.
"""

import datetime
import random
import requests
from typing import Dict, Any

from config import TRACKED_CROPS

# ---- Baseline price table (per quintal, INR) ----
# Values are representative for Madanapalle / Chittoor district.
# Randomise slightly to simulate day-to-day fluctuation.
_BASELINE = {
    "Tomato":    (800,  2000),
    "Groundnut": (4500, 6000),
    "Mango":     (2000, 5000),
    "Tamarind":  (6000, 9000),
    "Ragi":      (1800, 2500),
}

_TREND_MSGS = {
    "Tomato":    "Prices volatile — check daily before selling.",
    "Groundnut": "Stable demand; post-harvest dip expected in 3-4 weeks.",
    "Mango":     "Peak season — sell quickly before glut arrives.",
    "Tamarind":  "Off-season stock scarce; prices favourable for sellers.",
    "Ragi":      "Steady government MSP floor provides price security.",
}


def get_market_price(crop: str) -> Dict[str, Any]:
    """
    Return price info for the given crop.
    {
        "crop": str,
        "min_price": int,   # INR per quintal
        "max_price": int,
        "modal_price": int,
        "unit": "INR/quintal",
        "market": str,
        "date": str,
        "trend": str,
        "source": "live" | "baseline",
    }
    """
    crop_title = crop.strip().title()

    # --- attempt live lookup via data.gov.in / Agmarknet ---
    live = _try_agmarknet(crop_title)
    if live:
        return live

    # --- fallback to baseline ---
    low, high = _BASELINE.get(crop_title, (1000, 3000))
    modal = random.randint(int((low + high) * 0.4), int((low + high) * 0.6))
    return {
        "crop": crop_title,
        "min_price": low,
        "max_price": high,
        "modal_price": modal,
        "unit": "INR/quintal",
        "market": "Madanapalle APMC (estimated)",
        "date": datetime.date.today().isoformat(),
        "trend": _TREND_MSGS.get(crop_title, "No trend data available."),
        "source": "baseline",
    }


def _try_agmarknet(crop: str) -> Dict[str, Any] | None:
    """
    Attempt to fetch live price from data.gov.in Agmarknet API.
    Returns None on any failure so the caller can fall through.
    """
    # data.gov.in resource ID for daily mandi prices
    resource_id = "9ef84268-d588-465a-a308-a864a43d0070"
    url = "https://api.data.gov.in/resource/" + resource_id
    params = {
        "api-key": "579b464db66ec23bdd000001cdd3946e44ce4aad38d07d94a3ac5d5",
        "format": "json",
        "filters[State]": "Andhra Pradesh",
        "filters[Commodity]": crop,
        "limit": 5,
    }
    try:
        resp = requests.get(url, params=params, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        records = data.get("records", [])
        if not records:
            return None
        r = records[0]
        return {
            "crop": crop,
            "min_price": int(r.get("Min_x0020_Price", 0)),
            "max_price": int(r.get("Max_x0020_Price", 0)),
            "modal_price": int(r.get("Modal_x0020_Price", 0)),
            "unit": "INR/quintal",
            "market": r.get("Market", "Andhra Pradesh"),
            "date": r.get("Arrival_Date", datetime.date.today().isoformat()),
            "trend": _TREND_MSGS.get(crop, ""),
            "source": "live",
        }
    except Exception:
        return None
