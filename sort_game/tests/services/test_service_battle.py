import math
from unittest.mock import patch

import pytest

from app.services.battle_service import (
    run_battle,
    save_battle_result,
    list_battles,
    get_statistics,
)


# =====================================
# run_battle
# =====================================

def test_run_battle_invalid_benchmark_size_type(app_ctx):
    with pytest.raises(ValueError) as exc_info:
        run_battle("100")  # type: ignore[arg-type]

    assert str(exc_info.value) == "benchmark_size must be int"


def test_run_battle_benchmark_size_out_of_range_low(app_ctx):
    with pytest.raises(ValueError) as exc_info:
        run_battle(99)

    assert "benchmark_size must be between" in str(exc_info.value)


def test_run_battle_benchmark_size_out_of_range_high(app_ctx):
    with pytest.raises(ValueError) as exc_info:
        run_battle(10001)

    assert "benchmark_size must be between" in str(exc_info.value)


def test_run_battle_invalid_result_type(app_ctx):
    with patch("app.services.battle_service.run_sort", return_value="invalid"):
        with pytest.raises(ValueError) as exc_info:
            run_battle(2000)

    assert "run_sort returned invalid result" in str(exc_info.value)


def test_run_battle_unexpected_algorithm(app_ctx):
    with patch("app.services.battle_service.run_sort") as mock_run:
        mock_run.return_value = {
            "algorithm": "wrong",
            "duration_ms": 0.1,
        }

        with pytest.raises(ValueError) as exc_info:
            run_battle(2000)

    assert "run_sort returned unexpected algorithm" in str(exc_info.value)


def test_run_battle_invalid_duration_type(app_ctx):
    with patch("app.services.battle_service.run_sort") as mock_run:
        mock_run.return_value = {
            "algorithm": "bubble",
            "duration_ms": "not-number",
        }

        with pytest.raises(ValueError) as exc_info:
            run_battle(2000)

    assert "invalid duration_ms returned" in str(exc_info.value)


def test_run_battle_invalid_duration_nan(app_ctx):
    with patch("app.services.battle_service.run_sort") as mock_run:
        mock_run.return_value = {
            "algorithm": "bubble",
            "duration_ms": math.nan,
        }

        with pytest.raises(ValueError) as exc_info:
            run_battle(2000)

    assert "duration_ms must be finite and >= 0" in str(exc_info.value)


def test_run_battle_invalid_duration_negative(app_ctx):
    with patch("app.services.battle_service.run_sort") as mock_run:
        mock_run.return_value = {
            "algorithm": "bubble",
            "duration_ms": -1,
        }

        with pytest.raises(ValueError) as exc_info:
            run_battle(2000)

    assert "duration_ms must be finite and >= 0" in str(exc_info.value)


# =====================================
# save_battle_result
# =====================================

def test_save_battle_result_invalid_user_id_zero(app_ctx, valid_results):
    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=0,
            array_size=40,
            benchmark_size=2000,
            results=valid_results,
        )

    assert str(exc_info.value) == "user_id must be positive int"


def test_save_battle_result_invalid_user_id_type(app_ctx, valid_results):
    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id="1",  # type: ignore[arg-type]
            array_size=40,
            benchmark_size=2000,
            results=valid_results,
        )

    assert str(exc_info.value) == "user_id must be positive int"


def test_save_battle_result_invalid_array_size_type(app_ctx, valid_results):
    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=1,
            array_size="40",  # type: ignore[arg-type]
            benchmark_size=2000,
            results=valid_results,
        )

    assert str(exc_info.value) == "array_size must be int"


def test_save_battle_result_array_size_out_of_range_low(app_ctx, valid_results):
    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=1,
            array_size=4,
            benchmark_size=2000,
            results=valid_results,
        )

    assert "array_size must be between" in str(exc_info.value)


def test_save_battle_result_array_size_out_of_range_high(app_ctx, valid_results):
    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=1,
            array_size=101,
            benchmark_size=2000,
            results=valid_results,
        )

    assert "array_size must be between" in str(exc_info.value)


def test_save_battle_result_invalid_benchmark_size_type(app_ctx, valid_results):
    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=1,
            array_size=40,
            benchmark_size="2000",  # type: ignore[arg-type]
            results=valid_results,
        )

    assert str(exc_info.value) == "benchmark_size must be int"


def test_save_battle_result_benchmark_size_out_of_range_low(app_ctx, valid_results):
    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=1,
            array_size=40,
            benchmark_size=99,
            results=valid_results,
        )

    assert "benchmark_size must be between" in str(exc_info.value)


def test_save_battle_result_benchmark_size_out_of_range_high(app_ctx, valid_results):
    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=1,
            array_size=40,
            benchmark_size=10001,
            results=valid_results,
        )

    assert "benchmark_size must be between" in str(exc_info.value)


def test_save_battle_result_results_not_array(app_ctx):
    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=1,
            array_size=40,
            benchmark_size=2000,
            results="invalid",  # type: ignore[arg-type]
        )

    assert str(exc_info.value) == "results must be array"


def test_save_battle_result_results_invalid_count(app_ctx, valid_results):
    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=1,
            array_size=40,
            benchmark_size=2000,
            results=valid_results[:5],
        )

    assert str(exc_info.value) == "results must contain exactly 6 items"


def test_save_battle_result_row_not_object(app_ctx):
    invalid_results = [
        "invalid",
        {"algorithm": "merge", "duration_ms": 0.2, "rank": 2},
        {"algorithm": "heap", "duration_ms": 0.3, "rank": 3},
        {"algorithm": "insertion", "duration_ms": 0.4, "rank": 4},
        {"algorithm": "selection", "duration_ms": 0.5, "rank": 5},
        {"algorithm": "bubble", "duration_ms": 0.6, "rank": 6},
    ]

    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=1,
            array_size=40,
            benchmark_size=2000,
            results=invalid_results,  # type: ignore[arg-type]
        )

    assert str(exc_info.value) == "results[0] must be object"


def test_save_battle_result_invalid_duration_number(app_ctx, valid_results):
    invalid_results = [dict(row) for row in valid_results]
    invalid_results[0]["duration_ms"] = "abc"

    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=1,
            array_size=40,
            benchmark_size=2000,
            results=invalid_results,
        )

    assert str(exc_info.value) == "results[0].duration_ms must be number"


def test_save_battle_result_invalid_duration_nan(app_ctx, valid_results):
    invalid_results = [dict(row) for row in valid_results]
    invalid_results[0]["duration_ms"] = math.nan

    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=1,
            array_size=40,
            benchmark_size=2000,
            results=invalid_results,
        )

    assert str(exc_info.value) == "results[0].duration_ms must be finite and >= 0"


def test_save_battle_result_invalid_rank_type(app_ctx, valid_results):
    invalid_results = [dict(row) for row in valid_results]
    invalid_results[0]["rank"] = "1"

    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=1,
            array_size=40,
            benchmark_size=2000,
            results=invalid_results,
        )

    assert str(exc_info.value) == "results[0].rank must be int"


def test_save_battle_result_invalid_rank_range(app_ctx, valid_results):
    invalid_results = [dict(row) for row in valid_results]
    invalid_results[5]["rank"] = 7

    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=1,
            array_size=40,
            benchmark_size=2000,
            results=invalid_results,
        )

    assert str(exc_info.value) == "results[5].rank must be between 1 and 6"


def test_save_battle_result_duplicate_rank(app_ctx, valid_results):
    invalid_results = [dict(row) for row in valid_results]
    invalid_results[1]["rank"] = 1

    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=1,
            array_size=40,
            benchmark_size=2000,
            results=invalid_results,
        )

    assert str(exc_info.value) == "duplicate rank: 1"


def test_save_battle_result_duplicate_algorithm(app_ctx, valid_results):
    invalid_results = [dict(row) for row in valid_results]
    invalid_results[1]["algorithm"] = "quick"

    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=1,
            array_size=40,
            benchmark_size=2000,
            results=invalid_results,
        )

    assert str(exc_info.value) == "duplicate algorithm: quick"


def test_save_battle_result_invalid_algorithm(app_ctx, valid_results):
    invalid_results = [dict(row) for row in valid_results]
    invalid_results[0]["algorithm"] = "radix"

    with pytest.raises(ValueError) as exc_info:
        save_battle_result(
            user_id=1,
            array_size=40,
            benchmark_size=2000,
            results=invalid_results,
        )

    assert str(exc_info.value) == "results[0].algorithm is invalid: radix"


def test_save_battle_result_non_sequential_rank(app_ctx, valid_results):
    invalid_results = [dict(row) for row in valid_results]
    invalid_results[0]["rank"] = 6
    invalid_results[5]["rank"] = 1

    with patch("app.services.battle_service.save_battle") as mock_save:
        mock_save.return_value = 1

        result = save_battle_result(
            user_id=1,
            array_size=40,
            benchmark_size=2000,
            results=invalid_results,
        )

    assert result == 1


# =====================================
# list_battles
# =====================================

def test_list_battles_invalid_user_id_type(app_ctx):
    with pytest.raises(ValueError) as exc_info:
        list_battles("1", 10)  # type: ignore[arg-type]

    assert str(exc_info.value) == "user_id must be positive int"


def test_list_battles_invalid_user_id_zero(app_ctx):
    with pytest.raises(ValueError) as exc_info:
        list_battles(0, 10)

    assert str(exc_info.value) == "user_id must be positive int"


def test_list_battles_invalid_limit_type(app_ctx):
    with pytest.raises(ValueError) as exc_info:
        list_battles(1, "10")  # type: ignore[arg-type]

    assert str(exc_info.value) == "limit must be int"


def test_list_battles_invalid_limit_low(app_ctx):
    with pytest.raises(ValueError) as exc_info:
        list_battles(1, 0)

    assert "limit must be between" in str(exc_info.value)


def test_list_battles_invalid_limit_high(app_ctx):
    with pytest.raises(ValueError) as exc_info:
        list_battles(1, 51)

    assert "limit must be between" in str(exc_info.value)


# =====================================
# get_statistics
# =====================================

def test_get_statistics_invalid_user_id_type(app_ctx):
    with pytest.raises(ValueError) as exc_info:
        get_statistics("1", 10)  # type: ignore[arg-type]

    assert str(exc_info.value) == "user_id must be positive int"


def test_get_statistics_invalid_user_id_zero(app_ctx):
    with pytest.raises(ValueError) as exc_info:
        get_statistics(0, 10)

    assert str(exc_info.value) == "user_id must be positive int"


def test_get_statistics_invalid_limit_type(app_ctx):
    with pytest.raises(ValueError) as exc_info:
        get_statistics(1, "10")  # type: ignore[arg-type]

    assert str(exc_info.value) == "limit must be int"


def test_get_statistics_invalid_limit_low(app_ctx):
    with pytest.raises(ValueError) as exc_info:
        get_statistics(1, 0)

    assert "limit must be between" in str(exc_info.value)


def test_get_statistics_invalid_limit_high(app_ctx):
    with pytest.raises(ValueError) as exc_info:
        get_statistics(1, 1001)

    assert "limit must be between" in str(exc_info.value)