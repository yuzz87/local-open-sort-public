/* ======================================
   ソートアルゴリズム Step生成
====================================== */

const STEP = Object.freeze({
  COMPARE: "compare",
  SWAP: "swap",
  SET: "set",
  SPLIT: "split",
  FINALIZE: "finalize",
});

const MAX_VISUALIZE_SIZE = 100;

function validateValues(values) {
  if (!Array.isArray(values)) {
    throw new Error("values must be an array");
  }

  if (values.length < 1 || values.length > MAX_VISUALIZE_SIZE) {
    throw new Error(
      `values length must be between 1 and ${MAX_VISUALIZE_SIZE}`,
    );
  }

  for (const value of values) {
    if (typeof value !== "number" || !Number.isFinite(value)) {
      throw new Error("values must contain only finite numbers");
    }
  }
}

function createWorkingState(values) {
  validateValues(values);
  return {
    a: values.slice(),
    steps: [],
  };
}

/* ==============================
   Bubble Sort
============================== */

function bubbleSteps(values) {
  const { a, steps } = createWorkingState(values);
  const n = a.length;

  for (let i = 0; i < n; i++) {
    steps.push({ type: STEP.SPLIT, range: [0, n - i - 1] });

    for (let j = 0; j < n - i - 1; j++) {
      steps.push({ type: STEP.COMPARE, i: j, j: j + 1 });

      if (a[j] > a[j + 1]) {
        [a[j], a[j + 1]] = [a[j + 1], a[j]];
        steps.push({ type: STEP.SWAP, i: j, j: j + 1 });
      }
    }

    steps.push({ type: STEP.FINALIZE, index: n - i - 1 });
  }

  return steps;
}

/* ==============================
   Selection Sort
============================== */

function selectionSteps(values) {
  const { a, steps } = createWorkingState(values);
  const n = a.length;

  for (let i = 0; i < n; i++) {
    let min = i;

    steps.push({ type: STEP.SPLIT, range: [i, n - 1] });

    for (let j = i + 1; j < n; j++) {
      steps.push({ type: STEP.COMPARE, i: min, j });

      if (a[j] < a[min]) {
        min = j;
      }
    }

    if (min !== i) {
      [a[i], a[min]] = [a[min], a[i]];
      steps.push({ type: STEP.SWAP, i, j: min });
    }

    steps.push({ type: STEP.FINALIZE, index: i });
  }

  return steps;
}

/* ==============================
   Insertion Sort
============================== */

function insertionSteps(values) {
  const { a, steps } = createWorkingState(values);

  if (a.length > 0) {
    steps.push({ type: STEP.FINALIZE, index: 0 });
  }

  for (let i = 1; i < a.length; i++) {
    let j = i;

    steps.push({ type: STEP.SPLIT, range: [0, i] });

    while (j > 0) {
      steps.push({ type: STEP.COMPARE, i: j - 1, j });

      if (a[j - 1] <= a[j]) {
        break;
      }

      [a[j - 1], a[j]] = [a[j], a[j - 1]];
      steps.push({ type: STEP.SWAP, i: j - 1, j });

      j--;
    }

    steps.push({ type: STEP.FINALIZE, index: i });
  }

  return steps;
}

/* ==============================
   Merge Sort
============================== */

function mergeSteps(values) {
  const { a, steps } = createWorkingState(values);

  function sort(l, r) {
    if (l >= r) return;

    const m = Math.floor((l + r) / 2);

    steps.push({ type: STEP.SPLIT, range: [l, r] });

    sort(l, m);
    sort(m + 1, r);

    let i = l;
    let j = m + 1;
    const temp = [];

    while (i <= m && j <= r) {
      steps.push({ type: STEP.COMPARE, i, j });

      if (a[i] <= a[j]) {
        temp.push(a[i++]);
      } else {
        temp.push(a[j++]);
      }
    }

    while (i <= m) {
      temp.push(a[i++]);
    }

    while (j <= r) {
      temp.push(a[j++]);
    }

    for (let k = 0; k < temp.length; k++) {
      a[l + k] = temp[k];
      steps.push({
        type: STEP.SET,
        index: l + k,
        value: temp[k],
      });
    }
  }

  sort(0, a.length - 1);

  for (let i = 0; i < a.length; i++) {
    steps.push({ type: STEP.FINALIZE, index: i });
  }

  return steps;
}

/* ==============================
   Quick Sort
============================== */

function quickSteps(values) {
  const { a, steps } = createWorkingState(values);

  function sort(l, r) {
    if (l >= r) return;

    steps.push({ type: STEP.SPLIT, range: [l, r] });

    const pivot = a[r];
    let i = l;

    for (let j = l; j < r; j++) {
      steps.push({ type: STEP.COMPARE, i: j, j: r });

      if (a[j] < pivot) {
        if (i !== j) {
          [a[i], a[j]] = [a[j], a[i]];
          steps.push({ type: STEP.SWAP, i, j });
        }
        i++;
      }
    }

    if (i !== r) {
      [a[i], a[r]] = [a[r], a[i]];
      steps.push({ type: STEP.SWAP, i, j: r });
    }

    steps.push({ type: STEP.FINALIZE, index: i });

    sort(l, i - 1);
    sort(i + 1, r);
  }

  sort(0, a.length - 1);

  return steps;
}

/* ==============================
   Heap Sort
============================== */

function heapSteps(values) {
  const { a, steps } = createWorkingState(values);
  const n = a.length;

  function heapify(size, root) {
    let largest = root;
    const left = 2 * root + 1;
    const right = 2 * root + 2;

    if (left < size) {
      steps.push({ type: STEP.COMPARE, i: largest, j: left });
      if (a[left] > a[largest]) {
        largest = left;
      }
    }

    if (right < size) {
      steps.push({ type: STEP.COMPARE, i: largest, j: right });
      if (a[right] > a[largest]) {
        largest = right;
      }
    }

    if (largest !== root) {
      [a[root], a[largest]] = [a[largest], a[root]];
      steps.push({ type: STEP.SWAP, i: root, j: largest });
      heapify(size, largest);
    }
  }

  steps.push({ type: STEP.SPLIT, range: [0, n - 1] });

  for (let i = Math.floor(n / 2) - 1; i >= 0; i--) {
    heapify(n, i);
  }

  for (let i = n - 1; i > 0; i--) {
    [a[0], a[i]] = [a[i], a[0]];
    steps.push({ type: STEP.SWAP, i: 0, j: i });
    steps.push({ type: STEP.FINALIZE, index: i });
    heapify(i, 0);
  }

  steps.push({ type: STEP.FINALIZE, index: 0 });

  return steps;
}
