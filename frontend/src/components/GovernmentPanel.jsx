export default function GovernmentPanel({ grapData, stationName }) {
  const stage = grapData?.grap_stage;

  return (
    <div className="card reveal">
      <div className="section-label">Government Response · GRAP</div>
      <h2 className="h-title" style={{ marginBottom: 6 }}>
        {stationName ? `Recommended action · ${stationName}` : "Government advisory"}
      </h2>
      <p style={{ color: "var(--text-muted)", fontSize: 13, margin: "0 0 20px", maxWidth: 720 }}>
        The Graded Response Action Plan (GRAP) is India's official staged pollution-response
        mechanism, run by the CAQM. Legally in force for Delhi-NCR; shown here as a national
        reference for the measures this AQI level would trigger.
      </p>

      {!stage ? (
        <div className="skeleton" style={{ height: 80 }} />
      ) : (
        <>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 16,
              padding: "16px 20px",
              borderRadius: "var(--radius-sm)",
              background: `linear-gradient(120deg, ${stage.color}18, transparent)`,
              border: `1px solid ${stage.color}55`,
              borderLeft: `5px solid ${stage.color}`,
              marginBottom: 20,
            }}
          >
            <div
              style={{
                width: 52, height: 52, borderRadius: "50%", flexShrink: 0,
                display: "flex", alignItems: "center", justifyContent: "center",
                background: stage.color, color: "#1B1822",
                fontFamily: "var(--font-mono)", fontWeight: 700, fontSize: 20,
              }}
            >
              {stage.stage}
            </div>
            <div>
              <div style={{ fontFamily: "var(--font-display)", fontSize: 19, fontWeight: 600, color: stage.color }}>
                {stage.name}
              </div>
              <div style={{ fontSize: 13, color: "var(--text-muted)" }}>
                Current AQI {grapData.aqi} · action band {stage.aqi_min}–{stage.aqi_max}
              </div>
            </div>
          </div>

          <div style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 12, fontWeight: 600 }}>
            Measures in effect at this level:
          </div>
          <ul style={{ margin: 0, padding: 0, listStyle: "none", display: "grid", gap: 10 }}>
            {stage.actions.map((action, i) => (
              <li key={i} style={{ display: "flex", alignItems: "flex-start", gap: 12, fontSize: 14 }}>
                <span aria-hidden="true" style={{
                  marginTop: 2, width: 20, height: 20, borderRadius: "50%", flexShrink: 0,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  background: `${stage.color}22`, color: stage.color, fontSize: 12, fontWeight: 700,
                }}>✓</span>
                {action}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
