// Major pollutants panel — matches the aqi.in 6-card layout with icons,
// colored severity accents, and per-pollutant status dots.

const POLLUTANTS = [
  { key: "pm25", label: "Particulate Matter", formula: "PM2.5", unit: "µg/m³", icon: "🌫️", hi: 120 },
  { key: "pm10", label: "Particulate Matter", formula: "PM10", unit: "µg/m³", icon: "🌫️", hi: 200 },
  { key: "co", label: "Carbon Monoxide", formula: "CO", unit: "ppb", icon: "🟤", hi: 300 },
  { key: "so2", label: "Sulfur Dioxide", formula: "SO₂", unit: "ppb", icon: "🟡", hi: 40 },
  { key: "no2", label: "Nitrogen Dioxide", formula: "NO₂", unit: "ppb", icon: "🟢", hi: 80 },
  { key: "o3", label: "Ozone", formula: "O₃", unit: "ppb", icon: "🔵", hi: 100 },
];

function statusColor(value, hi) {
  if (value == null) return "var(--border)";
  const r = value / hi;
  if (r < 0.5) return "var(--aqi-good)";
  if (r < 0.85) return "var(--aqi-moderate)";
  if (r < 1.2) return "var(--aqi-poor)";
  return "var(--aqi-very-poor)";
}

export default function PollutantGrid({ reading }) {
  return (
    <div className="card reveal">
      <div className="section-label">Major Air Pollutants</div>
      <h2 className="h-title" style={{ marginBottom: 6 }}>
        {reading ? `${reading.station_name}, ${reading.area}` : "Select a district"}
      </h2>
      <p style={{ color: "var(--text-muted)", fontSize: 13, margin: "0 0 20px" }}>
        Live where a nearby sensor reports, AQI-derived estimates otherwise.
      </p>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))",
          gap: 14,
        }}
      >
        {POLLUTANTS.map((p) => {
          const value = reading?.[p.key];
          const color = statusColor(value, p.hi);
          return (
            <div
              key={p.formula}
              className="card-hover"
              style={{
                background: "var(--bg-elevated)",
                border: "1px solid var(--border-soft)",
                borderLeft: `4px solid ${color}`,
                borderRadius: "var(--radius-sm)",
                padding: "16px 18px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span style={{ fontSize: 22 }}>{p.icon}</span>
                <div style={{ fontSize: 13, color: "var(--text-muted)", lineHeight: 1.35 }}>
                  {p.label}
                  <br />
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: color }}>
                    {p.formula}
                  </span>
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 25, fontWeight: 700 }}>
                  {value ?? "—"}
                </span>
                <div style={{ fontSize: 11, color: "var(--text-faint)" }}>{p.unit}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
