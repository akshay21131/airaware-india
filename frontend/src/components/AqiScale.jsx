// AQI category scale legend — like the aqi.in "Air Quality Index Scale" section.

const SCALE = [
  { label: "Good", range: "0–50", color: "var(--aqi-good)", note: "Air is fresh and clean. Enjoy the outdoors." },
  { label: "Satisfactory", range: "51–100", color: "var(--aqi-satisfactory)", note: "Acceptable for most; very sensitive people take minor care." },
  { label: "Moderate", range: "101–200", color: "var(--aqi-moderate)", note: "Sensitive groups may feel mild discomfort." },
  { label: "Poor", range: "201–300", color: "var(--aqi-poor)", note: "Breathing discomfort likely on prolonged exposure." },
  { label: "Very Poor", range: "301–400", color: "var(--aqi-very-poor)", note: "Respiratory illness on prolonged exposure. Avoid outdoors." },
  { label: "Severe", range: "401–500", color: "var(--aqi-severe)", note: "Serious health impact for all. Stay indoors." },
];

export default function AqiScale({ activeLabel }) {
  return (
    <div className="card reveal">
      <div className="section-label">Air Quality Index Scale</div>
      <h2 className="h-title" style={{ marginBottom: 18 }}>What the numbers mean (CPCB, India)</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 12 }}>
        {SCALE.map((s) => {
          const active = s.label === activeLabel;
          return (
            <div
              key={s.label}
              style={{
                display: "flex",
                gap: 14,
                alignItems: "flex-start",
                padding: "14px 16px",
                borderRadius: "var(--radius-sm)",
                background: active ? "var(--bg-card-hover)" : "var(--bg-elevated)",
                border: `1px solid ${active ? s.color : "var(--border-soft)"}`,
              }}
            >
              <div
                style={{
                  width: 44, height: 44, borderRadius: 10, flexShrink: 0,
                  background: s.color, display: "flex", alignItems: "center", justifyContent: "center",
                  fontFamily: "var(--font-mono)", fontSize: 11, fontWeight: 700, color: "#1B1822",
                  textAlign: "center", lineHeight: 1.1, padding: 2,
                }}
              >
                {s.range}
              </div>
              <div>
                <div style={{ fontWeight: 600, color: s.color, display: "flex", alignItems: "center", gap: 8 }}>
                  {s.label}
                  {active && <span style={{ fontSize: 10, color: "var(--text-faint)", fontWeight: 500 }}>● current</span>}
                </div>
                <div style={{ fontSize: 12.5, color: "var(--text-muted)", marginTop: 3 }}>{s.note}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
