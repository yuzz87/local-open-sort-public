/* ==============================
   Config
============================== */

const CONFIG = Object.freeze({
  /* ===== 可視化設定 ===== */
  VIS_ARRAY_SIZE: 40,
  VIS_DELAY: 8,

  BAR_W: 6,
  BAR_GAP: 1,
  HEIGHT_SCALE: 4,

  /* ===== C++ベンチマーク ===== */
  BENCHMARK_ARRAY_SIZE: 2000,

  /* ===== API ===== */
  API_TIMEOUT_MS: 10000,

  /* ===== 統計 ===== */
  HISTORY_LIMIT: 10,
});

/* ==============================
   Algorithm Registry
============================== */

const ALGORITHMS = Object.freeze({
  バブル: bubbleSteps,
  選択: selectionSteps,
  挿入: insertionSteps,
  マージ: mergeSteps,
  クイック: quickSteps,
  ヒープ: heapSteps,
});

/* C++側識別子 */
const ENGINE_ALGO_KEY = Object.freeze({
  バブル: "bubble",
  選択: "selection",
  挿入: "insertion",
  マージ: "merge",
  クイック: "quick",
  ヒープ: "heap",
});

const ENGINE_KEY_TO_JA = Object.freeze(
  Object.fromEntries(
    Object.entries(ENGINE_ALGO_KEY).map(([ja, key]) => [key, ja]),
  ),
);

const EXPECTED_ENGINE_KEYS = Object.freeze(Object.values(ENGINE_ALGO_KEY));
const EXPECTED_JA_NAMES = Object.freeze(Object.keys(ALGORITHMS));

/* ==============================
   DOM References
============================== */

const DOM = Object.freeze({
  grid: document.getElementById("battle-grid"),
  startBtn: document.getElementById("start-battle"),
  generateBtn: document.getElementById("generate-board"),
  result: document.getElementById("prediction-result"),
  stats: document.getElementById("statistics"),
  history: document.getElementById("battleHistory"),
  canvas: document.getElementById("fireworks-canvas"),
  rankSlots: Array.from(document.querySelectorAll(".slot")),
  algoPool: document.getElementById("algo-pool"),
  authStatus: document.getElementById("authStatus"),
  loginLink: document.getElementById("loginLink"),
  logoutBtn: document.getElementById("logoutBtn"),
  saveBattleBtn: document.getElementById("saveBattleBtn"),
  saveMessage: document.getElementById("saveMessage"),
  guestMessage: document.getElementById("guestMessage"),
  guestLoginBtn: document.getElementById("guestLoginBtn"),
  recordsHeader: document.querySelector(".records-header"),
  recordsAccordion: document.querySelector(".records-accordion"),
});

/* ==============================
   State
============================== */

const BattleState = {
  running: false,
};

let fireworksRunning = false;
let fireworksResizeHandler = null;

/* ==============================
   Shared Helpers
============================== */

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function clearChildren(element) {
  if (!element) return;
  while (element.firstChild) {
    element.removeChild(element.firstChild);
  }
}

function createNode(tag, className, text) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text != null) el.textContent = text;
  return el;
}

function formatDateTime(value) {
  if (!value) return "";

  try {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return String(value);
    }
    return date.toLocaleString("ja-JP");
  } catch {
    return String(value);
  }
}

function makeValues(size) {
  const arr = Array.from({ length: size }, (_, i) => i + 1);

  for (let i = arr.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }

  return arr;
}

/* ==============================
   Message / UI Helpers
============================== */

function showMessageLines(lines, type = "normal") {
  if (!DOM.result) return;

  const safeType =
    type === "error" ? "error" : type === "success" ? "success" : "normal";

  clearChildren(DOM.result);

  const wrapper = document.createElement("span");
  wrapper.className = `message-${safeType}`;

  lines.forEach((line, index) => {
    if (index > 0) {
      wrapper.appendChild(document.createElement("br"));
    }
    wrapper.appendChild(document.createTextNode(String(line)));
  });

  DOM.result.appendChild(wrapper);
}

function showError(message) {
  showMessageLines([message], "error");
}

function clearMessage() {
  if (!DOM.result) return;
  clearChildren(DOM.result);
}

function showSaveMessage(message, type = "normal") {
  if (!DOM.saveMessage) return;

  DOM.saveMessage.textContent = message || "";
  DOM.saveMessage.classList.remove(
    "message-normal",
    "message-success",
    "message-error",
  );

  const safeType =
    type === "error"
      ? "message-error"
      : type === "success"
        ? "message-success"
        : "message-normal";

  if (message) {
    DOM.saveMessage.classList.add(safeType);
  }
}

function clearCardDecorations() {
  EXPECTED_JA_NAMES.forEach((name) => {
    const card = document.getElementById(`card-${name}`);
    if (!card) return;

    card.classList.remove("rank-1", "rank-2", "rank-3");
    card.querySelectorAll(".time-label").forEach((el) => el.remove());
  });
}

function clearStatistics(message = "") {
  if (!DOM.stats) return;
  clearChildren(DOM.stats);
  if (message) {
    DOM.stats.textContent = message;
  }
}

function clearHistory(message = "") {
  if (!DOM.history) return;
  clearChildren(DOM.history);
  if (message) {
    DOM.history.textContent = message;
  }
}

function resetPredictionSlots() {
  DOM.rankSlots.forEach((slot, index) => {
    delete slot.dataset.value;
    clearChildren(slot);
    slot.textContent =
      index === 0 ? "🥇 1位" : index === 1 ? "🥈 2位" : "🥉 3位";
  });
}

function setButtonBusy(isBusy) {
  if (DOM.startBtn) {
    DOM.startBtn.disabled = isBusy;
    DOM.startBtn.textContent = isBusy ? "実行中..." : "開始";
  }

  if (DOM.generateBtn) {
    DOM.generateBtn.disabled = isBusy;
  }

  if (DOM.saveBattleBtn) {
    DOM.saveBattleBtn.disabled = isBusy || !getSafeLoggedInState();
  }
}

/* ==============================
   Network
============================== */

async function fetchJson(url, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), CONFIG.API_TIMEOUT_MS);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });

    const contentType = response.headers.get("content-type") || "";
    let data = null;

    if (contentType.includes("application/json")) {
      data = await response.json().catch(() => null);
    } else {
      const text = await response.text().catch(() => "");
      data = text ? { raw: text } : null;
    }

    return {
      ok: response.ok,
      status: response.status,
      data,
      error: null,
    };
  } catch (error) {
    return {
      ok: false,
      status: 0,
      data: null,
      error,
    };
  } finally {
    clearTimeout(timer);
  }
}

/* ==============================
   Board Rendering
============================== */

function createBoards(values) {
  if (!DOM.grid) return;

  clearChildren(DOM.grid);
  const fragment = document.createDocumentFragment();

  EXPECTED_JA_NAMES.forEach((name) => {
    const card = createNode("div", "battle-card");
    card.id = `card-${name}`;

    const title = createNode("div", "battle-title", name);

    const board = createNode("div", "mini-board");
    board.id = `board-${name}`;

    values.forEach((v, i) => {
      const bar = createNode("div", "mini-bar");
      bar.style.left = `${i * (CONFIG.BAR_W + CONFIG.BAR_GAP)}px`;
      bar.style.width = `${CONFIG.BAR_W}px`;
      bar.style.height = `${v * CONFIG.HEIGHT_SCALE}px`;
      board.appendChild(bar);
    });

    card.appendChild(title);
    card.appendChild(board);
    fragment.appendChild(card);
  });

  DOM.grid.appendChild(fragment);
}

/* ==============================
   Prediction UI
============================== */

function initDragPrediction() {
  if (!DOM.algoPool || DOM.rankSlots.length === 0) return;

  clearChildren(DOM.algoPool);
  let draggedCard = null;

  EXPECTED_JA_NAMES.forEach((name) => {
    const card = createNode("div", "algo-card", name);
    card.draggable = true;

    card.addEventListener("dragstart", (event) => {
      draggedCard = card;
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("text/plain", name);
    });

    card.addEventListener("dragend", () => {
      draggedCard = null;
    });

    DOM.algoPool.appendChild(card);
  });

  DOM.rankSlots.forEach((slot) => {
    slot.addEventListener("dragover", (event) => {
      event.preventDefault();
      event.dataTransfer.dropEffect = "move";
    });

    slot.addEventListener("drop", (event) => {
      event.preventDefault();

      if (!draggedCard) return;
      if (slot.contains(draggedCard)) return;

      const existingCard = slot.querySelector(".algo-card");
      if (existingCard) {
        DOM.algoPool.appendChild(existingCard);
      }

      clearChildren(slot);
      slot.appendChild(draggedCard);
      slot.dataset.value = draggedCard.textContent || "";

      draggedCard.classList.add("dropped");
      const currentCard = draggedCard;
      setTimeout(() => {
        currentCard.classList.remove("dropped");
      }, 200);

      draggedCard = null;
    });
  });
}

function getPredictionPicks() {
  return DOM.rankSlots.map((slot) => slot.dataset.value || "");
}

function validatePrediction() {
  const picks = getPredictionPicks();
  if (picks.length !== 3) return false;
  if (picks.some((value) => !value)) return false;
  return new Set(picks).size === picks.length;
}

/* ==============================
   Effects
============================== */

function launchFireworks() {
  if (fireworksRunning) return;
  if (!DOM.canvas) return;

  const canvas = DOM.canvas;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  fireworksRunning = true;

  const resizeCanvas = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  };

  resizeCanvas();
  fireworksResizeHandler = resizeCanvas;
  window.addEventListener("resize", fireworksResizeHandler);

  const particles = Array.from({ length: 150 }, () => ({
    x: canvas.width / 2,
    y: canvas.height / 2,
    angle: Math.random() * Math.PI * 2,
    speed: Math.random() * 6 + 2,
    life: 80,
    color: `hsl(${Math.random() * 360},100%,60%)`,
  }));

  function cleanup() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    fireworksRunning = false;

    if (fireworksResizeHandler) {
      window.removeEventListener("resize", fireworksResizeHandler);
      fireworksResizeHandler = null;
    }
  }

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach((particle) => {
      if (particle.life <= 0) return;

      particle.x += Math.cos(particle.angle) * particle.speed;
      particle.y += Math.sin(particle.angle) * particle.speed;
      particle.life -= 1;

      ctx.fillStyle = particle.color;
      ctx.fillRect(particle.x, particle.y, 3, 3);
    });

    if (particles.some((particle) => particle.life > 0)) {
      requestAnimationFrame(animate);
      return;
    }

    cleanup();
  }

  animate();
}

/* ==============================
   Data Validation / Normalization
============================== */

function isValidRankingRow(row) {
  if (!row || typeof row !== "object") return false;

  const rank = Number(row.rank);
  const duration = Number(row.duration_ms);
  const algorithmKey = String(row.algorithm);

  return (
    Number.isInteger(rank) &&
    rank >= 1 &&
    rank <= EXPECTED_ENGINE_KEYS.length &&
    Number.isFinite(duration) &&
    duration >= 0 &&
    EXPECTED_ENGINE_KEYS.includes(algorithmKey)
  );
}

function normalizeRanking(rawRanking) {
  if (!Array.isArray(rawRanking)) {
    throw new Error("ranking が配列ではありません");
  }

  if (rawRanking.length !== EXPECTED_ENGINE_KEYS.length) {
    throw new Error(
      `ranking件数が不正です: expected=${EXPECTED_ENGINE_KEYS.length}, actual=${rawRanking.length}`,
    );
  }

  const normalized = rawRanking
    .map((row) => {
      if (!isValidRankingRow(row)) {
        throw new Error("ranking 内の要素形式が不正です");
      }

      const algorithmKey = String(row.algorithm);
      const algorithmJa = ENGINE_KEY_TO_JA[algorithmKey];

      if (!algorithmJa) {
        throw new Error(`未対応の algorithm です: ${algorithmKey}`);
      }

      return {
        rank: Number(row.rank),
        algorithmKey,
        algorithmJa,
        duration_ms: Number(row.duration_ms),
      };
    })
    .sort((a, b) => a.rank - b.rank);

  const rankSet = new Set(normalized.map((item) => item.rank));
  const algoSet = new Set(normalized.map((item) => item.algorithmKey));

  if (rankSet.size !== EXPECTED_ENGINE_KEYS.length) {
    throw new Error("rank が重複または欠損しています");
  }

  if (algoSet.size !== EXPECTED_ENGINE_KEYS.length) {
    throw new Error("algorithm が重複または欠損しています");
  }

  for (let i = 0; i < EXPECTED_ENGINE_KEYS.length; i += 1) {
    if (normalized[i].rank !== i + 1) {
      throw new Error("rank が 1 位から連番になっていません");
    }
  }

  return normalized;
}

function normalizeHistoryResponseData(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.rows)) return data.rows;
  return [];
}

function normalizeStatisticsResponseData(data) {
  if (Array.isArray(data)) {
    return data.map((row) => ({
      algorithm: String(row?.algorithm ?? ""),
      avg_duration_ms: Number(row?.avg_duration_ms ?? 0),
      wins: Number(row?.wins ?? 0),
      plays: Number(row?.plays ?? 0),
      win_rate: Number(row?.win_rate ?? 0),
      rank_counts: {
        1: Number(
          row?.rank_1 ??
            row?.rank_counts?.[1] ??
            row?.rank_counts?.["1"] ??
            row?.wins ??
            0,
        ),
        2: Number(
          row?.rank_2 ?? row?.rank_counts?.[2] ?? row?.rank_counts?.["2"] ?? 0,
        ),
        3: Number(
          row?.rank_3 ?? row?.rank_counts?.[3] ?? row?.rank_counts?.["3"] ?? 0,
        ),
      },
    }));
  }

  if (Array.isArray(data?.items))
    return normalizeStatisticsResponseData(data.items);
  if (Array.isArray(data?.rows))
    return normalizeStatisticsResponseData(data.rows);

  if (data && typeof data === "object") {
    return Object.entries(data).map(([algorithm, value]) => ({
      algorithm,
      avg_duration_ms: Number(value?.avg_duration_ms ?? 0),
      wins: Number(value?.wins ?? 0),
      plays: Number(value?.plays ?? 0),
      win_rate: Number(value?.win_rate ?? 0),
      rank_counts: {
        1: Number(
          value?.rank_1 ??
            value?.rank_counts?.[1] ??
            value?.rank_counts?.["1"] ??
            value?.wins ??
            0,
        ),
        2: Number(
          value?.rank_2 ??
            value?.rank_counts?.[2] ??
            value?.rank_counts?.["2"] ??
            0,
        ),
        3: Number(
          value?.rank_3 ??
            value?.rank_counts?.[3] ??
            value?.rank_counts?.["3"] ??
            0,
        ),
      },
    }));
  }

  return [];
}

function groupBattleHistory(rows) {
  const grouped = new Map();

  rows.forEach((row) => {
    const battleId = Number(row?.battle_id);
    if (!Number.isInteger(battleId)) return;

    if (!grouped.has(battleId)) {
      grouped.set(battleId, {
        battle_id: battleId,
        user_id:
          row?.user_id == null || row?.user_id === ""
            ? null
            : Number(row.user_id),
        array_size: Number(row?.array_size ?? 0),
        benchmark_size: Number(row?.benchmark_size ?? 0),
        status: row?.status ?? "",
        created_at: row?.created_at ?? "",
        results: [],
      });
    }

    const algorithm = String(row?.algorithm ?? "");
    const duration_ms = Number(row?.duration_ms);
    const rank = Number(row?.rank);

    if (
      !algorithm ||
      !Number.isFinite(duration_ms) ||
      !Number.isInteger(rank)
    ) {
      return;
    }

    grouped.get(battleId).results.push({
      algorithm,
      duration_ms,
      rank,
    });
  });

  return Array.from(grouped.values())
    .map((battle) => ({
      ...battle,
      results: battle.results.sort((a, b) => a.rank - b.rank),
    }))
    .sort((a, b) => b.battle_id - a.battle_id);
}

/* ==============================
   Auth UI
============================== */

function getSafeLoggedInState() {
  try {
    if (typeof isLoggedIn === "function") {
      return Boolean(isLoggedIn());
    }
    if (typeof window.isLoggedIn === "boolean") {
      return Boolean(window.isLoggedIn);
    }
    return false;
  } catch {
    return false;
  }
}

function getSafeCurrentUser() {
  try {
    return typeof getCurrentUser === "function" ? getCurrentUser() : null;
  } catch {
    return null;
  }
}

function clearLatestBattlePayloadSafe() {
  if (typeof setLatestBattlePayload === "function") {
    setLatestBattlePayload(null);
  }
}

function startGuestModeSafe() {
  if (typeof startGuestMode === "function") {
    startGuestMode();
    return;
  }

  if (typeof clearAuth === "function") {
    clearAuth();
  }
}

function renderAuthPanel() {
  const loggedIn = getSafeLoggedInState();
  const user = getSafeCurrentUser();

  if (DOM.authStatus) {
    DOM.authStatus.textContent =
      loggedIn && user?.username ? `Login: ${user.username}` : "Guest Mode";
  }

  if (DOM.loginLink) {
    DOM.loginLink.classList.toggle("hidden", loggedIn);
  }

  if (DOM.logoutBtn) {
    DOM.logoutBtn.classList.toggle("hidden", !loggedIn);
  }

  if (DOM.saveBattleBtn) {
    DOM.saveBattleBtn.classList.toggle("hidden", !loggedIn);
    DOM.saveBattleBtn.disabled = !loggedIn || Boolean(BattleState.running);
  }

  if (DOM.guestMessage) {
    DOM.guestMessage.classList.toggle("hidden", loggedIn);
  }
}

function bindAuthActions() {
  DOM.logoutBtn?.addEventListener("click", async () => {
    if (typeof clearAuth === "function") {
      clearAuth();
    }

    clearLatestBattlePayloadSafe();
    showSaveMessage("");
    renderAuthPanel();
    clearStatistics("ログインすると統計を表示できます");
    clearHistory("ログインすると保存済み履歴を表示できます");
    clearMessage();
    clearCardDecorations();
    resetPredictionSlots();
    createBoards(makeValues(CONFIG.VIS_ARRAY_SIZE));
  });

  DOM.saveBattleBtn?.addEventListener("click", async () => {
    await handleSaveBattle();
  });

  DOM.guestLoginBtn?.addEventListener("click", async () => {
    startGuestModeSafe();
    clearLatestBattlePayloadSafe();
    showSaveMessage("");
    clearMessage();
    clearStatistics("ログインすると統計を表示できます");
    clearHistory("ログインすると保存済み履歴を表示できます");
    resetPredictionSlots();
    clearCardDecorations();
    createBoards(makeValues(CONFIG.VIS_ARRAY_SIZE));
    renderAuthPanel();
  });
}

/* ==============================
   Saved Records / Statistics
============================== */

function renderBattleHistory(rows) {
  if (!DOM.history) return;

  clearChildren(DOM.history);

  if (!Array.isArray(rows) || rows.length === 0) {
    DOM.history.textContent = "保存済み履歴はありません";
    return;
  }

  const grouped = groupBattleHistory(rows);

  if (grouped.length === 0) {
    DOM.history.textContent = "保存済み履歴はありません";
    return;
  }

  grouped.forEach((battle) => {
    const box = createNode("div", "history-item");

    const title = createNode(
      "div",
      "history-title",
      `Battle #${battle.battle_id} / array_size=${battle.array_size} / benchmark_size=${battle.benchmark_size}`,
    );

    const userText =
      battle.user_id == null || Number.isNaN(battle.user_id)
        ? "guest"
        : `user_id=${battle.user_id}`;

    const meta = createNode(
      "div",
      "history-meta",
      `${formatDateTime(battle.created_at)} / ${userText} / status=${battle.status || "-"}`,
    );

    const list = createNode("ul", "history-results");

    battle.results.forEach((result) => {
      const jaName = ENGINE_KEY_TO_JA[result.algorithm] || result.algorithm;
      const item = createNode(
        "li",
        "",
        `${result.rank}位: ${jaName} (${Number(result.duration_ms).toFixed(3)} ms)`,
      );
      list.appendChild(item);
    });

    box.appendChild(title);
    box.appendChild(meta);
    box.appendChild(list);
    DOM.history.appendChild(box);
  });
}

function renderApiStatistics(rows) {
  if (!DOM.stats) return;

  clearChildren(DOM.stats);

  if (!Array.isArray(rows) || rows.length === 0) {
    DOM.stats.textContent = "保存済み統計はありません";
    return;
  }

  const fragment = document.createDocumentFragment();
  const title = createNode("h4", "", "保存済み統計");
  fragment.appendChild(title);

  rows.forEach((row) => {
    const algorithm = String(row?.algorithm ?? "");
    if (!algorithm) return;

    const jaName = ENGINE_KEY_TO_JA[algorithm] || algorithm;
    const wrapper = createNode("div", "stats-item");

    const header = createNode(
      "div",
      "stats-line",
      `${jaName} : 平均 ${Number(row?.avg_duration_ms ?? 0).toFixed(3)} ms / 記録 ${Number(row?.plays ?? 0)}回 / 勝率 ${(Number(row?.win_rate ?? 0) * 100).toFixed(1)}%`,
    );

    const rankCounts = row?.rank_counts ?? {};
    const rankLine = createNode(
      "div",
      "stats-ranks",
      [
        `1位 ${Number(rankCounts[1] ?? 0)}回`,
        `2位 ${Number(rankCounts[2] ?? 0)}回`,
        `3位 ${Number(rankCounts[3] ?? 0)}回`,
      ].join(" / "),
    );

    wrapper.appendChild(header);
    wrapper.appendChild(rankLine);
    fragment.appendChild(wrapper);
  });

  DOM.stats.appendChild(fragment);
}

async function loadSavedData() {
  const loggedIn = getSafeLoggedInState();

  if (!loggedIn) {
    clearStatistics("ログインすると統計を表示できます");
    clearHistory("ログインすると保存済み履歴を表示できます");
    return;
  }

  clearStatistics("読み込み中...");
  clearHistory("読み込み中...");

  try {
    const [historyResult, statsResult] = await Promise.all([
      typeof fetchBattleHistory === "function"
        ? fetchBattleHistory(CONFIG.HISTORY_LIMIT)
        : Promise.resolve({
            success: false,
            error: { message: "fetchBattleHistory が見つかりません" },
          }),
      typeof fetchStatistics === "function"
        ? fetchStatistics(CONFIG.HISTORY_LIMIT)
        : Promise.resolve({
            success: false,
            error: { message: "fetchStatistics が見つかりません" },
          }),
    ]);
    console.log("loggedIn =", getSafeLoggedInState());
    console.log("historyResult =", historyResult);
    console.log("statsResult =", statsResult);
    console.log("historyResult.data =", historyResult?.data);
    console.log("statsResult.data =", statsResult?.data);

    if (historyResult?.success) {
      renderBattleHistory(normalizeHistoryResponseData(historyResult.data));
    } else {
      clearHistory(historyResult?.error?.message || "履歴の取得に失敗しました");
    }

    if (statsResult?.success) {
      renderApiStatistics(normalizeStatisticsResponseData(statsResult.data));
    } else {
      clearStatistics(
        statsResult?.error?.message || "統計の取得に失敗しました",
      );
    }
  } catch (error) {
    clearHistory("履歴の取得に失敗しました");
    clearStatistics("統計の取得に失敗しました");
    console.error(error);
  }
}

async function handleSaveBattle() {
  if (typeof saveLatestBattle !== "function") {
    showSaveMessage("保存機能が読み込まれていません", "error");
    return;
  }

  if (!getSafeLoggedInState()) {
    showSaveMessage("ログイン中のみ保存できます", "error");
    renderAuthPanel();
    await loadSavedData();
    return;
  }

  showSaveMessage("");

  const result = await saveLatestBattle();

  if (!result?.success) {
    showSaveMessage(result?.error?.message || "保存に失敗しました", "error");
    renderAuthPanel();
    await loadSavedData();
    return;
  }

  showSaveMessage(
    `保存しました (battle_id=${result?.data?.battle_id ?? "-"})`,
    "success",
  );

  await loadSavedData();
}

/* ==============================
   Battle Engine
============================== */

class Battle {
  constructor() {
    this.results = [];
    this.running = false;
    this.runToken = 0;
  }

  async run() {
    if (this.running) return;

    if (!validatePrediction()) {
      alert("1位〜3位を予想してください（重複不可）");
      return;
    }

    this.running = true;
    BattleState.running = true;
    this.runToken += 1;
    const currentRunToken = this.runToken;

    setButtonBusy(true);
    renderAuthPanel();
    showSaveMessage("");
    clearLatestBattlePayloadSafe();

    try {
      clearCardDecorations();
      clearMessage();

      const values = makeValues(CONFIG.VIS_ARRAY_SIZE);
      createBoards(values);

      await this.fetchRankingFromServer();

      if (currentRunToken !== this.runToken) return;

      await Promise.all(
        Object.entries(ALGORITHMS).map(([name, algorithm]) =>
          this.visualize(name, algorithm, values.slice(), currentRunToken),
        ),
      );

      if (currentRunToken !== this.runToken) return;

      this.renderRanking();
      this.renderPrediction();
      this.prepareSavePayload();
      renderAuthPanel();
    } catch (error) {
      console.error(error);
      clearLatestBattlePayloadSafe();
      showError(error?.message || "バトル実行中にエラーが発生しました");
    } finally {
      if (currentRunToken === this.runToken) {
        this.running = false;
        BattleState.running = false;
        setButtonBusy(false);
        renderAuthPanel();
      }
    }
  }

  async fetchRankingFromServer() {
    const { ok, data, status, error } = await fetchJson("/api/run-battle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        benchmark_size: CONFIG.BENCHMARK_ARRAY_SIZE,
      }),
    });

    if (!ok || !data) {
      if (error?.name === "AbortError") {
        throw new Error("サーバー応答がタイムアウトしました");
      }
      throw new Error(`サーバー通信に失敗しました (status=${status})`);
    }

    if (!data.success) {
      throw new Error(data?.error?.message || "ランキング取得に失敗しました");
    }

    const rawRanking = Array.isArray(data?.data)
      ? data.data
      : data?.data?.ranking;

    this.results = normalizeRanking(rawRanking);
  }

  async visualize(name, algorithm, values, runToken) {
    const board = document.getElementById(`board-${name}`);
    if (!board) return;

    const bars = board.children;
    const steps = algorithm(values);

    if (!Array.isArray(steps)) return;

    for (const step of steps) {
      if (runToken !== this.runToken) return;
      if (!step || typeof step !== "object") continue;

      if (step.type === "swap") {
        const i = Number(step.i);
        const j = Number(step.j);

        if (!Number.isInteger(i) || !Number.isInteger(j)) continue;
        if (i < 0 || j < 0 || i >= values.length || j >= values.length)
          continue;

        [values[i], values[j]] = [values[j], values[i]];

        if (bars[i]) {
          bars[i].style.height = `${values[i] * CONFIG.HEIGHT_SCALE}px`;
        }
        if (bars[j]) {
          bars[j].style.height = `${values[j] * CONFIG.HEIGHT_SCALE}px`;
        }
      }

      if (step.type === "set") {
        const index = Number(step.index);
        const value = Number(step.value);

        if (!Number.isInteger(index)) continue;
        if (index < 0 || index >= values.length) continue;
        if (!Number.isFinite(value)) continue;

        values[index] = value;
        if (bars[index]) {
          bars[index].style.height = `${values[index] * CONFIG.HEIGHT_SCALE}px`;
        }
      }

      await sleep(CONFIG.VIS_DELAY);
    }
  }

  renderRanking() {
    this.results.forEach((result, index) => {
      const card = document.getElementById(`card-${result.algorithmJa}`);
      if (!card) return;

      if (index === 0) card.classList.add("rank-1");
      if (index === 1) card.classList.add("rank-2");
      if (index === 2) card.classList.add("rank-3");

      const label = createNode(
        "div",
        "time-label",
        `${index + 1}位 : ${result.duration_ms.toFixed(3)} ms`,
      );

      card.appendChild(label);
    });
  }

  renderPrediction() {
    const picks = getPredictionPicks();

    let correct = 0;
    for (let i = 0; i < 3; i += 1) {
      if (this.results[i]?.algorithmJa === picks[i]) {
        correct += 1;
      }
    }

    const top3 = this.results
      .slice(0, 3)
      .map((result) => result.algorithmJa)
      .join(" → ");

    showMessageLines(
      [`結果 : ${top3}`, `的中数 : ${correct}/3`],
      correct === 3 ? "success" : "normal",
    );

    if (correct === 3) {
      launchFireworks();
    }
  }

  prepareSavePayload() {
    if (typeof setLatestBattlePayload !== "function") return;

    setLatestBattlePayload({
      array_size: CONFIG.VIS_ARRAY_SIZE,
      benchmark_size: CONFIG.BENCHMARK_ARRAY_SIZE,
      results: this.results.map((result) => ({
        algorithm: result.algorithmKey,
        duration_ms: result.duration_ms,
        rank: result.rank,
      })),
    });
  }
}

/* ==============================
   Bootstrap
============================== */

window.addEventListener("DOMContentLoaded", async () => {
  if (!DOM.grid) return;

  initDragPrediction();
  resetPredictionSlots();
  createBoards(makeValues(CONFIG.VIS_ARRAY_SIZE));

  renderAuthPanel();
  bindAuthActions();
  await loadSavedData();

  DOM.recordsHeader?.addEventListener("click", async () => {
    DOM.recordsAccordion?.classList.toggle("active");

    if (DOM.recordsAccordion?.classList.contains("active")) {
      await loadSavedData();
    }
  });

  const battle = new Battle();

  DOM.generateBtn?.addEventListener("click", () => {
    if (battle.running) return;

    clearCardDecorations();
    clearMessage();
    showSaveMessage("");
    clearLatestBattlePayloadSafe();
    resetPredictionSlots();
    createBoards(makeValues(CONFIG.VIS_ARRAY_SIZE));
  });

  DOM.startBtn?.addEventListener("click", async () => {
    await battle.run();
  });

  window.addEventListener("focus", async () => {
    renderAuthPanel();
    await loadSavedData();
  });
});
