import MiniGauge from "./MiniGauge";

export default function RankingTable({ ranking, onSelect, selectedId }) {
  return (
    <div className="card reveal">
      <div className="section-label">Live Ranking</div>
      <h2 className="h-title" style={{ marginBottom: 4 }}>Most polluted districts right now</h2>
      <p style={{ color: "var(--text-muted)", fontSize: 13, margin: "0 0 18px" }}>
        Tap any district to load its full dashboard.
      </p>

      <div style={{ display: "grid", gap: 8 }}>
        {ranking.map((r, i) => {
          const isSelected = r.station_id === selectedId;
          return (
            <button
              key={r.station_id}
              onClick={() => onSelect(r.station_id)}
              className="card-hover"
              style={{
                display: "grid",
                gridTemplateColumns: "34px 1fr auto auto",
                alignItems: "center",
                gap: 14,
                width: "100%",
                textAlign: "left",
                padding: "10px 16px",
                borderRadius: "var(--radius-sm)",
                border: `1px solid ${isSelected ? r.category.color : "var(--border-soft)"}`,
                background: isSelected ? "var(--bg-card-hover)" : "var(--bg-elevated)",
                color: "var(--text-primary)",
              }}
            >
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: 15,
                  fontWeight: 700,
                  color: i < 3 ? r.category.color : "var(--text-faint)",
                }}
              >
                {i + 1}
              </span>
              <span style={{ fontSize: 14.5, fontWeight: 500, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {r.station_name}
                <span style={{ color: "var(--text-faint)", fontWeight: 400 }}> · {r.area}</span>
              </span>
              <span
                className="rank-status"
                style={{
                  fontSize: 11.5,
                  fontWeight: 600,
                  color: r.category.color,
                  padding: "3px 10px",
                  borderRadius: 999,
                  border: `1px solid ${r.category.color}44`,
                  background: `${r.category.color}14`,
                  whiteSpace: "nowrap",
                }}
              >
                {r.category.label}
              </span>
              <MiniGauge aqi={r.aqi} />
            </button>
          );
        })}
      </div>
      <style>{`
        @media (max-width: 560px) {
          .rank-status { display: none; }
        }
      `}</style>
    </div>
  );
}
