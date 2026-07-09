# AirAware India — Urban Air Quality Intelligence

A pan-India air quality dashboard: live + forecast AQI across 140+ districts,
a full six-pollutant panel, weather, an AI-powered health advisor (Gemini),
a government-action panel based on India's real GRAP framework, a live
"most polluted districts" leaderboard, and optional Firebase login.

- **Backend:** FastAPI (Python) — OpenAQ live data + synthetic fallback,
  a RandomForest 72-hour forecaster, Gemini advisories, Open-Meteo weather, GRAP.
- **Frontend:** React + Vite — dark "dusk-haze" dashboard with Leaflet map,
  Recharts forecast, searchable district picker, and Firebase auth.

---

## 🔑 Where to paste your API keys

| Key | File | What for |
|-----|------|----------|
| **Gemini API key** | `backend/.env` → `GEMINI_API_KEY=...` | AI health advisories. Free key: https://aistudio.google.com/apikey |
| **Firebase config** | `frontend/src/firebase.js` (top of file) | Login / signup / logout. Optional. |

- **No Gemini key?** The advisor still works — it falls back to a clear
  rule-based advisory. Nothing crashes.
- **No Firebase config?** The whole dashboard works. The Login button just
  shows a friendly "not configured" note until you paste your config.
- **OpenAQ** (live AQI) and **Open-Meteo** (weather) need **no key at all**.

---

## 🚀 Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt

# add your Gemini key (optional but recommended)
cp .env.example .env
#   then edit .env and set GEMINI_API_KEY=...

python -m uvicorn app.main:app --reload --port 8000
```

> **Tip (fixes the error you hit earlier):** always use `python -m uvicorn ...`
> and `python -m pip ...` rather than the bare `uvicorn` / `pip` commands. That
> guarantees you're using the *same* Python that has your packages installed,
> and sidesteps the conda-vs-python.org PATH conflict.

First launch auto-trains the forecast model (~30s, MAE ≈ 14–15 AQI points) and
caches it to `backend/models/aqi_forest.joblib`.

Backend is now at **http://localhost:8000** — try http://localhost:8000/docs.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the printed URL (usually **http://localhost:5173**).

---

## 🗺️ The district dataset

`backend/app/data/india_districts.json` holds 140+ real Indian districts/cities
with genuine lat/lon coordinates, each tagged with a climate/pollution **zone**
(`igp`, `coastal`, `peninsular`, `arid`, `gangetic-delta`, `northeast`,
`central`, `himalayan`). These zones drive the seasonal AQI model.

To regenerate or extend the list, edit `backend/build_districts.py` and run:

```bash
cd backend && python build_districts.py
```

---

## 🧠 How the data works (honest version)

- **Live AQI:** each district tries OpenAQ v3 for a real nearby sensor. India's
  OpenAQ coverage is sparse, so where no live sensor exists, a physically
  plausible **synthetic estimate** is used (clearly labeled `source` in every
  reading: `openaq-live` vs `synthetic-fallback`).
- **The national map & leaderboard** default to instant synthetic estimates
  (live-checking every district serially took ~40s). Drilling into one district
  (`/api/aqi/current/{id}`, forecast, chat, weather, government) always tries
  live data first. Pass `?live=true` to `/api/aqi/current` or `/api/ranking`
  to force live checks everywhere.
- **Forecast:** a RandomForest chained one-step-ahead over 72h. It's **anchored
  on the live reading** — the seed history is shifted so the forecast starts
  from the true current value, then evolves with realistic diurnal/seasonal shape.
- **Weather:** live from Open-Meteo, with a seasonal fallback.
- **Government panel (GRAP):** India's real Graded Response Action Plan, run by
  CAQM. Legally in force for **Delhi-NCR only** — shown nationally as a reference
  for "what measures this AQI would trigger," and labeled as such in the UI.

---

## 📡 API endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/stations` | All districts |
| GET | `/api/aqi/current?live=false` | Current reading for every district (map) |
| GET | `/api/aqi/current/{id}` | One district, live-first |
| GET | `/api/aqi/forecast/{id}?hours=72` | 72h forecast, anchored on live |
| GET | `/api/weather/{id}` | Live weather |
| GET | `/api/government/{id}` | GRAP stage for current AQI |
| GET | `/api/ranking?limit=15` | Most polluted districts |
| POST | `/api/chat` | Gemini health advisory (`{station_id, question}`) |
| POST | `/api/train` | Retrain the forecast model |
| GET | `/api/health` | Health check |

---

## 🛠️ Tech & structure

```
airaware/
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── build_districts.py          # regenerates the district dataset
│   └── app/
│       ├── main.py                 # FastAPI app + all endpoints
│       ├── data_fetcher.py         # OpenAQ live + synthetic fallback
│       ├── ml_model.py             # RandomForest 72h forecaster
│       ├── advisor.py              # Gemini health advisories
│       ├── weather.py              # Open-Meteo weather
│       ├── grap.py                 # GRAP government-action framework
│       └── data/india_districts.json
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx / App.jsx / api.js / index.css
        ├── firebase.js / AuthContext.jsx      # auth
        └── components/
            ├── Hero.jsx / HazeBar.jsx / StationPicker.jsx / WeatherWidget.jsx
            ├── IndiaMap.jsx / PollutantGrid.jsx / ForecastChart.jsx
            ├── GovernmentPanel.jsx / RankingTable.jsx
            ├── AdvisoryChat.jsx / Login.jsx
```

---

## ⚠️ Known limitations

- OpenAQ India coverage is sparse; most map points are modeled estimates.
- Pollutant breakdown (CO/SO₂/NO₂/O₃) is AQI-derived where live data is missing.
- GRAP is Delhi-NCR law only; shown nationally as reference, labeled accordingly.
- Forecast is a solid baseline (RandomForest). An LSTM sketch is in
  `ml_model.py` for when you have real multi-month history per station.

---

Built for the ET AI Hackathon · Urban Air Quality Intelligence.
