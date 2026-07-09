import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";

export default function ForecastChart({ forecast, stationName }) {
  const data = (forecast || []).map((f) => ({
    time: new Date(f.timestamp).toLocaleString("en-IN", { weekday: "short", hour: "2-digit" }),
    aqi: f.aqi,
  }));

  const peak = data.reduce((m, d) => Math.max(m, d.aqi), 0);

  return (
    <div className="card reveal">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 8 }}>
        <div>
          <div className="section-label">72-Hour Forecast</div>
          <h2 className="h-title">
            {stationName ? `Projected AQI · ${stationName}` : "Select a station"}
          </h2>
        </div>
        {peak > 0 && (
          <span className="pill">Peak {peak}</span>
        )}
      </div>
      <div style={{ marginTop: 18 }}>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={data} margin={{ top: 10, right: 8, left: -14, bottom: 0 }}>
            <defs>
              <linearGradient id="forecastFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--accent-marigold)" stopOpacity={0.55} />
                <stop offset="100%" stopColor="var(--accent-marigold)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="var(--border-soft)" strokeDasharray="3 4" vertical={false} />
            <XAxis
              dataKey="time"
              interval={Math.max(0, Math.floor(data.length / 8))}
              tick={{ fill: "var(--text-faint)", fontSize: 11, fontFamily: "var(--font-mono)" }}
              axisLine={{ stroke: "var(--border)" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "var(--text-faint)", fontSize: 11, fontFamily: "var(--font-mono)" }}
              axisLine={false}
              tickLine={false}
              width={40}
            />
            <ReferenceLine y={100} stroke="var(--aqi-moderate)" strokeDasharray="4 4" strokeOpacity={0.4} />
            <ReferenceLine y={200} stroke="var(--aqi-poor)" strokeDasharray="4 4" strokeOpacity={0.4} />
            <ReferenceLine y={300} stroke="var(--aqi-very-poor)" strokeDasharray="4 4" strokeOpacity={0.4} />
            <Tooltip
              contentStyle={{
                background: "var(--bg-elevated)",
                border: "1px solid var(--border)",
                borderRadius: 10,
                fontFamily: "var(--font-mono)",
                fontSize: 12.5,
              }}
              labelStyle={{ color: "var(--text-muted)" }}
              itemStyle={{ color: "var(--accent-marigold)" }}
            />
            <Area type="monotone" dataKey="aqi" stroke="var(--accent-marigold)" strokeWidth={2.5} fill="url(#forecastFill)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
