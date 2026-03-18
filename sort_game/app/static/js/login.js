const loginForm = document.getElementById("loginForm");
const loginError = document.getElementById("loginError");
console.log("login.js loaded");
function showLoginError(message) {
  if (!loginError) return;
  loginError.textContent = message;
  loginError.classList.remove("hidden");
}

function clearLoginError() {
  if (!loginError) return;
  loginError.textContent = "";
  loginError.classList.add("hidden");
}

async function loginRequest(email, password) {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });

  let result = null;

  try {
    result = await response.json();
  } catch {
    result = null;
  }

  return {
    ok: response.ok,
    result,
  };
}
console.log("loginForm:", loginForm);
if (loginForm) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearLoginError();

    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");

    const email = emailInput?.value.trim() || "";
    const password = passwordInput?.value || "";

    if (!email || !password) {
      showLoginError("メールアドレスとパスワードを入力してください。");
      return;
    }

    try {
      const { ok, result } = await loginRequest(email, password);
      console.log("login result:", result);

      if (!ok || !result?.success) {
        showLoginError(result?.error?.message || "ログインに失敗しました。");
        return;
      }

      if (!result.data?.accessToken || !result.data?.user) {
        showLoginError("ログインレスポンスが不正です。");
        return;
      }

      if (typeof saveAuth !== "function") {
        showLoginError("認証機能の読み込みに失敗しました。");
        return;
      }

      saveAuth(result.data);
      console.log("localStorage accessToken:", localStorage.getItem("accessToken"));
      console.log("localStorage user:", localStorage.getItem("user"));
      console.log("localStorage playMode:", localStorage.getItem("playMode"));

      console.log("Redirecting to game start page...");
      window.location.href = "/game-b-Description/start";
    } catch (error) {
      console.error("login error:", error);
      showLoginError("通信エラーが発生しました。");
    }
  });
}