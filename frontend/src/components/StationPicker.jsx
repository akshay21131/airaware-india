import { useEffect, useMemo, useRef, useState } from "react";

export default function StationPicker({ stations, selectedId, onSelect }) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);

  const selected = stations.find((s) => s.id === selectedId);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return stations.slice(0, 50);
    return stations
      .filter(
        (s) =>
          s.name.toLowerCase().includes(q) ||
          s.area.toLowerCase().includes(q) ||
          s.state.toLowerCase().includes(q)
      )
      .slice(0, 50);
  }, [query, stations]);

  useEffect(() => {
    function handleClick(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  return (
    <div ref={containerRef} style={{ position: "relative", maxWidth: 360 }}>
      <div style={{ position: "relative" }}>
        <span
          aria-hidden="true"
          style={{
            position: "absolute",
            left: 14,
            top: "50%",
            transform: "translateY(-50%)",
            fontSize: 15,
            opacity: 0.6,
            pointerEvents: "none",
          }}
        >
          🔍
        </span>
        <input
          value={open ? query : selected ? `${selected.name}, ${selected.state}` : ""}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => {
            setOpen(true);
            setQuery("");
          }}
          placeholder="Search any district…"
          style={{
            width: "100%",
            background: "var(--bg-elevated)",
            color: "var(--text-primary)",
            border: `1px solid ${open ? "var(--accent-teal)" : "var(--border)"}`,
            borderRadius: 999,
            padding: "11px 16px 11px 40px",
            fontFamily: "var(--font-body)",
            fontSize: 15,
            transition: "border-color 0.15s ease",
          }}
        />
      </div>
      {open && (
        <div
          style={{
            position: "absolute",
            top: "calc(100% + 6px)",
            left: 0,
            right: 0,
            maxHeight: 340,
            overflowY: "auto",
            background: "var(--bg-elevated)",
            border: "1px solid var(--border)",
            borderRadius: 14,
            zIndex: 30,
            boxShadow: "0 16px 44px rgba(0,0,0,0.5)",
            padding: 6,
          }}
        >
          {results.length === 0 && (
            <div style={{ padding: "12px 14px", color: "var(--text-faint)", fontSize: 13 }}>
              No districts match "{query}"
            </div>
          )}
          {results.map((s) => (
            <button
              key={s.id}
              onClick={() => {
                onSelect(s.id);
                setOpen(false);
                setQuery("");
              }}
              style={{
                display: "block",
                width: "100%",
                textAlign: "left",
                padding: "9px 14px",
                borderRadius: 9,
                background: s.id === selectedId ? "var(--bg-card-hover)" : "transparent",
                border: "none",
                color: "var(--text-primary)",
                fontSize: 14,
                transition: "background 0.12s ease",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "var(--bg-card-hover)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = s.id === selectedId ? "var(--bg-card-hover)" : "transparent")}
            >
              {s.name} <span style={{ color: "var(--text-faint)", fontSize: 12.5 }}>· {s.state}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
