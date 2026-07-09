const CONDITION_EMOJI = {
  "Clear": "☀️", "Mainly Clear": "🌤️", "Partly Cloudy": "⛅", "Overcast": "☁️",
  "Fog": "🌫️", "Light Drizzle": "🌦️", "Drizzle": "🌦️", "Heavy Drizzle": "🌧️",
  "Light Rain": "🌦️", "Rain": "🌧️", "Heavy Rain": "🌧️",
  "Light Snow": "🌨️", "Snow": "🌨️", "Heavy Snow": "❄️",
  "Rain Showers": "🌦️", "Violent Showers": "⛈️",
  "Thunderstorm": "⛈️", "Thunderstorm Hail": "⛈️", "Variable": "🌡️",
};

export default function WeatherWidget({ weather, loading, embedded = false }) {
  const pad = embedded ? "18px 20px" : "20px 22px";

  if (loading || !weather) {
    return (
      <div style={{ ...(embedded ? {} : cardStyle), padding: pad }}>
        <div className="skeleton" style={{ height: 20, width: 110, marginBottom: 12 }} />
        <div className="skeleton" style={{ height: 40, width: 80 }} />
      </div>
    );
  }

  const emoji = CONDITION_EMOJI[weather.condition] || "🌡️";

  return (
    <div style={{ ...(embedded ? {} : cardStyle), padding: pad }}>
      <div style={{ fontSize: 11.5, letterSpacing: "0.14em", textTransform: "uppercase", color: "var(--text-faint)", fontFamily: "var(--font-mono)", marginBottom: 12 }}>
        Weather
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <span style={{ fontSize: 42, lineHeight: 1 }}>{emoji}</span>
        <div>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: 32, fontWeight: 700, lineHeight: 1 }}>
            {weather.temp_c != null ? `${Math.round(weather.temp_c)}°` : "—"}
          </div>
          <div style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 2 }}>{weather.condition}</div>
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginTop: 16 }}>
        <Stat icon="💧" label="Humidity" value={weather.humidity != null ? `${Math.round(weather.humidity)}%` : "—"} />
        <Stat icon="🌬️" label="Wind" value={weather.wind_kmh != null ? `${Math.round(weather.wind_kmh)}` : "—"} sub="km/h" />
        <Stat icon="☀️" label="UV" value={weather.uv_index != null ? Math.round(weather.uv_index) : "—"} />
      </div>
    </div>
  );
}

function Stat({ icon, label, value, sub }) {
  return (
    <div style={{ background: "rgba(255,255,255,0.03)", borderRadius: 10, padding: "10px 8px", textAlign: "center", border: "1px solid var(--border-soft)" }}>
      <div style={{ fontSize: 15 }}>{icon}</div>
      <div style={{ fontFamily: "var(--font-mono)", fontSize: 14, fontWeight: 600, marginTop: 2 }}>{value}<span style={{ fontSize: 9, color: "var(--text-faint)" }}>{sub ? ` ${sub}` : ""}</span></div>
      <div style={{ fontSize: 10, color: "var(--text-faint)" }}>{label}</div>
    </div>
  );
}

const cardStyle = {
  background: "linear-gradient(160deg, var(--bg-elevated), var(--bg-card))",
  border: "1px solid var(--border-soft)",
  borderRadius: "var(--radius)",
  minWidth: 260,
};
