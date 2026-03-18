let latestBattlePayload = null;

function setLatestBattlePayload(payload) {
  if (!payload || typeof payload !== "object") {
    latestBattlePayload = null;
    return;
  }

  latestBattlePayload = payload;
}

function getLatestBattlePayload() {
  return latestBattlePayload;
}

async function saveLatestBattle() {
  const payload = getLatestBattlePayload();

  if (!payload) {
    return {
      success: false,
      error: {
        code: "NO_BATTLE_RESULT",
        message: "先にバトルを実行してください",
      },
    };
  }

  const token = typeof getAccessToken === "function" ? getAccessToken() : null;

  if (!token) {
    return {
      success: false,
      error: {
        code: "AUTH_REQUIRED",
        message: "保存にはログインが必要です",
      },
    };
  }

  try {
    const response = await fetch("/api/battles", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json().catch(() => null);

    if (response.status === 401) {
      if (typeof clearAuth === "function") {
        clearAuth();
      }
      setLatestBattlePayload(null);

      return {
        success: false,
        error: {
          code: "AUTH_UNAUTHORIZED",
          message:
            data?.error?.message ||
            "ログイン状態が無効です。再ログインしてください",
        },
      };
    }

    if (!response.ok || !data?.success) {
      return {
        success: false,
        error: {
          code: data?.error?.code || "SAVE_FAILED",
          message: data?.error?.message || "保存に失敗しました",
        },
      };
    }

    return {
      success: true,
      data: data.data,
    };
  } catch (error) {
    return {
      success: false,
      error: {
        code: "NETWORK_ERROR",
        message: "通信エラーが発生しました",
      },
    };
  }
}

async function fetchBattleHistory(limit = 10) {
  const token = typeof getAccessToken === "function" ? getAccessToken() : null;

  if (!token) {
    return {
      success: false,
      error: {
        code: "AUTH_REQUIRED",
        message: "履歴取得にはログインが必要です",
      },
    };
  }

  try {
    const response = await fetch(
      `/api/battles?limit=${encodeURIComponent(limit)}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    const data = await response.json().catch(() => null);

    if (response.status === 401) {
      if (typeof clearAuth === "function") {
        clearAuth();
      }
      setLatestBattlePayload(null);

      return {
        success: false,
        error: {
          code: "AUTH_UNAUTHORIZED",
          message:
            data?.error?.message ||
            "ログイン状態が無効です。再ログインしてください",
        },
      };
    }

    if (!response.ok || !data?.success) {
      return {
        success: false,
        error: {
          code: data?.error?.code || "HISTORY_FETCH_FAILED",
          message: data?.error?.message || "履歴取得に失敗しました",
        },
      };
    }

    return {
      success: true,
      data: data.data,
    };
  } catch (error) {
    return {
      success: false,
      error: {
        code: "NETWORK_ERROR",
        message: "通信エラーが発生しました",
      },
    };
  }
}

async function fetchStatistics(limit = 10) {
  const token = typeof getAccessToken === "function" ? getAccessToken() : null;

  if (!token) {
    return {
      success: false,
      error: {
        code: "AUTH_REQUIRED",
        message: "統計取得にはログインが必要です",
      },
    };
  }

  try {
    const response = await fetch(
      `/api/statistics?limit=${encodeURIComponent(limit)}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    const data = await response.json().catch(() => null);

    if (response.status === 401) {
      if (typeof clearAuth === "function") {
        clearAuth();
      }
      setLatestBattlePayload(null);

      return {
        success: false,
        error: {
          code: "AUTH_UNAUTHORIZED",
          message:
            data?.error?.message ||
            "ログイン状態が無効です。再ログインしてください",
        },
      };
    }

    if (!response.ok || !data?.success) {
      return {
        success: false,
        error: {
          code: data?.error?.code || "STATISTICS_FETCH_FAILED",
          message: data?.error?.message || "統計取得に失敗しました",
        },
      };
    }

    return {
      success: true,
      data: data.data,
    };
  } catch (error) {
    return {
      success: false,
      error: {
        code: "NETWORK_ERROR",
        message: "通信エラーが発生しました",
      },
    };
  }
}