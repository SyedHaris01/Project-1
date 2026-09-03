import { useEffect, useState } from "react";
import "./App.css";

const tokenKey = "smart-study-tokens";

function getTokens() {
  try { return JSON.parse(localStorage.getItem(tokenKey)) || null; } catch { return null; }
}

async function api(path, options = {}) {
  const tokens = getTokens();
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(tokens?.access ? { Authorization: `Bearer ${tokens.access}` } : {}), ...options.headers },
  });
  const body = await response.text();
  let data = null;
  if (body.trim()) {
    try {
      data = JSON.parse(body);
    } catch {
      throw new Error(`Server returned an invalid response (${response.status}).`);
    }
  }
  if (!response.ok) {
    const firstError = Object.values(data || {})[0];
    throw new Error(data?.detail || (Array.isArray(firstError) ? firstError[0] : firstError) || `Request failed (${response.status}).`);
  }
  return data;
}

function AuthPage({ mode, onAuthenticated, onModeChange }) {
  const isSignUp = mode === "signup";
  const [form, setForm] = useState({ username: "", email: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  function update(event) { setForm({ ...form, [event.target.name]: event.target.value }); setError(""); }
  async function submit(event) {
    event.preventDefault();
    if (isSignUp && form.password !== form.confirm) return setError("Passwords do not match.");
    setBusy(true);
    try {
      const data = await api(`/api/auth/${isSignUp ? "register" : "login"}/`, { method: "POST", body: JSON.stringify({ username: form.username, password: form.password, ...(isSignUp ? { email: form.email } : {}) }) });
      localStorage.setItem(tokenKey, JSON.stringify({ access: data.access, refresh: data.refresh }));
      onAuthenticated(data.user || await api("/api/auth/me/"));
    } catch (requestError) { setError(requestError.message); } finally { setBusy(false); }
  }
  return <main className="auth-shell"><section className="auth-intro"><div className="brand-mark">SS</div><p className="eyebrow">SMART STUDY ROOM</p><h1>Make room for better learning.</h1><p className="intro-copy">A calm, focused home for your subjects, tasks, notes, and progress.</p><div className="intro-rule" /><p className="quote">“Small sessions become remarkable progress.”</p></section><section className="auth-panel"><p className="eyebrow">YOUR WORKSPACE</p><h2>{isSignUp ? "Create your account" : "Welcome back"}</h2><p className="panel-copy">{isSignUp ? "Start building your most productive study rhythm." : "Sign in to pick up where you left off."}</p><form onSubmit={submit}><label>Username<input name="username" value={form.username} onChange={update} autoComplete="username" required /></label>{isSignUp && <label>Email address<input type="email" name="email" value={form.email} onChange={update} autoComplete="email" required /></label>}<label>Password<input type="password" name="password" value={form.password} onChange={update} autoComplete={isSignUp ? "new-password" : "current-password"} minLength="8" required /></label>{isSignUp && <label>Confirm password<input type="password" name="confirm" value={form.confirm} onChange={update} autoComplete="new-password" minLength="8" required /></label>}{error && <p className="form-error" role="alert">{error}</p>}<button className="submit-button" disabled={busy}>{busy ? "Please wait..." : isSignUp ? "Create account" : "Sign in"}</button></form><p className="switch-copy">{isSignUp ? "Already have an account?" : "New to Smart Study?"} <button className="link-button" onClick={() => onModeChange(isSignUp ? "login" : "signup")}>{isSignUp ? "Sign in" : "Create an account"}</button></p></section></main>;
}
 
function Dashboard({ user, onLogout }) {
  const [subjects, setSubjects] = useState([]);
  useEffect(() => { api("/api/subjects/").then(setSubjects).catch(() => {}); }, []);
  const initials = user.username.slice(0, 1).toUpperCase();
  return <div className="dashboard"><aside className="sidebar"><div className="logo"><span className="logo-mark">SS</span><span>Smart Study</span></div><nav><a className="active">Dashboard</a><a>Subjects</a><a>Tasks</a><a>Notes</a><a>Progress</a></nav><button className="logout" onClick={onLogout}>↪ <span>Log out</span></button></aside><main className="main"><header className="topbar"><div><p className="eyebrow">SMART STUDY ROOM</p><h1>Good morning, {user.username}.</h1><p className="subtitle">Stay organized. Study smarter. Achieve more.</p></div><div className="profile"><div className="avatar">{initials}</div><div><strong>{user.username}</strong><p>Student</p></div></div></header><section className="welcome"><div><p className="eyebrow">TODAY'S FOCUS</p><h2>Welcome back.</h2><p>Your learning journey starts here. Let’s make today productive.</p></div><button className="primary-btn">+ Add study session</button></section><section className="stats"><Stat icon="01" label="Subjects" value={subjects.length} /><Stat icon="02" label="Active tasks" value="8" /><Stat icon="03" label="Notes" value="12" /><Stat icon="04" label="Study hours" value="12.5h" /></section><section className="content-grid"><div className="card"><div className="card-header"><div><h2>My subjects</h2><p>Your current learning subjects</p></div><button className="text-btn">View all →</button></div><div className="subject-list">{subjects.length ? subjects.map((subject) => <div className="subject" key={subject.id}><div className="subject-icon" style={{ backgroundColor: `${subject.color}22`, color: subject.color }}>●</div><div><strong>{subject.name}</strong><p>{subject.description || "Ready for your next session"}</p></div><span>—</span></div>) : <p className="empty">No subjects yet. Add your first one to begin.</p>}</div></div><div className="card"><div className="card-header"><div><h2>Today’s tasks</h2><p>Keep your day productive</p></div><button className="text-btn">View all →</button></div><div className="task-list"><Task text="Complete React practice" time="Today · 10:00 AM" /><Task text="Read Database chapter 4" time="Today · 2:00 PM" /><Task text="Review Python notes" time="Completed" done /></div></div></section><section className="card progress-card"><div className="card-header"><div><h2>Weekly progress</h2><p>Your study performance this week</p></div><strong className="progress-number">78%</strong></div><div className="progress-bar"><div className="progress-fill" /></div><div className="progress-info"><span>12.5 hours studied</span><span>Goal: 16 hours</span></div></section></main></div>;
}
function Stat({ icon, label, value }) { return <div className="stat-card"><div className="stat-icon">{icon}</div><div><p>{label}</p><h3>{value}</h3></div></div>; }
function Task({ text, time, done }) { return <div className={`task ${done ? "completed" : ""}`}><input type="checkbox" checked={done} readOnly /><div><strong>{text}</strong><p>{time}</p></div></div>; }
function App() {
  const [user, setUser] = useState(null); const [mode, setMode] = useState("login"); const [checking, setChecking] = useState(true);
  useEffect(() => { if (getTokens()) api("/api/auth/me/").then(setUser).catch(() => localStorage.removeItem(tokenKey)).finally(() => setChecking(false)); else setChecking(false); }, []);
  async function logout() { try { await api("/api/auth/logout/", { method: "POST", body: JSON.stringify({ refresh: getTokens()?.refresh }) }); } catch {} localStorage.removeItem(tokenKey); setUser(null); }
  if (checking) return <div className="loading">Loading your workspace...</div>;
  return user ? <Dashboard user={user} onLogout={logout} /> : <AuthPage mode={mode} onAuthenticated={setUser} onModeChange={setMode} />;
}
export default App;
