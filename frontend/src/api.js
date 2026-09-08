const tokenKey = "smart-study-tokens";
const apiBase = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export function getTokens() {
  try {
    return JSON.parse(localStorage.getItem(tokenKey)) || null;
  } catch {
    return null;
  }
}

export function saveTokens(tokens) {
  localStorage.setItem(tokenKey, JSON.stringify(tokens));
}

export function clearTokens() {
  localStorage.removeItem(tokenKey);
}

export async function api(path, options = {}) {
  const apiPath = path.startsWith("/api/")
    ? path
    : `/api${path}`;

  async function request(access) {
    return fetch(`${apiBase}${apiPath}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(access ? { Authorization: `Bearer ${access}` } : {}),
        ...options.headers,
      },
    });
  }

  let tokens = getTokens();
  let response = await request(tokens?.access);
  if (response.status === 401 && tokens?.refresh && !options.skipRefresh) {
    const refreshResponse = await fetch(`${apiBase}/api/auth/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: tokens.refresh }),
    });
    if (refreshResponse.ok) {
      const refreshed = await refreshResponse.json();
      tokens = { ...tokens, access: refreshed.access };
      saveTokens(tokens);
      response = await request(tokens.access);
    } else {
      clearTokens();
    }
  }

  const body = await response.text();

  let data = null;

  if (body.trim()) {
    try {
      data = JSON.parse(body);
    } catch {
      throw new Error(
        `Server returned an invalid response (${response.status}).`
      );
    }
  }

  if (!response.ok) {
    const first = Object.values(data || {})[0];

    throw new Error(
      data?.detail ||
        (Array.isArray(first) ? first[0] : first) ||
        `Request failed (${response.status}).`
    );
  }

  return data;
}

export { tokenKey };