"""
Health advisory layer, powered by the Gemini API (Google).

Given a station's current reading (+ optional forecast context) and a user
question, produces a grounded, India-context health recommendation. Falls
back to a deterministic rule-based advisory if no GEMINI_API_KEY is set, so
the rest of the app remains demoable without a key.

Uses the raw REST endpoint (no SDK dependency) since it's a single call and
keeps requirements.txt lean:
  POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key=...

Model defaults to "gemini-flash-latest" - an auto-updating alias Google
points at their current recommended Flash model, so this keeps working as
new Gemini versions roll out without needing a code change. Pin a specific
version (e.g. "gemini-2.5-flash") via GEMINI_MODEL in .env if you'd rather
control upgrades yourself.
"""
from __future__ import annotations

import os
from typing import Optional

import httpx

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def _get_api_key() -> Optional[str]:
    return os.environ.get("GEMINI_API_KEY")


RULE_BASED_ADVICE = {
    "Good": "Air quality is good. Fine for outdoor activity, including for sensitive groups.",
    "Satisfactory": "Air quality is acceptable. Unusually sensitive individuals should consider limiting prolonged outdoor exertion.",
    "Moderate": "Sensitive groups (children, elderly, those with asthma or heart conditions) should reduce prolonged outdoor exertion.",
    "Poor": "Everyone should reduce prolonged outdoor exertion. Sensitive groups should avoid it. Consider wearing an N95 mask outdoors.",
    "Very Poor": "Avoid outdoor physical activity. Sensitive groups should stay indoors. Use an air purifier indoors if available.",
    "Severe": "Stay indoors. Avoid all outdoor exertion. Wear an N95/N99 mask if you must go out. Seek medical attention if experiencing breathing difficulty.",
}


def _rule_based(reading: dict, question: Optional[str]) -> str:
    label = reading["category"]["label"]
    base = RULE_BASED_ADVICE.get(label, RULE_BASED_ADVICE["Moderate"])
    return (
        f"{reading['station_name']}, {reading['area']}: AQI {reading['aqi']} ({label}). {base}\n\n"
        "(This is a rule-based fallback response - set GEMINI_API_KEY on the backend "
        "for Gemini-generated, question-aware advisories.)"
    )


SYSTEM_PROMPT = """You are a public health advisory assistant embedded in an Indian \
urban air quality platform. You are given a live/forecast AQI reading (Indian CPCB \
0-500 scale) for a specific district and a user's question. Give clear, practical, \
non-alarmist health guidance grounded in the actual numbers provided. Consider \
sensitive groups (children, elderly, pregnant people, those with asthma/COPD/heart \
disease) explicitly when relevant. Keep responses under 120 words unless the user \
asks for more detail. Do not invent AQI numbers beyond what's given. If asked about \
something you cannot answer from the data provided (e.g. hyperlocal traffic), say so \
briefly rather than guessing."""


async def get_advisory(reading: dict, question: Optional[str] = None, forecast_summary: Optional[str] = None) -> str:
    api_key = _get_api_key()
    if not api_key:
        return _rule_based(reading, question)

    model = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
    context = (
        f"Location: {reading['station_name']}, {reading['area']}\n"
        f"Current AQI: {reading['aqi']} ({reading['category']['label']})\n"
        f"PM2.5: {reading.get('pm25', 'n/a')} ug/m3, PM10: {reading.get('pm10', 'n/a')} ug/m3\n"
        f"NO2: {reading.get('no2', 'n/a')} ppb, SO2: {reading.get('so2', 'n/a')} ppb, "
        f"CO: {reading.get('co', 'n/a')} ppb, O3: {reading.get('o3', 'n/a')} ppb\n"
    )
    if forecast_summary:
        context += f"Forecast trend: {forecast_summary}\n"

    user_question = question or "What health precautions should I take right now?"

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": f"{context}\nUser question: {user_question}"}]}],
        "generationConfig": {"maxOutputTokens": 350, "temperature": 0.4},
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{GEMINI_API_BASE}/{model}:generateContent",
                params={"key": api_key},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return _rule_based(reading, question)
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "\n".join(p.get("text", "") for p in parts).strip()
            return text or _rule_based(reading, question)
    except Exception:
        return _rule_based(reading, question)
