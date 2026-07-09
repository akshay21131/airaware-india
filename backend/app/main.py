"""
AirAware India - FastAPI backend.

Endpoints:
  GET  /api/stations                   -> list of all monitored districts
  GET  /api/aqi/current                -> current reading for every district (map layer)
  GET  /api/aqi/current/{station_id}   -> current reading for one district
  GET  /api/aqi/forecast/{station_id}?hours=72 -> forecast series, anchored on live reading
  GET  /api/weather/{station_id}       -> live weather (Open-Meteo)
  GET  /api/government/{station_id}     -> GRAP government-action stage for current AQI
  GET  /api/ranking?limit=15           -> most-polluted districts right now
  POST /api/chat                       -> Gemini-powered health advisory
  POST /api/train                      -> (re)train the forecasting model

Run locally:
  uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

import asyncio
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .data_fetcher import INDIA_STATIONS, fetch_live_reading, synthetic_reading
from . import ml_model
from .advisor import get_advisory
from .weather import fetch_weather
from .grap import get_grap_stage

load_dotenv()

app = FastAPI(title="AirAware India", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your deployed frontend origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)

_STATIONS_BY_ID = {s["id"]: s for s in INDIA_STATIONS}


def _get_station_or_404(station_id: str) -> dict:
    station = _STATIONS_BY_ID.get(station_id)
    if not station:
        raise HTTPException(404, f"Unknown station_id '{station_id}'")
    return station


@app.get("/api/stations")
def list_stations():
    return {"stations": INDIA_STATIONS, "count": len(INDIA_STATIONS)}


@app.get("/api/aqi/current")
async def current_all(live: bool = False):
    """
    Current readings for every district (for the national map view).

    Defaults to the synthetic estimator for ALL districts, which is instant.
    Setting live=true attempts a real OpenAQ lookup per district (2 sequential
    HTTP calls each) - correct, but 30-45s for the full list since OpenAQ's
    India coverage is sparse and most calls fall through to the same synthetic
    fallback anyway. Individual station endpoints (current_one, forecast, chat,
    weather, government) always try live data first regardless of this flag,
    since drilling into one district is fast.
    """
    if live:
        readings = await asyncio.gather(*(fetch_live_reading(s) for s in INDIA_STATIONS))
    else:
        readings = [synthetic_reading(s) for s in INDIA_STATIONS]
    return {"readings": readings, "count": len(readings), "mode": "live" if live else "synthetic"}


@app.get("/api/aqi/current/{station_id}")
async def current_one(station_id: str):
    station = _get_station_or_404(station_id)
    return await fetch_live_reading(station)


@app.get("/api/aqi/forecast/{station_id}")
async def forecast_one(station_id: str, hours: int = 72):
    station = _get_station_or_404(station_id)
    hours = max(1, min(hours, 168))
    # Anchor the forecast on the live/fallback reading so it starts from the
    # true current value rather than a purely synthetic seed point.
    current_reading = await fetch_live_reading(station)
    forecast = ml_model.forecast(station, hours=hours, current_reading=current_reading)
    return {"station_id": station_id, "current": current_reading, "forecast": forecast}


@app.get("/api/weather/{station_id}")
async def weather_one(station_id: str):
    station = _get_station_or_404(station_id)
    return await fetch_weather(station["lat"], station["lon"])


@app.get("/api/government/{station_id}")
async def government_one(station_id: str):
    """
    GRAP-based government action stage for this district's current AQI.
    GRAP is Delhi-NCR's actual legal mechanism (run by CAQM) - see grap.py
    for the jurisdiction note. Shown here as a reference framework nationally.
    """
    station = _get_station_or_404(station_id)
    reading = await fetch_live_reading(station)
    stage = get_grap_stage(reading["aqi"])
    return {"station_id": station_id, "aqi": reading["aqi"], "grap_stage": stage}


@app.get("/api/ranking")
async def ranking(limit: int = 15, live: bool = False):
    """Most polluted districts right now, across all monitored districts."""
    limit = max(1, min(limit, 100))
    if live:
        readings = await asyncio.gather(*(fetch_live_reading(s) for s in INDIA_STATIONS))
    else:
        readings = [synthetic_reading(s) for s in INDIA_STATIONS]
    ranked = sorted(readings, key=lambda r: r["aqi"], reverse=True)[:limit]
    return {"ranking": ranked, "count": len(ranked), "mode": "live" if live else "synthetic"}


@app.post("/api/train")
def train_model():
    metrics = ml_model.train()
    ml_model._bundle_cache = None  # force reload on next forecast call
    return {"status": "trained", **metrics}


class ChatRequest(BaseModel):
    station_id: str
    question: Optional[str] = None


@app.post("/api/chat")
async def chat(req: ChatRequest):
    station = _get_station_or_404(req.station_id)
    reading = await fetch_live_reading(station)
    forecast = ml_model.forecast(station, hours=24, current_reading=reading)
    trend_first, trend_last = forecast[0]["aqi"], forecast[-1]["aqi"]
    trend_summary = f"AQI expected to go from {trend_first} to {trend_last} over next 24h"
    answer = await get_advisory(reading, question=req.question, forecast_summary=trend_summary)
    return {"reading": reading, "advisory": answer}


@app.get("/api/health")
def health():
    return {"status": "ok"}
