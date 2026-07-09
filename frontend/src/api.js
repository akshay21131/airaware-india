const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function req(path, options) {
  const res = await fetch(`${BASE_URL}${path}`, options);
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  stations: () => req("/api/stations"),
  currentAll: (live = false) => req(`/api/aqi/current?live=${live}`),
  currentOne: (stationId) => req(`/api/aqi/current/${stationId}`),
  forecast: (stationId, hours = 72) => req(`/api/aqi/forecast/${stationId}?hours=${hours}`),
  weather: (stationId) => req(`/api/weather/${stationId}`),
  government: (stationId) => req(`/api/government/${stationId}`),
  ranking: (limit = 15, live = false) => req(`/api/ranking?limit=${limit}&live=${live}`),
  chat: (stationId, question) =>
    req("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ station_id: stationId, question }),
    }),
};
