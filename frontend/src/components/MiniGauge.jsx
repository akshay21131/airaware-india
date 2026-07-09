// Small semicircular gauge for ranking rows (like aqi.in's rank dials).
const BANDS = [
  { max: 50, color: "#4CAF6D" }, { max: 100, color: "#A3D977" },
  { max: 200, color: "#F1C40F" }, { max: 300, color: "#E67E22" },
  { max: 400, color: "#E74C3C" }, { max: 500, color: "#9B59B6" },
];
function colorForAqi(aqi) {
  for (const b of BANDS) if (aqi <= b.max) return b.color;
  return "#9B59B6";
}

export default function MiniGauge({ aqi, size = 52 }) {
  const value = aqi ?? 0;
  const pct = Math.max(0, Math.min(1, value / 500));
  const color = colorForAqi(value);
  const stroke = 5;
  const r = (size - stroke) / 2;
  const cx = size / 2;
  const cy = size / 2;
  const startAngle = 180, sweep = 180;
  const circ = 2 * Math.PI * r;
  const arcLen = (sweep / 360) * circ;
  const prog = arcLen * pct;
  const polar = (a) => ({ x: cx + r * Math.cos((a * Math.PI) / 180), y: cy + r * Math.sin((a * Math.PI) / 180) });
  const s = polar(startAngle), e = polar(startAngle + sweep);
  const path = `M ${s.x} ${s.y} A ${r} ${r} 0 0 1 ${e.x} ${e.y}`;
  return (
    <div style={{ position: "relative", width: size, height: size / 2 + 8, flexShrink: 0 }}>
      <svg width={size} height={size / 2 + 8}>
        <path d={path} fill="none" stroke="var(--border)" strokeWidth={stroke} strokeLinecap="round" />
        <path d={path} fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round"
          strokeDasharray={`${prog} ${circ}`} style={{ transition: "stroke-dasharray 0.7s ease" }} />
      </svg>
      <span style={{
        position: "absolute", bottom: 0, left: 0, right: 0, textAlign: "center",
        fontFamily: "var(--font-mono)", fontSize: 14, fontWeight: 700, color,
      }}>
        {aqi != null ? Math.round(aqi) : "—"}
      </span>
    </div>
  );
}
