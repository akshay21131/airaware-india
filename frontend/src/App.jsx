import { useEffect, useState } from "react";
import { api } from "./api";
import { useAuth } from "./AuthContext";
import MapHero from "./components/MapHero";
import ForecastChart from "./components/ForecastChart";
import AdvisoryChat from "./components/AdvisoryChat";
import PollutantGrid from "./components/PollutantGrid";
import GovernmentPanel from "./components/GovernmentPanel";
import RankingTable from "./components/RankingTable";
import AqiScale from "./components/AqiScale";
import Login from "./components/Login";

export default function App() {
  const { user, authLoading, logout, isFirebaseConfigured } = useAuth();
  const [showLogin, setShowLogin] = useState(false);

  const [stations, setStations] = useState([]);
  const [readings, setReadings] = useState([]);
  const [selectedId, setSelectedId] = useState("new-delhi-delhi");
  const [forecast, setForecast] = useState([]);
  const [weather, setWeather] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(true);
  const [grapData, setGrapData] = useState(null);
  const [ranking, setRanking] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.stations()
      .then((d) => {
        setStations(d.stations);
        if (d.stations.length && !d.stations.some((s) => s.id === selectedId)) {
          setSelectedId(d.stations[0].id);
        }
      })
      .catch(() => setError("Could not reach backend. Is it running on port 8000?"));
    api.currentAll()
      .then((d) => { setReadings(d.readings); setLoading(false); })
      .catch(() => { setError("Could not reach backend. Is it running on port 8000?"); setLoading(false); });
    api.ranking(15).then((d) => setRanking(d.ranking)).catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    api.forecast(selectedId, 72).then((d) => setForecast(d.forecast)).catch(() => {});
    api.government(selectedId).then(setGrapData).catch(() => {});
    setWeatherLoading(true);
    api.weather(selectedId).then((w) => { setWeather(w); setWeatherLoading(false); }).catch(() => setWeatherLoading(false));
  }, [selectedId]);

  const selectedReading = readings.find((r) => r.station_id === selectedId);
  const selectedStation = stations.find((s) => s.id === selectedId);

  return (
    <>
      <header className="site-header">
        <div className="site-header-inner">
          <div style={{ display: "flex", alignItems: "center", gap: 11 }}>
            <div className="brand-mark" />
            <div style={{ lineHeight: 1.1 }}>
              <div style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 18 }}>
                AirAware <span style={{ color: "var(--accent-marigold)" }}>India</span>
              </div>
              <div style={{ fontSize: 10, color: "var(--text-faint)", fontFamily: "var(--font-mono)", letterSpacing: "0.08em" }}>
                URBAN AIR QUALITY INTELLIGENCE
              </div>
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span className="pill hide-sm">{stations.length || "…"} districts</span>
            {!authLoading && (
              user ? (
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span className="hide-sm" style={{ fontSize: 13, color: "var(--text-muted)" }}>
                    {user.email || user.displayName}
                  </span>
                  <button onClick={logout} className="btn-ghost">Logout</button>
                </div>
              ) : (
                <button onClick={() => setShowLogin(true)} className="btn-primary">Login</button>
              )
            )}
          </div>
        </div>
      </header>

      {error && (
        <div className="wrap" style={{ paddingTop: 20 }}>
          <div className="card" style={{ borderColor: "var(--aqi-poor)", color: "var(--aqi-poor)" }}>
            {error} — run <code>python -m uvicorn app.main:app --reload</code> inside <code>backend/</code>.
          </div>
        </div>
      )}

      <MapHero
        stations={stations}
        readings={readings}
        selectedId={selectedId}
        onSelect={setSelectedId}
        reading={selectedReading}
        loading={loading}
        weather={weather}
        weatherLoading={weatherLoading}
      />

      <main className="wrap">
        <div className="section">
          <PollutantGrid reading={selectedReading} />
        </div>

        <div className="section" style={{ paddingTop: 0 }}>
          <div className="grid-2">
            <ForecastChart forecast={forecast} stationName={selectedStation?.name} />
            <GovernmentPanel grapData={grapData} stationName={selectedStation?.name} />
          </div>
        </div>

        <div className="section" style={{ paddingTop: 0 }}>
          <div className="grid-2">
            {ranking.length > 0 && (
              <RankingTable ranking={ranking} onSelect={setSelectedId} selectedId={selectedId} />
            )}
            <AdvisoryChat stationId={selectedId} stationName={selectedStation?.name} />
          </div>
        </div>

        <div className="section" style={{ paddingTop: 0 }}>
          <AqiScale activeLabel={selectedReading?.category?.label} />
        </div>
      </main>

      {showLogin && <Login onClose={() => setShowLogin(false)} />}

      <footer style={{ borderTop: "1px solid var(--border-soft)", padding: "36px 0", textAlign: "center", marginTop: 20 }}>
        <div className="wrap">
          <div style={{ display: "flex", alignItems: "center", gap: 10, justifyContent: "center", marginBottom: 10 }}>
            <div className="brand-mark" style={{ width: 26, height: 26 }} />
            <span style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 16 }}>AirAware India</span>
          </div>
          <p style={{ margin: "0 auto", maxWidth: 560, color: "var(--text-faint)", fontSize: 12.5 }}>
            Built for the ET AI Hackathon · Urban Air Quality Intelligence. Data blends live sensor
            reads with modeled estimates where live data is unavailable.
            {!isFirebaseConfigured && " · Login not configured — see frontend/src/firebase.js"}
          </p>
        </div>
      </footer>
    </>
  );
}
