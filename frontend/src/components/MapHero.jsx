import { MapContainer, TileLayer, CircleMarker, Tooltip, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect } from "react";
import StationPicker from "./StationPicker";
import AqiGauge from "./AqiGauge";
import WeatherWidget from "./WeatherWidget";

// Recenters the map when the selected district changes.
function Recenter({ lat, lon }) {
  const map = useMap();
  useEffect(() => {
    if (lat != null && lon != null) {
      map.flyTo([lat, lon], 6.4, { duration: 1.1 });
    }
  }, [lat, lon, map]);
  return null;
}

const HEALTH_BLURB = {
  Good: "Air is fresh. Great for outdoor activity.",
  Satisfactory: "Acceptable air. Sensitive people take minor care.",
  Moderate: "Sensitive groups should limit prolonged exertion.",
  Poor: "Reduce outdoor exertion. Consider a mask.",
  "Very Poor": "Avoid outdoor activity. Stay indoors if sensitive.",
  Severe: "Health alert — stay indoors, wear an N95 outside.",
};

export default function MapHero({
  stations, readings, selectedId, onSelect,
  reading, loading, weather, weatherLoading,
}) {
  const color = reading?.category?.color || "#4FA9A8";
  const label = reading?.category?.label;

  return (
    <section className="map-hero">
      {/* Full-bleed live map */}
      <div className="map-hero__map">
        <MapContainer
          center={[22.8, 79]}
          zoom={5}
          scrollWheelZoom={false}
          zoomControl={false}
          style={{ height: "100%", width: "100%", background: "#0f0d14" }}
        >
          <TileLayer
            attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>, OpenStreetMap'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
          <Recenter lat={reading?.lat} lon={reading?.lon} />
          {readings.map((r) => (
            <CircleMarker
              key={r.station_id}
              center={[r.lat, r.lon]}
              radius={r.station_id === selectedId ? 11 : 6.5}
              pathOptions={{
                color: r.category.color,
                fillColor: r.category.color,
                fillOpacity: 0.8,
                weight: r.station_id === selectedId ? 3 : 1,
              }}
              eventHandlers={{ click: () => onSelect(r.station_id) }}
            >
              <Tooltip direction="top" offset={[0, -6]}>
                <strong>{r.station_name}</strong>, {r.area}
                <br />AQI {r.aqi} · {r.category.label}
              </Tooltip>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      {/* gradient scrims for legibility */}
      <div className="map-hero__scrim" aria-hidden="true" />

      {/* Floating glass panel */}
      <div className="map-hero__panel">
        <div className="glass-card reveal">
          <div className="section-label">Live Air Quality Index</div>
          <StationPicker stations={stations} selectedId={selectedId} onSelect={onSelect} />

          <div className="map-hero__readout">
            <AqiGauge aqi={loading ? null : reading?.aqi} label={label} size={172} />
            <div style={{ minWidth: 0 }}>
              <div style={{ color: "var(--text-muted)", fontSize: 13.5, fontWeight: 500 }}>
                {reading ? `${reading.station_name}, ${reading.area}` : "Fetching…"}
              </div>
              <p style={{ margin: "8px 0 0", fontSize: 14, lineHeight: 1.5 }}>
                {label ? HEALTH_BLURB[label] : "Loading air quality…"}
              </p>
              <div style={{ display: "flex", gap: 16, marginTop: 12, flexWrap: "wrap" }}>
                <Metric label="PM2.5" value={reading?.pm25} />
                <Metric label="PM10" value={reading?.pm10} />
              </div>
              <span className="pill" style={{ marginTop: 12, display: "inline-flex" }}>
                {reading?.source === "openaq-live" ? "● Live sensor" : "○ Modeled estimate"}
              </span>
            </div>
          </div>
        </div>

        <div className="glass-card reveal reveal-1" style={{ padding: 0, overflow: "hidden" }}>
          <WeatherWidget weather={weather} loading={weatherLoading} embedded />
        </div>
      </div>

      {/* map legend */}
      <div className="map-hero__legend">
        {[
          ["Good", "var(--aqi-good)"],
          ["Satisfactory", "var(--aqi-satisfactory)"],
          ["Moderate", "var(--aqi-moderate)"],
          ["Poor", "var(--aqi-poor)"],
          ["Very Poor", "var(--aqi-very-poor)"],
          ["Severe", "var(--aqi-severe)"],
        ].map(([lbl, c]) => (
          <span key={lbl} className="map-hero__legend-item">
            <span style={{ width: 8, height: 8, borderRadius: "50%", background: c }} />
            {lbl}
          </span>
        ))}
      </div>

      {/* scroll cue */}
      <div className="map-hero__cue" aria-hidden="true">
        <span>Scroll for full report</span>
        <div className="map-hero__chev">⌄</div>
      </div>
    </section>
  );
}

function Metric({ label, value }) {
  return (
    <div>
      <div style={{ fontFamily: "var(--font-mono)", fontSize: 18, fontWeight: 700 }}>{value ?? "—"}</div>
      <div style={{ fontSize: 10.5, color: "var(--text-faint)" }}>{label} · µg/m³</div>
    </div>
  );
}
