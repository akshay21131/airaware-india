"""
Government response layer, based on India's Graded Response Action Plan
(GRAP) - the actual legally-binding staged pollution response mechanism run
by the Commission for Air Quality Management (CAQM) for Delhi-NCR.

GRAP is officially scoped to Delhi-NCR only; it isn't a national law. We
surface it nationally as a reference framework ("what would kick in if this
AQI were in Delhi-NCR"), and label it as such everywhere it's shown, rather
than implying every district is legally bound by it. This still gives the
user something concrete and true to point to for the "government advisory"
angle of the hackathon brief, without misrepresenting jurisdiction.

Source: CAQM's published GRAP schedule (revised 2023), summarized here at
the level of citizen-relevant actions, not the full regulatory text.
"""
from __future__ import annotations

GRAP_STAGES = [
    {
        "stage": 0,
        "name": "Below GRAP thresholds",
        "aqi_min": 0,
        "aqi_max": 200,
        "color": "#4CAF6D",
        "actions": [
            "No GRAP-specific restrictions in force.",
            "Routine dust and emission control norms apply as usual.",
        ],
    },
    {
        "stage": 1,
        "name": "Stage I - Poor",
        "aqi_min": 201,
        "aqi_max": 300,
        "color": "#E67E22",
        "actions": [
            "Mechanized road sweeping and water sprinkling on major roads.",
            "Strict action against open burning of waste and biomass.",
            "Dust-control norms enforced at construction/demolition sites.",
            "PUC (Pollution Under Control) checks intensified; old/unfit vehicles fined.",
        ],
    },
    {
        "stage": 2,
        "name": "Stage II - Very Poor",
        "aqi_min": 301,
        "aqi_max": 400,
        "color": "#E74C3C",
        "actions": [
            "Increased parking fees to discourage private vehicle use.",
            "Higher frequency of public bus/metro services.",
            "Diesel generator sets restricted, except for essential services.",
            "Stricter enforcement of dust-control at construction sites; some may be halted.",
        ],
    },
    {
        "stage": 3,
        "name": "Stage III - Severe",
        "aqi_min": 401,
        "aqi_max": 450,
        "color": "#9B59B6",
        "actions": [
            "Construction and demolition activity stopped (except essential projects).",
            "BS-III petrol and BS-IV diesel light vehicles may be restricted.",
            "Schools may shift younger grades to hybrid/online mode at local discretion.",
            "Non-essential truck entry into the city restricted.",
        ],
    },
    {
        "stage": 4,
        "name": "Stage IV - Severe+",
        "aqi_min": 451,
        "aqi_max": 500,
        "color": "#6B2E7A",
        "actions": [
            "All construction and demolition activity stopped.",
            "Truck entry banned except those carrying essential goods.",
            "Odd-even vehicle rationing scheme may be invoked.",
            "Physical classes may be suspended for all grades at local discretion.",
            "Work-from-home advised for government and private offices where feasible.",
        ],
    },
]


def get_grap_stage(aqi: float) -> dict:
    """Return the GRAP stage entry whose AQI band contains the given value."""
    for stage in GRAP_STAGES:
        if stage["aqi_min"] <= aqi <= stage["aqi_max"]:
            return stage
    return GRAP_STAGES[-1] if aqi > 500 else GRAP_STAGES[0]
