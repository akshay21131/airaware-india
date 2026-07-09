"""
Air quality data fetching layer.

Primary source: OpenAQ API v3 (https://api.openaq.org) - free, no key needed for
low volume use, covers CPCB (Central Pollution Control Board) stations across
India among thousands of stations worldwide.

Fallback: a physically-plausible synthetic generator, used when OpenAQ is
unreachable (rate limited, network down, hackathon wifi, etc). This keeps demos
safe from live-API flakiness while being clearly labeled as such to the caller.
"""
from __future__ import annotations

import asyncio
import json
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import httpx

# Full pan-India district station list, derived from real district-boundary
# polygons (GADM level-2 admin boundaries for India) with lat/lon computed as
# each district's geometric centroid. Every district is tagged with a
# climate/pollution zone (igp, coastal, peninsular, arid, gangetic-delta,
# northeast, central, himalayan) used to drive the synthetic seasonal model
# below. Bundled as JSON rather than inlined here; see app/data/india_districts.json.
_DATA_PATH = Path(__file__).resolve().parent / "data" / "india_districts.json"
with open(_DATA_PATH, encoding="utf-8") as _f:
    INDIA_STATIONS = json.load(_f)

# Backwards-compatible alias used elsewhere in this codebase
NCR_STATIONS = [
    s for s in INDIA_STATIONS
    if s["state"] in ("Delhi", "Uttar Pradesh", "Haryana") and s["zone"] == "igp"
]

OPENAQ_BASE = "https://api.openaq.org/v3"


def aqi_category(aqi: float) -> dict:
    """Map a numeric AQI (Indian CPCB scale, 0-500) to category, color, and advice level."""
    bands = [
        (0, 50, "Good", "#4CAF6D"),
        (50, 100, "Satisfactory", "#A3D977"),
        (100, 200, "Moderate", "#F1C40F"),
        (200, 300, "Poor", "#E67E22"),
        (300, 400, "Very Poor", "#E74C3C"),
        (400, 500, "Severe", "#9B59B6"),
    ]
    for lo, hi, label, color in bands:
        if aqi <= hi:
            return {"label": label, "color": color, "min": lo, "max": hi}
    return {"label": "Severe", "color": "#9B59B6", "min": 400, "max": 500}


# Each Indian climate zone has a distinct seasonal AQI fingerprint. Values are
# illustrative monthly baselines (CPCB AQI, 0-500) grounded in well-documented
# regional patterns, not live measurements.
ZONE_SEASONAL_CURVES = {
    # Indo-Gangetic Plain: worst in the country. Post-monsoon stubble burning
    # (Punjab/Haryana) + winter thermal inversion trap particulates over
    # Delhi-NCR, UP, Bihar, Punjab through Oct-Jan.
    "igp": {1: 320, 2: 240, 3: 180, 4: 165, 5: 175, 6: 190, 7: 110, 8: 95, 9: 120, 10: 260, 11: 380, 12: 340},
    # Coastal cities (Mumbai, Chennai, Kochi, Surat, Vizag): sea breeze aids
    # dispersion; monsoon washout is strong; still degrades a bit in dry winter.
    "coastal": {1: 140, 2: 130, 3: 120, 4: 110, 5: 100, 6: 70, 7: 55, 8: 55, 9: 65, 10: 95, 11: 130, 12: 150},
    # Peninsular interior (Bengaluru, Hyderabad, Pune, Bhubaneswar): moderate,
    # fairly flat, elevation and less industrial density help.
    "peninsular": {1: 110, 2: 105, 3: 100, 4: 95, 5: 90, 6: 70, 7: 60, 8: 60, 9: 70, 10: 90, 11: 105, 12: 115},
    # Arid west (Jaipur, Ahmedabad): dust-driven, hot dry summers spike PM10.
    "arid": {1: 200, 2: 190, 3: 210, 4: 230, 5: 240, 6: 180, 7: 100, 8: 90, 9: 110, 10: 170, 11: 210, 12: 210},
    # Gangetic delta (Kolkata, Howrah): humid, moderate-poor, brick kiln belt.
    "gangetic-delta": {1: 220, 2: 190, 3: 160, 4: 140, 5: 130, 6: 100, 7: 75, 8: 70, 9: 90, 10: 150, 11: 210, 12: 230},
    # Northeast (Guwahati): heavy monsoon, generally cleaner air overall.
    "northeast": {1: 130, 2: 120, 3: 110, 4: 100, 5: 90, 6: 60, 7: 45, 8: 45, 9: 55, 10: 85, 11: 120, 12: 135},
    # Central India (Bhopal, Nagpur, Raipur): industrial/mining belt, moderate.
    "central": {1: 170, 2: 160, 3: 150, 4: 145, 5: 150, 6: 120, 7: 80, 8: 75, 9: 90, 10: 130, 11: 165, 12: 175},
    # Himalayan belt (J&K, Himachal Pradesh, Uttarakhand): generally the
    # cleanest air in the country; some wood/biomass-burning haze in winter,
    # heavy monsoon washout in summer.
    "himalayan": {1: 95, 2: 90, 3: 85, 4: 80, 5: 75, 6: 60, 7: 50, 8: 50, 9: 55, 10: 70, 11: 90, 12: 100},
}


def _seasonal_base(dt: datetime, zone: str = "igp") -> float:
    """
    Return a plausible baseline AQI for the given date and climate zone.
    Superimposes a diurnal (time-of-day) swing on top of the monthly curve:
    pollution peaks in the early morning/night due to thermal inversion and
    dips around midday as the boundary layer mixes out.
    """
    curve = ZONE_SEASONAL_CURVES.get(zone, ZONE_SEASONAL_CURVES["igp"])
    base = curve[dt.month]
    hour = dt.hour
    diurnal = 30 * math.cos((hour - 4) / 24 * 2 * math.pi)
    return base + diurnal


def synthetic_reading(station: dict, dt: Optional[datetime] = None) -> dict:
    """Generate one physically-plausible reading for a station at a given time."""
    dt = dt or datetime.now(timezone.utc)
    zone = station.get("zone", "igp")
    base = _seasonal_base(dt, zone)
    # Small station-specific offset for known traffic/industrial hotspots
    hotspot_bonus = {
        "anand-vihar": 35, "ito": 20, "punjabi-bagh": 15, "rohini": 10,
        "ghaziabad-vasundhara": 25, "lucknow-talkatora": 15, "kanpur-nehru-nagar": 20,
        "howrah-ghusuri": 20, "ahmedabad-airport": 15,
    }
    base += hotspot_bonus.get(station["id"], 0)
    noise = random.gauss(0, 18)
    aqi = max(15, min(480, base + noise))
    return {
        "station_id": station["id"],
        "station_name": station["name"],
        "area": station["area"],
        "lat": station["lat"],
        "lon": station["lon"],
        "timestamp": dt.isoformat(),
        "aqi": round(aqi),
        **derive_pollutants(aqi),
        "category": aqi_category(aqi),
        "source": "synthetic-fallback",
    }


def derive_pollutants(aqi: float, overrides: Optional[dict] = None) -> dict:
    """
    Estimate the full six-pollutant panel (PM2.5, PM10, CO, SO2, NO2, O3) from
    a single AQI value, using rough ratios typical of Indian urban readings
    (calibrated loosely against public CPCB station data). overrides lets a
    live-data caller substitute any pollutant it actually measured while
    filling in the rest, so the UI always has all six fields populated.
    """
    est = {
        "pm25": round(aqi * 0.62, 1),
        "pm10": round(aqi * 0.92, 1),
        "co": round(max(2, aqi * 1.15 + random.gauss(0, 8)), 1),
        "so2": round(max(1, aqi * 0.05 + random.gauss(0, 2)), 1),
        "no2": round(max(2, aqi * 0.14 + random.gauss(0, 4)), 1),
        "o3": round(max(3, aqi * 0.17 + random.gauss(0, 5)), 1),
    }
    if overrides:
        est.update({k: v for k, v in overrides.items() if v is not None})
    return est


# Caps how many concurrent outbound OpenAQ requests are in flight at once.
# With hundreds of districts, firing every request simultaneously is both rude
# to OpenAQ and slower in practice than a bounded pool (connection/DNS/TLS setup
# overhead dominates past a few dozen concurrent sockets).
_OPENAQ_CONCURRENCY = asyncio.Semaphore(40)


async def fetch_live_reading(station: dict) -> dict:
    """
    Try OpenAQ v3 for a real recent measurement near the station's coordinates.
    Falls back to the synthetic generator on any failure (network, rate limit,
    no nearby sensor, schema change, etc) so the API never hard-fails a demo.
    """
    async with _OPENAQ_CONCURRENCY:
        return await _fetch_live_reading_inner(station)


async def _fetch_live_reading_inner(station: dict) -> dict:
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(
                f"{OPENAQ_BASE}/locations",
                params={
                    "coordinates": f"{station['lat']},{station['lon']}",
                    "radius": 15000,
                    "limit": 1,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            if not results:
                raise ValueError("no nearby OpenAQ sensor")
            location_id = results[0]["id"]

            resp2 = await client.get(f"{OPENAQ_BASE}/locations/{location_id}/latest")
            resp2.raise_for_status()
            latest = resp2.json().get("results", [])
            if not latest:
                raise ValueError("no latest measurement")

            def _param(name: str) -> Optional[float]:
                return next(
                    (m["value"] for m in latest if m.get("parameter", {}).get("name") == name),
                    None,
                )

            pm25_val = _param("pm25")
            if pm25_val is None:
                raise ValueError("no pm25 in latest")

            aqi = round(pm25_val * 2.1)  # rough PM2.5 -> Indian AQI approximation
            live_overrides = {
                "pm25": round(pm25_val, 1),
                "pm10": _param("pm10"),
                "co": _param("co"),
                "so2": _param("so2"),
                "no2": _param("no2"),
                "o3": _param("o3"),
            }
            return {
                "station_id": station["id"],
                "station_name": station["name"],
                "area": station["area"],
                "lat": station["lat"],
                "lon": station["lon"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "aqi": aqi,
                **derive_pollutants(aqi, overrides=live_overrides),
                "category": aqi_category(aqi),
                "source": "openaq-live",
            }
    except Exception:
        return synthetic_reading(station)


def historical_series(station: dict, days: int = 30) -> list[dict]:
    """Generate days of hourly synthetic history for model training/backtesting."""
    now = datetime.now(timezone.utc)
    series = []
    for h in range(days * 24, 0, -1):
        dt = now - timedelta(hours=h)
        series.append(synthetic_reading(station, dt))
    return series
