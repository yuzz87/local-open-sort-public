import math


ALLOWED_ALGORITHMS = {
    "bubble",
    "selection",
    "insertion",
    "merge",
    "quick",
    "heap",
}


def validate_json_object(payload):
    if not isinstance(payload, dict):
        return False, "INVALID_INPUT", "payload must be an object"
    return True, None, None


def validate_allowed_fields(payload: dict, allowed_fields: set[str]):
    extra_fields = set(payload.keys()) - allowed_fields
    if extra_fields:
        return False, "INVALID_INPUT", f"unexpected fields: {', '.join(sorted(extra_fields))}"
    return True, None, None


def validate_run_battle_payload(payload: dict):
    ok, code, message = validate_json_object(payload)
    if not ok:
        return ok, code, message

    ok, code, message = validate_allowed_fields(payload, {"benchmark_size"})
    if not ok:
        return ok, code, message

    if "benchmark_size" not in payload:
        return False, "INVALID_BENCHMARK_SIZE", "benchmark_size is required"

    benchmark_size = payload.get("benchmark_size")

    if type(benchmark_size) is not int:
        return False, "INVALID_BENCHMARK_SIZE", "benchmark_size must be int"

    if not (100 <= benchmark_size <= 10000):
        return False, "INVALID_BENCHMARK_SIZE", "benchmark_size must be between 100 and 10000"

    return True, None, None


def validate_battle_payload(payload: dict):
    ok, code, message = validate_json_object(payload)
    if not ok:
        return ok, code, message

    ok, code, message = validate_allowed_fields(
        payload,
        {"array_size", "benchmark_size", "results"},
    )
    if not ok:
        return ok, code, message

    array_size = payload.get("array_size")
    benchmark_size = payload.get("benchmark_size")
    results = payload.get("results")

    if "array_size" not in payload:
        return False, "INVALID_ARRAY_SIZE", "array_size is required"
    if type(array_size) is not int:
        return False, "INVALID_ARRAY_SIZE", "array_size must be int"
    if not (5 <= array_size <= 100):
        return False, "INVALID_ARRAY_SIZE", "array_size must be between 5 and 100"

    if "benchmark_size" not in payload:
        return False, "INVALID_BENCHMARK_SIZE", "benchmark_size is required"
    if type(benchmark_size) is not int:
        return False, "INVALID_BENCHMARK_SIZE", "benchmark_size must be int"
    if not (100 <= benchmark_size <= 10000):
        return False, "INVALID_BENCHMARK_SIZE", "benchmark_size must be between 100 and 10000"

    if "results" not in payload:
        return False, "INVALID_RESULTS", "results is required"
    if not isinstance(results, list):
        return False, "INVALID_RESULTS", "results must be an array"

    expected_count = len(ALLOWED_ALGORITHMS)
    if len(results) != expected_count:
        return False, "INVALID_RESULTS", f"results must contain exactly {expected_count} items"

    ranks = []
    algorithms = []

    for i, row in enumerate(results):
        if not isinstance(row, dict):
            return False, "INVALID_RESULTS", f"results[{i}] must be object"

        ok, code, message = validate_allowed_fields(row, {"algorithm", "duration_ms", "rank"})
        if not ok:
            return ok, code, message

        algorithm = row.get("algorithm")
        duration_ms = row.get("duration_ms")
        rank = row.get("rank")

        if not isinstance(algorithm, str):
            return False, "INVALID_ALGORITHM", f"results[{i}].algorithm must be string"

        if algorithm not in ALLOWED_ALGORITHMS:
            return False, "INVALID_ALGORITHM", f"results[{i}].algorithm is invalid"

        if not isinstance(duration_ms, (int, float)) or isinstance(duration_ms, bool):
            return False, "INVALID_DURATION", f"results[{i}].duration_ms must be number"

        if not math.isfinite(duration_ms) or duration_ms < 0:
            return False, "INVALID_DURATION", f"results[{i}].duration_ms must be finite and >= 0"

        if duration_ms > 3600000:
            return False, "INVALID_DURATION", f"results[{i}].duration_ms is too large"

        if type(rank) is not int:
            return False, "INVALID_RANK", f"results[{i}].rank must be int"

        if not (1 <= rank <= expected_count):
            return False, "INVALID_RANK", f"results[{i}].rank must be between 1 and {expected_count}"

        algorithms.append(algorithm)
        ranks.append(rank)

    if len(algorithms) != len(set(algorithms)):
        return False, "DUPLICATE_ALGORITHM", "algorithm must be unique"

    if set(algorithms) != ALLOWED_ALGORITHMS:
        return False, "INVALID_RESULTS", "results must contain all allowed algorithms exactly once"

    if len(ranks) != len(set(ranks)):
        return False, "DUPLICATE_RANK", "rank must be unique"

    if set(ranks) != set(range(1, expected_count + 1)):
        return False, "INVALID_RANK", "rank must be sequential from 1"

    return True, None, None


def validate_limit(value, *, max_value: int):
    if value is None:
        return True, None, None, None

    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return False, "INVALID_LIMIT", "limit must be int", None

    if not (1 <= parsed <= max_value):
        return False, "INVALID_LIMIT", f"limit must be between 1 and {max_value}", None

    return True, None, None, parsed