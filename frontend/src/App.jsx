import { useEffect, useState } from "react";
import "./App.css";
import Workspace from "./Workspace";
import { api, clearTokens, getTokens, saveTokens } from "./api";

function AuthPage({ mode, onAuthenticated, onModeChange }) {
  const isSignUp = mode === "signup";
  const [form, setForm] = useState({ username: "", email: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  function update(event) { setForm((current) => ({ ...current, [event.target.name]: event.target.value })); setError(""); }
  async function submit(event) {
    event.preventDefault();
    if (isSignUp && form.password !== form.confirm) { setError("Passwords do not match."); return; }
    setBusy(true);
    try {
      const data = await api(`/api/auth/${isSignUp ? "register" : "login"}/`, { method: "POST", body: JSON.stringify({ username: form.username, password: form.password, ...(isSignUp ? { email: form.email } : {}) }) });
      saveTokens({ access: data.access, refresh: data.refresh });
      onAuthenticated(data.user || await api("/api/auth/me/"));
    } catch (requestError) { setError(requestError.message); } finally { setBusy(false); }
  }
  return <main className="auth-shell"><section className="auth-intro"><div className="auth-glow auth-glow-one" /><div className="auth-glow auth-glow-two" /><div className="auth-brand"><span className="brand-mark">SS</span><span><strong>Smart Study</strong><small>Room</small></span></div><div className="auth-copy"><p className="eyebrow">A QUIETER WAY TO LEARN</p><h1>Make space for better learning.</h1><p className="intro-copy">A calm, focused home for your subjects, tasks, notes, and progress.</p><div className="auth-rule" /><p className="quote">“Small sessions become remarkable progress.”</p></div><div className="auth-footnote"><span />Built for your next breakthrough</div></section><section className="auth-panel"><div className="auth-panel-inner"><p className="eyebrow">{isSignUp ? "START YOUR RHYTHM" : "WELCOME BACK"}</p><h2>{isSignUp ? "Create your account" : "Pick up where you left off"}</h2><p className="panel-copy">{isSignUp ? "Build a workspace that makes studying feel lighter." : "Your focused workspace is ready when you are."}</p><form onSubmit={submit}><label>Username<input name="username" value={form.username} onChange={update} autoComplete="username" placeholder="e.g. alex.study" required /></label>{isSignUp && <label>Email address<input type="email" name="email" value={form.email} onChange={update} autoComplete="email" placeholder="you@example.com" required /></label>}<label>Password<input type="password" name="password" value={form.password} onChange={update} autoComplete={isSignUp ? "new-password" : "current-password"} placeholder="At least 8 characters" minLength="8" required /></label>{isSignUp && <label>Confirm password<input type="password" name="confirm" value={form.confirm} onChange={update} autoComplete="new-password" placeholder="Repeat your password" minLength="8" required /></label>}{error && <p className="form-error" role="alert">{error}</p>}<button className="submit-button" disabled={busy}>{busy ? "Preparing your space..." : isSignUp ? "Create my workspace" : "Enter my workspace"}<span>→</span></button></form><p className="switch-copy">{isSignUp ? "Already have an account?" : "New to Smart Study?"} <button className="link-button" type="button" onClick={() => { setError(""); onModeChange(isSignUp ? "login" : "signup"); }}>{isSignUp ? "Sign in" : "Create an account"}</button></p></div></section></main>;
}

function App() {
  const [user, setUser] = useState(null); const [mode, setMode] = useState("login"); const [checking, setChecking] = useState(true);
  useEffect(() => { const tokens = getTokens(); if (!tokens) { setChecking(false); return; } api("/api/auth/me/").then(setUser).catch(() => clearTokens()).finally(() => setChecking(false)); }, []);
  async function logout() { try { await api("/api/auth/logout/", { method: "POST", body: JSON.stringify({ refresh: getTokens()?.refresh }) }); } catch { /* Clear local state when the refresh token is already invalid. */ } clearTokens(); setUser(null); setMode("login"); }
  if (checking) return <div className="loading auth-loading"><span className="spinner" />Loading your workspace...</div>;
  return user ? <Workspace user={user} onLogout={logout} /> : <AuthPage mode={mode} onAuthenticated={setUser} onModeChange={setMode} />;
}

export default App;