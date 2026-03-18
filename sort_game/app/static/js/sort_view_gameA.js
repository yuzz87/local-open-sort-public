const CONFIG = Object.freeze({
  MAX_CARD_SIZE: 44,
  MIN_CARD_SIZE: 14,
  GAP: 8,
  SPEED_BASE: 100,
  DEFAULT_COUNT: 13,
  DEFAULT_BOARD_WIDTH: 1000,
  PAUSE_POLL_MS: 50,
  MIN_COUNT: 2,
  MAX_COUNT: 100,
  FINISH_OVERLAY_MS: 3000,
});

/* ==========================
   ユーティリティ
========================== */

function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function makeValues(n) {
  const values = Array.from({ length: n }, (_, i) => i + 1);

  for (let i = values.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [values[i], values[j]] = [values[j], values[i]];
  }

  return values;
}

/* ==========================
   Visualizer
========================== */

class Visualizer {
  constructor() {
    this.board = document.getElementById("board");

    this.startBtn = document.getElementById("start-btn");
    this.pauseBtn = document.getElementById("pause-btn");
    this.resetBtn = document.getElementById("reset-btn");

    this.algorithmInput = document.getElementById("algorithm-input");
    this.countInput = document.getElementById("count-input");
    this.speedInput = document.getElementById("speed-input");
    this.speedValue = document.getElementById("speed-value");

    this.values = [];
    this.cards = [];
    this.steps = [];

    this.running = false;
    this.paused = false;
    this.abort = false;
    this.runId = 0;
    this.finishOverlayTimer = null;

    this.init();
  }

  /* ==========================
     初期化
  ========================== */

  init() {
    this.reset();

    this.startBtn.addEventListener("click", () => {
      this.start();
    });

    this.pauseBtn.addEventListener("click", () => {
      this.togglePause();
    });

    this.resetBtn.addEventListener("click", () => {
      this.reset();
    });

    this.speedInput.addEventListener("input", () => {
      this.updateSpeedLabel();
    });

    this.countInput.addEventListener("change", () => {
      if (this.running) return;
      this.normalizeCountInput();
      this.reset();
    });

    this.algorithmInput.addEventListener("change", () => {
      if (this.running) return;
      this.reset();
    });

    window.addEventListener("resize", () => {
      if (this.running) return;
      this.resetLayoutOnly();
    });

    this.updateSpeedLabel();
    this.updatePauseButtonLabel();
    this.updateButtonStates();
  }

  normalizeCountInput() {
    const n = clamp(
      parseInt(this.countInput.value, 10) || CONFIG.DEFAULT_COUNT,
      CONFIG.MIN_COUNT,
      CONFIG.MAX_COUNT,
    );
    this.countInput.value = String(n);
    return n;
  }

  updateSpeedLabel() {
    const speed = Number(this.speedInput.value) || 1;
    this.speedValue.textContent = `${speed.toFixed(1)}x`;
  }

  updatePauseButtonLabel() {
    this.pauseBtn.textContent = this.paused ? "再開" : "一時停止";
  }

  updateButtonStates() {
    this.startBtn.disabled = this.running;
    this.pauseBtn.disabled = !this.running;
    this.resetBtn.disabled = false;
    this.algorithmInput.disabled = this.running;
    this.countInput.disabled = this.running;
  }

  clearFinishOverlay() {
    if (this.finishOverlayTimer) {
      clearTimeout(this.finishOverlayTimer);
      this.finishOverlayTimer = null;
    }

    this.board.querySelector(".finish-overlay")?.remove();
  }

  /* ==========================
     リセット
  ========================== */

  reset() {
    this.runId += 1;
    this.abort = true;
    this.running = false;
    this.paused = false;

    this.updatePauseButtonLabel();
    this.updateButtonStates();
    this.clearFinishOverlay();

    this.board.innerHTML = "";

    const n = this.normalizeCountInput();
    this.values = makeValues(n);

    const boardWidth = this.board.clientWidth || CONFIG.DEFAULT_BOARD_WIDTH;

    const cardSize = clamp(
      Math.floor((boardWidth - (n - 1) * CONFIG.GAP) / n),
      CONFIG.MIN_CARD_SIZE,
      CONFIG.MAX_CARD_SIZE,
    );

    this.board.style.setProperty("--card-size", `${cardSize}px`);
    this.board.style.setProperty(
      "--card-font-size",
      `${Math.max(10, Math.floor(cardSize / 2))}px`,
    );

    this.cards = this.values.map((value) => {
      const el = document.createElement("div");
      el.className = "card";
      el.textContent = String(value);
      this.board.appendChild(el);

      return {
        value,
        element: el,
        x: 0,
      };
    });

    this.layout();
  }

  resetLayoutOnly() {
    if (!this.cards.length) return;

    const n = this.cards.length;
    const boardWidth = this.board.clientWidth || CONFIG.DEFAULT_BOARD_WIDTH;

    const cardSize = clamp(
      Math.floor((boardWidth - (n - 1) * CONFIG.GAP) / n),
      CONFIG.MIN_CARD_SIZE,
      CONFIG.MAX_CARD_SIZE,
    );

    this.board.style.setProperty("--card-size", `${cardSize}px`);
    this.board.style.setProperty(
      "--card-font-size",
      `${Math.max(10, Math.floor(cardSize / 2))}px`,
    );

    this.layout();
  }

  /* ==========================
     配置
  ========================== */

  layout() {
    const size = parseInt(
      getComputedStyle(this.board).getPropertyValue("--card-size"),
      10,
    );

    this.cards.forEach((card, i) => {
      card.x = i * (size + CONFIG.GAP);
      card.element.style.transform = `translate(${card.x}px, 0px)`;
    });
  }

  /* ==========================
     Step生成
  ========================== */

  buildSteps() {
    const map = {
      bubble: bubbleSteps,
      selection: selectionSteps,
      insertion: insertionSteps,
      merge: mergeSteps,
      quick: quickSteps,
      heap: heapSteps,
    };

    const algo = map[this.algorithmInput.value];

    if (typeof algo !== "function") {
      throw new Error(`Unsupported algorithm: ${this.algorithmInput.value}`);
    }

    return algo(this.values.slice());
  }

  /* ==========================
     実行継続可否
  ========================== */

  isCancelled(currentRunId) {
    return this.abort || currentRunId !== this.runId;
  }

  /* ==========================
     Start
  ========================== */

  async start() {
    if (this.running) return;

    const currentRunId = ++this.runId;

    this.abort = false;
    this.running = true;
    this.paused = false;
    this.updatePauseButtonLabel();
    this.updateButtonStates();
    this.clearFinishOverlay();

    try {
      this.steps = this.buildSteps();
    } catch (error) {
      console.error(error);
      this.running = false;
      this.updateButtonStates();
      alert(
        "ステップ生成に失敗しました。入力値またはアルゴリズムを確認してください。",
      );
      return;
    }

    try {
      for (const step of this.steps) {
        if (this.isCancelled(currentRunId)) {
          this.running = false;
          this.updateButtonStates();
          return;
        }

        while (this.paused) {
          if (this.isCancelled(currentRunId)) {
            this.running = false;
            this.updateButtonStates();
            return;
          }
          await sleep(CONFIG.PAUSE_POLL_MS);
        }

        if (this.isCancelled(currentRunId)) {
          this.running = false;
          this.updateButtonStates();
          return;
        }

        this.clearStates();
        this.applyStep(step);

        const speedMultiplier = Math.max(
          0.1,
          Number(this.speedInput.value) || 1,
        );
        const delay = CONFIG.SPEED_BASE / speedMultiplier;
        await sleep(delay);

        if (this.isCancelled(currentRunId)) {
          this.running = false;
          this.updateButtonStates();
          return;
        }
      }

      if (this.isCancelled(currentRunId)) {
        this.running = false;
        this.updateButtonStates();
        return;
      }

      this.running = false;
      this.updateButtonStates();
      this.onFinish();
    } catch (error) {
      console.error(error);
      this.running = false;
      this.updateButtonStates();
      alert("アニメーション実行中にエラーが発生しました。");
    }
  }

  /* ==========================
     Step反映
  ========================== */

  applyStep(step) {
    if (!step || !step.type) return;

    if (step.type === "compare") {
      if (this.cards[step.i]) {
        this.cards[step.i].element.classList.add("compare");
      }
      if (this.cards[step.j]) {
        this.cards[step.j].element.classList.add("compare");
      }
      return;
    }

    if (step.type === "split") {
      if (!Array.isArray(step.range) || step.range.length < 2) return;

      const [l, r] = step.range;

      for (let i = l; i <= r; i++) {
        if (this.cards[i]) {
          this.cards[i].element.classList.add("split");
        }
      }
      return;
    }

    if (step.type === "swap") {
      if (!this.cards[step.i] || !this.cards[step.j]) return;
      if (step.i === step.j) return;

      const tmp = this.cards[step.i];
      this.cards[step.i] = this.cards[step.j];
      this.cards[step.j] = tmp;

      this.cards[step.i].element.classList.add("move");
      this.cards[step.j].element.classList.add("move");

      this.layout();
      return;
    }

    if (step.type === "set") {
      if (!this.cards[step.index]) return;

      this.cards[step.index].value = step.value;
      this.cards[step.index].element.textContent = String(step.value);
      this.cards[step.index].element.classList.add("move");
      return;
    }

    if (step.type === "finalize") {
      if (!this.cards[step.index]) return;
      this.cards[step.index].element.classList.add("finalize");
    }
  }

  /* ==========================
     Pause
  ========================== */

  togglePause() {
    if (!this.running) return;

    this.paused = !this.paused;
    this.updatePauseButtonLabel();
  }

  /* ==========================
     classクリア
  ========================== */

  clearStates() {
    this.cards.forEach((card) => {
      card.element.classList.remove("compare");
      card.element.classList.remove("split");
      card.element.classList.remove("move");
    });
  }

  /* ==========================
     完了表示
  ========================== */

  onFinish() {
    this.clearStates();

    this.cards.forEach((card) => {
      card.element.classList.add("finalize");
    });

    this.clearFinishOverlay();

    const overlay = document.createElement("div");
    overlay.className = "finish-overlay";
    overlay.textContent = "ソート完了";

    this.board.appendChild(overlay);

    this.finishOverlayTimer = setTimeout(() => {
      overlay.remove();
      this.finishOverlayTimer = null;
    }, CONFIG.FINISH_OVERLAY_MS);
  }
}

/* ==========================
   起動
========================== */

window.addEventListener("DOMContentLoaded", () => {
  if (!document.getElementById("board")) return;
  new Visualizer();
});
