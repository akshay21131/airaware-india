"""
Weather layer, powered by Open-Meteo (https://open-meteo.com) - free, no API
key required, used purely for the hero weather widget (temperature, humidity,
wind, condition) to match the reference design. Falls back to a plausible
seasonal estimate if the request fails, same spirit as the AQI fallback.
"""
from __future__ import annotations

import random
from datetime import datetime

import httpx

OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"

# WMO weather codes (used by Open-Meteo) collapsed into a handful of
# human-readable conditions for display.
_WMO_CONDITIONS = {
    0: "Clear", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Fog", 48: "Fog",
    51: "Light Drizzle", 53: "Drizzle", 55: "Heavy Drizzle",
    61: "Light Rain", 63: "Rain", 65: "Heavy Rain",
    71: "Light Snow", 73: "Snow", 75: "Heavy Snow",
    80: "Rain Showers", 81: "Rain Showers", 82: "Violent Showers",
    95: "Thunderstorm", 96: "Thunderstorm Hail", 99: "Thunderstorm Hail",
}


def _condition_for_code(code: int) -> str:
    return _WMO_CONDITIONS.get(code, "Variable")


def _seasonal_fallback(lat: float, month: int) -> dict:
    """Rough climatological fallback if Open-Meteo is unreachable."""
    # Very rough India-wide seasonal temperature curve, warmer for lower latitude.
    base_by_month = {1: 20, 2: 23, 3: 28, 4: 33, 5: 36, 6: 34, 7: 31, 8: 30, 9: 30, 10: 28, 11: 24, 12: 20}
    temp = base_by_month.get(month, 28) - max(0, (lat - 15)) * 0.3
    return {
        "temp_c": round(temp + random.gauss(0, 2), 1),
        "condition": "Clear" if month in (3, 4, 5) else ("Rain" if month in (7, 8) else "Partly Cloudy"),
        "humidity": 55,
        "wind_kmh": 8.0,
        "uv_index": 5.0,
        "source": "seasonal-estimate",
    }


async def fetch_weather(lat: float, lon: float) -> dict:
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(
                OPEN_METEO_BASE,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                    "daily": "uv_index_max",
                    "timezone": "auto",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            current = data.get("current", {})
            daily = data.get("daily", {})
            uv_list = daily.get("uv_index_max", [])
            return {
                "temp_c": current.get("temperature_2m"),
                "condition": _condition_for_code(current.get("weather_code", -1)),
                "humidity": current.get("relative_humidity_2m"),
                "wind_kmh": current.get("wind_speed_10m"),
                "uv_index": uv_list[0] if uv_list else None,
                "source": "open-meteo-live",
            }
    except Exception:
        return _seasonal_fallback(lat, datetime.now().month)
