"""Pure-Python forecasting layer (no pandas/numpy/sklearn — crash-proof)."""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Optional

from .data_fetcher import INDIA_STATIONS, aqi_category, _seasonal_base

_bundle_cache: Optional[dict] = None


def train(*_args, **_kwargs) -> dict:
    return {
        "status": "ok",
        "method": "analytic-seasonal (pure python, no ML deps)",
        "total_stations": len(INDIA_STATIONS),
    }


def _hotspot_bonus(station_id: str) -> int:
    return {
        "anand-vihar": 35, "ito": 20, "punjabi-bagh": 15, "rohini": 10,
        "ghaziabad-vasundhara": 25, "lucknow-talkatora": 15,
        "kanpur-nehru-nagar": 20, "howrah-ghusuri": 20, "ahmedabad-airport": 15,
    }.get(station_id, 0)


def forecast(station: dict, hours: int = 72, current_reading: Optional[dict] = None) -> list[dict]:
    zone = station.get("zone", "igp")
    hotspot = _hotspot_bonus(station["id"])
    now = datetime.now(timezone.utc)

    if current_reading is not None and "aqi" in current_reading:
        base_now = _seasonal_base(now, zone) + hotspot
        offset = current_reading["aqi"] - base_now
    else:
        offset = 0.0

    results = []
    drift = 0.0
    for step in range(1, hours + 1):
        ts = now + timedelta(hours=step)
        base = _seasonal_base(ts, zone) + hotspot
        decay = max(0.0, 1.0 - step / 48.0)
        anchored = base + offset * decay
        drift = drift * 0.8 + random.gauss(0, 3.5)
        value = max(10, min(490, anchored + drift))
        results.append({
            "timestamp": ts.isoformat(),
            "aqi": round(value),
            "category": aqi_category(value),
        })
    return results
