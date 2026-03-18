const AUTH_KEYS = Object.freeze({
  ACCESS_TOKEN: "accessToken",
  USER: "user",
  PLAY_MODE: "playMode",
});

function getPlayMode() {
  return localStorage.getItem(AUTH_KEYS.PLAY_MODE) || "guest";
}

function getAccessToken() {
  if (getPlayMode() !== "auth") {
    return null;
  }

  return localStorage.getItem(AUTH_KEYS.ACCESS_TOKEN);
}

function getCurrentUser() {
  if (getPlayMode() !== "auth") {
    return null;
  }

  const raw = localStorage.getItem(AUTH_KEYS.USER);
  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function isLoggedIn() {
  const token = getAccessToken();
  const user = getCurrentUser();
  return Boolean(token && user);
}

function saveAuth(authData) {
  if (!authData?.accessToken || !authData?.user) {
    throw new Error("Invalid auth data");
  }

  localStorage.setItem(AUTH_KEYS.PLAY_MODE, "auth");
  localStorage.setItem(AUTH_KEYS.ACCESS_TOKEN, authData.accessToken);
  localStorage.setItem(AUTH_KEYS.USER, JSON.stringify(authData.user));
}

function clearAuth() {
  localStorage.removeItem(AUTH_KEYS.ACCESS_TOKEN);
  localStorage.removeItem(AUTH_KEYS.USER);
  localStorage.setItem(AUTH_KEYS.PLAY_MODE, "guest");
}

function startGuestMode() {
  clearAuth();
}

async function fetchWithAuth(url, options = {}) {
  const token = getAccessToken();

  const headers = {
    ...(options.headers || {}),
  };

  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  let response;
  let data = null;

  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch (error) {
    return {
      success: false,
      status: 0,
      data: null,
      error: {
        message: "通信に失敗しました",
        detail: error?.message || null,
      },
      raw: null,
    };
  }

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (response.status === 401) {
    clearAuth();
  }

  return {
    success: response.ok && data?.success !== false,
    status: response.status,
    data: data?.data ?? null,
    error: data?.error ?? null,
    raw: data,
  };
}