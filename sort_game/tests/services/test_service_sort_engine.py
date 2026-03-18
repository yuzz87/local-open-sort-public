import json
import subprocess
from unittest.mock import patch

import pytest

from app.services.sort_engine_service import run_sort


def test_run_sort_engine_subprocess_error():
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.is_file", return_value=True):
            with patch("app.services.sort_engine_service.os.access", return_value=True):
                with patch("app.services.sort_engine_service.subprocess.run") as mock_run:
                    mock_run.side_effect = subprocess.CalledProcessError(
                        returncode=1,
                        cmd=["cpp_engine/sort_engine", "quick", "2000"],
                        stderr="engine failed",
                    )

                    with pytest.raises(RuntimeError) as exc_info:
                        run_sort("quick", 2000)

                    assert "sort_engine execution failed" in str(exc_info.value)


def test_run_sort_engine_invalid_json():
    mock_completed = subprocess.CompletedProcess(
        args=["cpp_engine/sort_engine", "quick", "2000"],
        returncode=0,
        stdout="not-json",
        stderr="",
    )

    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.is_file", return_value=True):
            with patch("app.services.sort_engine_service.os.access", return_value=True):
                with patch(
                    "app.services.sort_engine_service.subprocess.run",
                    return_value=mock_completed,
                ):
                    with pytest.raises(RuntimeError) as exc_info:
                        run_sort("quick", 2000)

                    assert "Invalid JSON from sort_engine" in str(exc_info.value)


def test_run_sort_engine_empty_output():
    mock_completed = subprocess.CompletedProcess(
        args=["cpp_engine/sort_engine", "quick", "2000"],
        returncode=0,
        stdout="",
        stderr="",
    )

    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.is_file", return_value=True):
            with patch("app.services.sort_engine_service.os.access", return_value=True):
                with patch(
                    "app.services.sort_engine_service.subprocess.run",
                    return_value=mock_completed,
                ):
                    with pytest.raises(RuntimeError) as exc_info:
                        run_sort("quick", 2000)

                    assert "Invalid JSON from sort_engine" in str(exc_info.value)


def test_run_sort_engine_not_found():
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(RuntimeError) as exc_info:
            run_sort("quick", 2000)

        assert "sort_engine not found" in str(exc_info.value)


def test_run_sort_engine_unknown_algorithm():
    with pytest.raises(ValueError) as exc_info:
        run_sort("radix", 2000)

    assert "Unknown algorithm" in str(exc_info.value)


def test_run_sort_engine_success():
    mock_stdout = json.dumps(
        {
            "algorithm": "quick",
            "size": 2000,
            "duration_ms": 0.057803,
        }
    )

    mock_completed = subprocess.CompletedProcess(
        args=["cpp_engine/sort_engine", "quick", "2000"],
        returncode=0,
        stdout=mock_stdout,
        stderr="",
    )

    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.is_file", return_value=True):
            with patch("app.services.sort_engine_service.os.access", return_value=True):
                with patch(
                    "app.services.sort_engine_service.subprocess.run",
                    return_value=mock_completed,
                ):
                    result = run_sort("quick", 2000)

    assert isinstance(result, dict)
    assert result["algorithm"] == "quick"
    assert result["size"] == 2000
    assert result["duration_ms"] == 0.057803
    
    