from __future__ import annotations

import math
from typing import Any, Dict, List

from flask import current_app

from .sort_engine_service import run_sort
from ..repositories.battle_repository import (
    save_battle,
    fetch_recent_battles,
    fetch_statistics,
)

ALGORITHMS = (
    "bubble",
    "selection",
    "insertion",
    "merge",
    "quick",
    "heap",
)


# =====================================
# C++ソートランキング実行
# =====================================
def run_battle(benchmark_size: int) -> List[Dict[str, Any]]:
    if type(benchmark_size) is not int:
        raise ValueError("benchmark_size must be int")

    min_size = current_app.config["RUN_BATTLE_ARRAY_SIZE_MIN"]
    max_size = current_app.config["RUN_BATTLE_ARRAY_SIZE_MAX"]

    if not (min_size <= benchmark_size <= max_size):
        raise ValueError(f"benchmark_size must be between {min_size} and {max_size}")

    results: List[Dict[str, Any]] = []

    for algo in ALGORITHMS:
        raw = run_sort(algo, benchmark_size)

        if not isinstance(raw, dict):
            raise ValueError(f"run_sort returned invalid result for {algo}")

        algorithm = raw.get("algorithm")
        duration_ms = raw.get("duration_ms")

        if algorithm != algo:
            raise ValueError(f"run_sort returned unexpected algorithm: {algorithm}")

        try:
            duration_ms = float(duration_ms)
        except (TypeError, ValueError):
            raise ValueError(f"invalid duration_ms returned for {algo}")

        if not math.isfinite(duration_ms) or duration_ms < 0:
            raise ValueError(f"duration_ms must be finite and >= 0 for {algo}")

        results.append({
            "algorithm": algorithm,
            "duration_ms": duration_ms,
        })

    results.sort(key=lambda x: x["duration_ms"])

    for i, row in enumerate(results, start=1):
        row["rank"] = i

    return results


# =====================================
# バトル保存
# User 専用
# =====================================
def save_battle_result(
    user_id: int,
    array_size: int,
    benchmark_size: int,
    results: List[Dict[str, Any]],
):
    if type(user_id) is not int or user_id <= 0:
        raise ValueError("user_id must be positive int")

    if type(array_size) is not int:
        raise ValueError("array_size must be int")

    array_min = current_app.config["SAVE_BATTLE_ARRAY_SIZE_MIN"]
    array_max = current_app.config["SAVE_BATTLE_ARRAY_SIZE_MAX"]

    if not (array_min <= array_size <= array_max):
        raise ValueError(f"array_size must be between {array_min} and {array_max}")

    if type(benchmark_size) is not int:
        raise ValueError("benchmark_size must be int")

    benchmark_min = current_app.config["SAVE_BATTLE_BENCHMARK_SIZE_MIN"]
    benchmark_max = current_app.config["SAVE_BATTLE_BENCHMARK_SIZE_MAX"]

    if not (benchmark_min <= benchmark_size <= benchmark_max):
        raise ValueError(
            f"benchmark_size must be between {benchmark_min} and {benchmark_max}"
        )

    if not isinstance(results, list):
        raise ValueError("results must be array")

    if len(results) != len(ALGORITHMS):
        raise ValueError(f"results must contain exactly {len(ALGORITHMS)} items")

    normalized_results: List[Dict[str, Any]] = []
    seen_algorithms = set()
    seen_ranks = set()

    for i, row in enumerate(results):
        if not isinstance(row, dict):
            raise ValueError(f"results[{i}] must be object")

        algorithm = row.get("algorithm")
        duration_ms = row.get("duration_ms")
        rank = row.get("rank")

        if algorithm not in ALGORITHMS:
            raise ValueError(f"results[{i}].algorithm is invalid: {algorithm}")

        try:
            duration_ms = float(duration_ms)
        except (TypeError, ValueError):
            raise ValueError(f"results[{i}].duration_ms must be number")

        if not math.isfinite(duration_ms) or duration_ms < 0:
            raise ValueError(f"results[{i}].duration_ms must be finite and >= 0")

        if type(rank) is not int:
            raise ValueError(f"results[{i}].rank must be int")

        if not (1 <= rank <= len(ALGORITHMS)):
            raise ValueError(
                f"results[{i}].rank must be between 1 and {len(ALGORITHMS)}"
            )

        if algorithm in seen_algorithms:
            raise ValueError(f"duplicate algorithm: {algorithm}")
        seen_algorithms.add(algorithm)

        if rank in seen_ranks:
            raise ValueError(f"duplicate rank: {rank}")
        seen_ranks.add(rank)

        normalized_results.append({
            "algorithm": algorithm,
            "duration_ms": duration_ms,
            "rank": rank,
        })

    if seen_ranks != set(range(1, len(ALGORITHMS) + 1)):
        raise ValueError(f"rank must be sequential from 1 to {len(ALGORITHMS)}")

    normalized_results.sort(key=lambda x: x["rank"])

    return save_battle(
        user_id=user_id,
        array_size=array_size,
        benchmark_size=benchmark_size,
        results=normalized_results,
    )


# =====================================
# バトル履歴取得
# User 専用
# =====================================
def list_battles(user_id: int, limit: int = 10):
    if type(user_id) is not int or user_id <= 0:
        raise ValueError("user_id must be positive int")

    if type(limit) is not int:
        raise ValueError("limit must be int")

    limit_min = current_app.config["BATTLES_LIMIT_MIN"]
    limit_max = current_app.config["BATTLES_LIMIT_MAX"]

    if not (limit_min <= limit <= limit_max):
        raise ValueError(f"limit must be between {limit_min} and {limit_max}")

    return fetch_recent_battles(user_id=user_id, limit=limit)


def get_battle_history(user_id: int, limit: int = 10):
    return list_battles(user_id=user_id, limit=limit)


# =====================================
# 統計取得
# User 専用
# =====================================
def get_statistics(user_id: int, limit: int = 10):
    if type(user_id) is not int or user_id <= 0:
        raise ValueError("user_id must be positive int")

    if type(limit) is not int:
        raise ValueError("limit must be int")

    limit_min = current_app.config["STATISTICS_LIMIT_MIN"]
    limit_max = current_app.config["STATISTICS_LIMIT_MAX"]

    if not (limit_min <= limit <= limit_max):
        raise ValueError(f"limit must be between {limit_min} and {limit_max}")

    rows = fetch_statistics(user_id=user_id, limit=limit)

    stats: Dict[str, Dict[str, Any]] = {}

    for row in rows:
        algorithm = row.get("algorithm")
        if algorithm not in ALGORITHMS:
            continue

        plays = int(row.get("plays") or 0)
        wins = int(row.get("wins") or 0)
        avg = float(row.get("avg_duration_ms") or 0.0)

        rank_1 = int(row.get("rank_1") or 0)
        rank_2 = int(row.get("rank_2") or 0)
        rank_3 = int(row.get("rank_3") or 0)

        win_rate = (wins / plays) if plays > 0 else 0.0

        stats[algorithm] = {
            "avg_duration_ms": avg,
            "win_rate": win_rate,
            "wins": wins,
            "plays": plays,
            "rank_1": rank_1,
            "rank_2": rank_2,
            "rank_3": rank_3,
        }

    return stats