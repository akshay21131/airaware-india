// Circular AQI gauge — the signature radial dial (like aqi.in).
// Renders a 270° arc with a colored progress sweep and the AQI value centered.

const BANDS = [
  { max: 50, color: "#4CAF6D" },
  { max: 100, color: "#A3D977" },
  { max: 200, color: "#F1C40F" },
  { max: 300, color: "#E67E22" },
  { max: 400, color: "#E74C3C" },
  { max: 500, color: "#9B59B6" },
];

function colorForAqi(aqi) {
  for (const b of BANDS) if (aqi <= b.max) return b.color;
  return "#9B59B6";
}

export default function AqiGauge({ aqi, label, size = 220, stroke = 16 }) {
  const value = aqi ?? 0;
  const pct = Math.max(0, Math.min(1, value / 500));
  const color = colorForAqi(value);

  const radius = (size - stroke) / 2;
  const cx = size / 2;
  const cy = size / 2;

  // 270° arc, starting at 135° (bottom-left) going clockwise to 45° (bottom-right)
  const startAngle = 135;
  const sweep = 270;
  const circumference = 2 * Math.PI * radius;
  const arcLength = (sweep / 360) * circumference;
  const progressLength = arcLength * pct;

  const polar = (angleDeg) => {
    const a = (angleDeg * Math.PI) / 180;
    return { x: cx + radius * Math.cos(a), y: cy + radius * Math.sin(a) };
  };
  const start = polar(startAngle);
  const end = polar(startAngle + sweep);
  const largeArc = sweep > 180 ? 1 : 0;
  const trackPath = `M ${start.x} ${start.y} A ${radius} ${radius} 0 ${largeArc} 1 ${end.x} ${end.y}`;

  return (
    <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ display: "block" }}>
        <defs>
          <linearGradient id={`gaugeGrad-${label}`} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.85" />
            <stop offset="100%" stopColor={color} />
          </linearGradient>
          <filter id={`glow-${label}`} x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="4" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Track */}
        <path
          d={trackPath}
          fill="none"
          stroke="var(--border)"
          strokeWidth={stroke}
          strokeLinecap="round"
        />
        {/* Progress */}
        <path
          d={trackPath}
          fill="none"
          stroke={`url(#gaugeGrad-${label})`}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${progressLength} ${circumference}`}
          filter={`url(#glow-${label})`}
          style={{ transition: "stroke-dasharray 0.9s cubic-bezier(0.22,1,0.36,1)" }}
        />
      </svg>

      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
        }}
      >
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: size * 0.28,
            fontWeight: 700,
            lineHeight: 1,
            color,
          }}
        >
          {aqi != null ? Math.round(aqi) : "—"}
        </span>
        <span style={{ fontSize: size * 0.06, color: "var(--text-faint)", letterSpacing: "0.08em", marginTop: 4 }}>
          AQI · IN
        </span>
        {label && (
          <span
            style={{
              marginTop: 8,
              fontFamily: "var(--font-display)",
              fontSize: size * 0.085,
              fontWeight: 600,
              color,
            }}
          >
            {label}
          </span>
        )}
      </div>
    </div>
  );
}
