import { useState } from "react";
import { useAuth } from "../AuthContext";

export default function Login({ onClose }) {
  const { login, signup, loginWithGoogle, isFirebaseConfigured } = useAuth();
  const [mode, setMode] = useState("login"); // "login" | "signup"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await signup(email, password);
      }
      onClose();
    } catch (err) {
      setError(err.message || "Authentication failed.");
    } finally {
      setBusy(false);
    }
  }

  async function handleGoogle() {
    setError(null);
    setBusy(true);
    try {
      await loginWithGoogle();
      onClose();
    } catch (err) {
      setError(err.message || "Google sign-in failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.6)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 100,
        padding: 20,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="card"
        style={{ width: "100%", maxWidth: 400, position: "relative" }}
      >
        <button
          onClick={onClose}
          aria-label="Close"
          style={{
            position: "absolute",
            top: 14,
            right: 16,
            background: "transparent",
            border: "none",
            color: "var(--text-faint)",
            fontSize: 22,
            lineHeight: 1,
          }}
        >
          ×
        </button>

        <div className="section-label">Account</div>
        <h2 style={{ fontSize: 22, marginBottom: 18 }}>
          {mode === "login" ? "Welcome back" : "Create your account"}
        </h2>

        {!isFirebaseConfigured && (
          <div
            style={{
              background: "var(--bg-elevated)",
              border: "1px solid var(--accent-marigold)",
              borderRadius: "var(--radius-sm)",
              padding: "12px 14px",
              fontSize: 13,
              color: "var(--text-muted)",
              marginBottom: 16,
            }}
          >
            Login isn't configured yet. Paste your Firebase project config into{" "}
            <code>frontend/src/firebase.js</code> to enable sign-in. The rest of the
            dashboard works without an account.
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "grid", gap: 12 }}>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            style={inputStyle}
          />
          <input
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password (6+ characters)"
            style={inputStyle}
          />

          {error && (
            <div style={{ color: "var(--aqi-poor)", fontSize: 13 }}>{error}</div>
          )}

          <button
            type="submit"
            disabled={busy}
            style={{
              background: "var(--accent-marigold)",
              color: "#211A0D",
              border: "none",
              borderRadius: "var(--radius-sm)",
              padding: "11px",
              fontWeight: 600,
              fontSize: 15,
              opacity: busy ? 0.6 : 1,
            }}
          >
            {mode === "login" ? "Log in" : "Sign up"}
          </button>
        </form>

        <button
          onClick={handleGoogle}
          disabled={busy}
          style={{
            width: "100%",
            marginTop: 10,
            background: "var(--bg-elevated)",
            color: "var(--text-primary)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-sm)",
            padding: "11px",
            fontSize: 14,
            fontWeight: 500,
            opacity: busy ? 0.6 : 1,
          }}
        >
          Continue with Google
        </button>

        <div style={{ marginTop: 16, fontSize: 13.5, color: "var(--text-muted)", textAlign: "center" }}>
          {mode === "login" ? "New here?" : "Already have an account?"}{" "}
          <button
            onClick={() => {
              setMode(mode === "login" ? "signup" : "login");
              setError(null);
            }}
            style={{
              background: "none",
              border: "none",
              color: "var(--accent-teal)",
              fontSize: 13.5,
              fontWeight: 600,
              padding: 0,
            }}
          >
            {mode === "login" ? "Create an account" : "Log in"}
          </button>
        </div>
      </div>
    </div>
  );
}

const inputStyle = {
  width: "100%",
  background: "var(--bg-elevated)",
  color: "var(--text-primary)",
  border: "1px solid var(--border)",
  borderRadius: "var(--radius-sm)",
  padding: "11px 14px",
  fontSize: 15,
  fontFamily: "var(--font-body)",
};
