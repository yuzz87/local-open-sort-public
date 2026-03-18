import json
import os
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_ENGINE_PATH = BASE_DIR / "cpp_engine" / "sort_engine"

ENGINE_PATH = Path(os.getenv("ENGINE_PATH", str(DEFAULT_ENGINE_PATH))).resolve()


ALGORITHMS = {
    "bubble",
    "selection",
    "insertion",
    "merge",
    "quick",
    "heap",
}


def run_sort(algorithm: str, size: int, seed: int | None = None):
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    if type(size) is not int or size <= 0:
        raise ValueError("size must be positive int")

    if not ENGINE_PATH.exists():
        raise RuntimeError(f"sort_engine not found: {ENGINE_PATH}")

    if not ENGINE_PATH.is_file():
        raise RuntimeError(f"sort_engine is not a file: {ENGINE_PATH}")

    if not os.access(ENGINE_PATH, os.X_OK):
        raise RuntimeError(f"sort_engine is not executable: {ENGINE_PATH}")

    cmd = [str(ENGINE_PATH), algorithm, str(size)]

    if seed is not None:
        cmd.append(str(seed))

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=str(BASE_DIR),
        )
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        stdout = (e.stdout or "").strip()
        raise RuntimeError(
            f"sort_engine execution failed: stderr={stderr} stdout={stdout}"
        ) from e
    except Exception as e:
        raise RuntimeError(f"sort_engine unexpected error: {e}") from e

    stdout = (result.stdout or "").strip()

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from sort_engine: {stdout}") from e

    returned_algorithm = data.get("algorithm")
    returned_size = data.get("size")
    returned_duration_ms = data.get("duration_ms")

    if returned_algorithm not in ALGORITHMS:
        raise RuntimeError(f"Invalid algorithm in engine response: {returned_algorithm}")

    try:
        returned_size = int(returned_size)
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Invalid size from sort_engine: {returned_size}") from e

    try:
        returned_duration_ms = float(returned_duration_ms)
    except (TypeError, ValueError) as e:
        raise RuntimeError(
            f"Invalid duration_ms from sort_engine: {returned_duration_ms}"
        ) from e

    return {
        "algorithm": returned_algorithm,
        "size": returned_size,
        "duration_ms": returned_duration_ms,
    }
    # python -m pytest --maxfail=1 --disable-warnings --cov=app --cov-report=term-missing --cov-report=xml