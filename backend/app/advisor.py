"""
Health advisory layer, powered by the Gemini API (Google).

Given a station's current reading plus optional forecast context, this module
produces a grounded, India-specific environmental health advisory. It falls
back to a structured rule-based response when the Gemini API key is not
available or when the API call fails.
"""
from __future__ import annotations

import os
from typing import Any, Optional

import httpx

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_MODEL = "gemini-flash-latest"

INTENT_KEYWORDS = {
    "exercise": [
        "exercise",
        "exercising",
        "workout",
        "gym",
        "jog",
        "jogging",
        "run",
        "running",
        "walk",
        "walking",
        "sport",
        "sports",
        "yoga",
        "cycling",
    ],
    "outdoor activities": [
        "outdoor",
        "outside",
        "play",
        "park",
        "picnic",
        "garden",
        "recreation",
        "playing",
        "go outside",
    ],
    "commuting": ["commute", "travel to work", "office", "road", "drive", "car", "bike", "ride", "metro"],
    "travel": ["travel", "trip", "vacation", "visit", "tour", "journey"],
    "children": ["child", "children", "kid", "kids", "school", "playground"],
    "elderly": ["elderly", "older adult", "senior", "grandparent"],
    "asthma": ["asthma", "wheezing", "breathing", "trigger", "breath"],
    "pregnancy": ["pregnant", "pregnancy", "expecting"],
    "mask": ["mask", "n95", "n99", "respirator", "face mask"],
    "air purifier": ["air purifier", "purifier", "filtration", "filter"],
    "AQI comparison": ["compare", "better than", "worse than", "is it good", "is it bad", "aqi 106", "aqi 150"],
    "pollution improvement": ["improve air quality", "reduce pollution", "clean the air", "how can i improve"],
    "indoor air quality": ["indoor air", "inside", "home air", "ventilation", "ventilate"],
    "weather impact": ["weather", "rain", "wind", "humidity", "temperature", "heat", "cold"],
    "forecast": ["forecast", "tomorrow", "next day", "will it get", "trend", "increasing", "decreasing"],
    "pollutant explanation": ["what does", "what is", "meaning of", "pm2.5", "pm10", "no2", "so2", "co", "o3"],
    "health symptoms": ["cough", "headache", "sore throat", "irritation", "symptom", "symptoms", "difficulty breathing"],
    "emergency": ["emergency", "urgent", "severe", "trouble breathing", "medical attention"],
    "schools": ["school", "classroom", "students", "teacher", "campus"],
    "office workers": ["office", "workplace", "desk", "workspace", "employee"],
}

AQI_CATEGORY_TABLE = (
    "Indian CPCB AQI categories: Good (0-50), Satisfactory (51-100), Moderate (101-200), "
    "Poor (201-300), Very Poor (301-400), Severe (401-500)."
)

SYSTEM_PROMPT = """
You are AirCare AI, an advanced Environmental Health Assistant for India.

You combine the expertise of:
- Pulmonologist
- Environmental Scientist
- Public Health Expert
- CPCB AQI Specialist
- Climate Researcher

Your primary goal is to answer the USER'S QUESTION.

Environmental data should PERSONALIZE your answer, not dominate it.

Rules:

1. Answer the user's question first.

2. Use AQI only where it changes the advice.

3. Never start every answer by repeating the AQI.

4. Never sound like a government report.

5. Never sound robotic.

6. Explain WHY.

7. Speak naturally like an experienced doctor talking to a patient.

8. Use simple English.

9. Never hallucinate.

10. Never invent pollutant values.

11. Mention sensitive groups only if relevant.

12. Give practical advice.

13. If the user asks about exercise,
focus on exercise.

If the user asks about asthma,
focus on asthma.

If the user asks about pollution reduction,
focus on pollution reduction.

14. Keep the answer conversational.

15. Avoid repeating information.

16. If the answer can be personalized using AQI,
do so naturally.

17. If the user asks a medical question,
answer the medical concern first,
then explain how today's AQI affects it.

18. Never answer only Yes or No.

19. Do not mention AQI more than once unless necessary.

20. Sound helpful and reassuring.
"""

FEW_SHOT_EXAMPLES = """

Example 1

User:
I have asthma.
Can I go outside today?
Can my child play outside?
Should I wear a mask today?
Why is PM2.5 dangerous?

Assistant:

Because you have asthma, today's air quality deserves extra attention.

An AQI of 114 falls in the Moderate category.

Many people can spend short periods outdoors safely, but asthma symptoms may worsen even at moderate pollution levels.

Carry your inhaler.

Avoid busy roads.

Avoid intense exercise.

Wear an N95 mask if you'll be outdoors for long.

---------------------------------------

Example 2

User:
Is it safe to exercise?

Assistant:

For most healthy adults, light exercise is acceptable today.

However, because the AQI is moderate, long-distance running or high-intensity workouts may increase your exposure to PM2.5.

Morning hours are generally better than evening if pollution is expected to rise.

---------------------------------------

Example 3

User:

How can I improve air quality?

Assistant:

You cannot significantly reduce city-wide AQI alone, but you can reduce your own exposure and contribute to cleaner air.

Personal Actions
• Use public transport
• Avoid burning waste
• Maintain vehicles

Community Actions
• Plant trees
• Report garbage burning
• Promote clean transport

Government Actions
• Industrial emission control
• Dust suppression
• Public transport investment

"""

def _get_api_key() -> Optional[str]:
    return os.environ.get("GEMINI_API_KEY")


def _coerce_numeric(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def _get_dominant_pollutant(reading: dict) -> str:
    pollutants = {
        "PM2.5": reading.get("pm25"),
        "PM10": reading.get("pm10"),
        "NO2": reading.get("no2"),
        "SO2": reading.get("so2"),
        "CO": reading.get("co"),
        "O3": reading.get("o3"),
    }
    ranked: list[tuple[str, Optional[float]]] = []
    for name, value in pollutants.items():
        ranked.append((name, _coerce_numeric(value)))

    valid = [(name, value) for name, value in ranked if value is not None]
    if not valid:
        return "unclear"

    dominant_name, _ = max(valid, key=lambda item: item[1])
    return dominant_name


def _detect_intent(question: Optional[str]) -> str:

    if not question:
        return "general"

    q = question.lower()

    if any(x in q for x in [
        "asthma",
        "breathing",
        "wheezing",
        "copd",
        "lungs",
        "difficulty breathing"
    ]):
        return "medical"

    elif any(x in q for x in [
        "exercise",
        "gym",
        "walk",
        "run",
        "jog",
        "cycling",
        "play"
    ]):
        return "exercise"

    elif any(x in q for x in [
        "child",
        "kid",
        "school"
    ]):
        return "children"

    elif any(x in q for x in [
        "elderly",
        "senior",
        "old"
    ]):
        return "elderly"

    elif any(x in q for x in [
        "improve",
        "reduce pollution",
        "clean air",
        "make air better"
    ]):
        return "improvement"

    elif any(x in q for x in [
        "mask",
        "n95"
    ]):
        return "mask"

    elif any(x in q for x in [
        "pm2.5",
        "pm10",
        "co",
        "no2",
        "so2",
        "o3"
    ]):
        return "pollutant"

    return "general"


def _get_aqi_guidance(aqi_value: Optional[float]) -> str:
    if aqi_value is None:
        return "Use the current AQI category as a guide and reduce exposure when symptoms appear."
    if aqi_value < 50:
        return "AQI is low enough for most people to continue normal outdoor activity. Keep routine habits simple and stay hydrated."
    if aqi_value < 100:
        return "AQI is in the acceptable range for most people, but sensitive individuals should limit prolonged outdoor exertion."
    if aqi_value < 200:
        return "AQI is moderate to poor. Reduce prolonged outdoor exertion and consider lighter activity or shorter trips outdoors."
    if aqi_value < 300:
        return "AQI is poor. Avoid strenuous exercise, especially outdoors, and limit time outside during peak pollution periods."
    if aqi_value < 400:
        return "AQI is very poor. Stay indoors as much as possible, especially for children, older adults, and anyone with breathing issues."
    return "AQI is severe. Avoid outdoor exertion, use indoor air protection, and seek medical help if symptoms develop."


def _build_context(reading: dict, forecast_summary: Optional[str]) -> str:
    station_name = reading.get("station_name", "Current station")
    area = reading.get("area", "your area")
    category = reading.get("category", {}).get("label", "Unknown") if isinstance(reading.get("category"), dict) else reading.get("category", "Unknown")
    aqi_value = reading.get("aqi", "n/a")
    dominant_pollutant = _get_dominant_pollutant(reading)

    context_lines = [
        f"Location: {station_name}, {area}",
        f"Station: {station_name}",
        f"Area: {area}",
        f"Current AQI: {aqi_value} ({category})",
        f"PM2.5: {reading.get('pm25', 'n/a')} ug/m3",
        f"PM10: {reading.get('pm10', 'n/a')} ug/m3",
        f"NO2: {reading.get('no2', 'n/a')} ppb",
        f"SO2: {reading.get('so2', 'n/a')} ppb",
        f"CO: {reading.get('co', 'n/a')} ppb",
        f"O3: {reading.get('o3', 'n/a')} ppb",
        f"Dominant pollutant: {dominant_pollutant}",
        f"Time: {reading.get('time', 'not provided')}",
        AQI_CATEGORY_TABLE,
    ]

    if forecast_summary:
        context_lines.append(f"Forecast: {forecast_summary}")

    return "\n".join(context_lines)


def _build_prompt(reading: dict, question: Optional[str], forecast_summary: Optional[str]) -> str:
    intent = _detect_intent(question)
    user_question = question or "What health precautions should I take right now?"
    aqi_value = _coerce_numeric(reading.get("aqi"))
    guidance = _get_aqi_guidance(aqi_value)

    intent_instructions = {
        "general": "Provide a comprehensive but practical advisory. Explain the current risk, the likely health effects, and the most relevant precautions for the user.",
        "exercise": "Explain whether exercise is safe, why, what health effects are likely, how intense the activity should be, when the best time is, and what indoor alternatives are sensible.",
        "outdoor activities": "Explain whether outdoor time is appropriate, how long it should be limited, and what alternatives are better if the air is poor.",
        "commuting": "Give practical advice for travel, route selection, timing, and reducing exposure during commutes, especially for people who spend time near traffic.",
        "travel": "Explain travel-specific risks, what to do before leaving, and how to reduce exposure while traveling.",
        "children": "Focus on children and explain how this AQI may affect play, school, and outdoor time. Mention that children are often more sensitive to poor air quality.",
        "elderly": "Focus on older adults and explain why they may be more vulnerable. Mention reduced exertion and indoor alternatives.",
        "asthma": "Explain how this AQI may affect breathing, asthma symptoms, and when to avoid exertion or use preventive measures. Mention medication or care plans only as general caution, not as medical instruction.",
        "pregnancy": "Explain the relevance for pregnant individuals and why lower exposure is advisable. Mention that serious concerns should be discussed with a clinician.",
        "mask": "Explain which masks help, when they are useful, and what kind of mask is appropriate for the current AQI and exposure situation.",
        "air purifier": "Explain how air purifiers can help indoors, when they are most useful, and what else should be done to improve indoor air.",
        "AQI comparison": "Compare the current AQI using the CPCB categories and explain what the category means in plain language.",
        "pollution improvement": "Differentiate personal actions, community actions, and government-level actions clearly. Give practical steps for each.",
        "indoor air quality": "Focus on indoor exposure, ventilation, filtration, and ways to reduce pollution inside homes, schools, and offices.",
        "weather impact": "Explain how weather conditions may worsen or reduce exposure and how they interact with pollution levels.",
        "forecast": "Explain whether AQI is likely to improve or worsen and how that changes the advice.",
        "pollutant explanation": "Explain the pollutant clearly in plain language and connect it to the health impacts and the current AQI context.",
        "health symptoms": "Explain the likely health risks and advise when symptoms should be taken seriously. Encourage prompt medical attention for urgent symptoms.",
        "emergency": "Treat the situation as potentially urgent. Emphasize staying indoors, reducing exposure, and seeking medical help if breathing difficulty or severe symptoms occur.",
        "schools": "Make the advice relevant to schools, classrooms, children's activities, and school commute exposure.",
        "office workers": "Make the advice relevant to office settings, long indoor exposure, and commuting between home and work.",
    }

    prompt = f"""
You are AirCare AI.

Current Environmental Data

{_build_context(reading, forecast_summary)}

Current AQI Guidance

{guidance}

Detected Intent

{intent}

Examples of High Quality Responses

{FEW_SHOT_EXAMPLES}

Now answer the user's question using the same style.

User Question

{user_question}

Instructions for this intent

{intent_instructions.get(intent, intent_instructions["general"])}

Instructions

The USER'S QUESTION is always more important than the AQI.

Environmental data should only personalize your advice.

Never simply summarize the AQI.

Never repeat AQI unless it helps answer the question.

If the user asks a medical question,
focus on the medical concern first.

If the user asks about exercise,
focus on exercise first.

If the user asks about pollution,
focus on pollution reduction.

Think like a pulmonologist and environmental scientist.

Explain WHY.

Give practical recommendations.

Avoid generic advice.

Avoid repeating yourself.

Do not sound like an AI.

Use simple English.

Sound like an experienced doctor talking to a patient.

Only mention the AQI when it changes the recommendation.

If the AQI does not affect the answer significantly,
do not spend time discussing it.

Always end with one actionable takeaway.

"""
    return prompt


async def _call_gemini(api_key: str, model: str, prompt: str) -> Optional[str]:
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 700, "temperature": 0.7},
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(
            f"{GEMINI_API_BASE}/{model}:generateContent",
            params={"key": api_key},
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return None

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "\n".join(part.get("text", "") for part in parts).strip()
        return text or None


def _rule_based(reading: dict, question: Optional[str]) -> str:
    label = reading.get("category", {}).get("label", "Unknown") if isinstance(reading.get("category"), dict) else reading.get("category", "Unknown")
    aqi_value = _coerce_numeric(reading.get("aqi"))
    guidance = _get_aqi_guidance(aqi_value)
    sensitive_groups = "Children, older adults, pregnant individuals, and people with asthma, COPD, or heart disease should be more cautious."

    return f"""## Quick Answer
Current AQI is {reading.get('aqi', 'n/a')} ({label}). {guidance}

## Why
Air quality matters because fine particles and gases can irritate the lungs and increase cardiovascular strain. The current reading suggests the level of exposure should be managed carefully.

## Health Impact
The main concerns are irritation, reduced exercise tolerance, and worsening symptoms in sensitive groups. People with existing respiratory or heart conditions should be more cautious.

## Recommendations
- Keep outdoor exertion shorter and lighter than usual.
- Reduce time outside during peak pollution hours if possible.
- Use a well-fitted N95 or N99 mask when going outdoors for longer periods.
- Improve indoor air with ventilation and filtration when possible.

## Sensitive Groups
{sensitive_groups}

## Extra Tips
If you have breathing difficulty, chest discomfort, or unusual symptoms, seek medical advice promptly.
"""


async def get_advisory(reading: dict, question: Optional[str] = None, forecast_summary: Optional[str] = None) -> str:
    """Return a grounded health advisory for the supplied air-quality context."""
    api_key = _get_api_key()
    if not api_key:
        return _rule_based(reading, question)

    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    prompt = _build_prompt(reading, question, forecast_summary)

    try:
        response_text = await _call_gemini(api_key, model, prompt)
        if response_text:
            return response_text
    except (httpx.HTTPError, httpx.TimeoutException, ValueError, KeyError, TypeError):
        pass

    return _rule_based(reading, question)
