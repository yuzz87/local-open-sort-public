from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request

from app.middleware.auth_middleware import login_required
from app.services.battle_service import (
    get_battle_history,
    get_statistics,
    run_battle,
    save_battle_result,
)
from app.validators.battle_validator import (
    validate_battle_payload,
    validate_limit,
    validate_run_battle_payload,
)

api_bp = Blueprint("api", __name__)


def success_response(data, status_code=200):
    return jsonify({
        "success": True,
        "data": data,
        "error": None,
    }), status_code


def error_response(code, message, status_code=400):
    return jsonify({
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
        },
    }), status_code


def get_json_object():
    if not request.is_json:
        return None, error_response("INVALID_JSON", "JSON body is required", 400)

    payload = request.get_json(silent=True)
    if payload is None:
        return None, error_response("INVALID_JSON", "JSON body is required", 400)

    if not isinstance(payload, dict):
        return None, error_response("INVALID_INPUT", "payload must be an object", 400)

    return payload, None


def to_iso8601(value):
    if value is None:
        return None

    if isinstance(value, str):
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return parsed.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
        except ValueError:
            return value

    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    return value


@api_bp.route("/run-battle", methods=["POST"])
def run_battle_route():
    payload, error = get_json_object()
    if error is not None:
        return error

    ok, code, message = validate_run_battle_payload(payload)
    if not ok:
        return error_response(code, message, 400)

    benchmark_size = payload["benchmark_size"]

    try:
        ranking = run_battle(benchmark_size)
        return success_response({"ranking": ranking}, 200)
    except ValueError as e:
        return error_response("INVALID_BENCHMARK_SIZE", str(e), 400)
    except RuntimeError:
        return error_response("INTERNAL_ERROR", "Internal server error", 500)
    except Exception:
        return error_response("INTERNAL_ERROR", "Internal server error", 500)


@api_bp.route("/battles", methods=["POST"])
@login_required
def create_battle():
    payload, error = get_json_object()
    if error is not None:
        return error

    ok, code, message = validate_battle_payload(payload)
    if not ok:
        return error_response(code, message, 400)

    try:
        battle_id = save_battle_result(
            user_id=g.user["id"],
            array_size=payload["array_size"],
            benchmark_size=payload["benchmark_size"],
            results=payload["results"],
        )
        return success_response({"battle_id": battle_id}, 201)
    except ValueError as e:
        return error_response("INVALID_REQUEST", str(e), 400)
    except RuntimeError:
        return error_response("INTERNAL_ERROR", "Internal server error", 500)
    except Exception:
        return error_response("INTERNAL_ERROR", "Internal server error", 500)


@api_bp.route("/battles", methods=["GET"])
@login_required
def list_battles():
    ok, code, message, limit = validate_limit(request.args.get("limit"), max_value=50)
    if not ok:
        return error_response(code, message, 400)

    if limit is None:
        limit = 10

    try:
        rows = get_battle_history(user_id=g.user["id"], limit=limit)

        normalized_rows = []
        for row in rows:
            item = dict(row)
            if "created_at" in item:
                item["created_at"] = to_iso8601(item["created_at"])
            normalized_rows.append(item)

        return success_response(normalized_rows, 200)
    except ValueError as e:
        return error_response("INVALID_LIMIT", str(e), 400)
    except RuntimeError:
        return error_response("INTERNAL_ERROR", "Internal server error", 500)
    except Exception:
        return error_response("INTERNAL_ERROR", "Internal server error", 500)


@api_bp.route("/statistics", methods=["GET"])
@login_required
def statistics():
    ok, code, message, limit = validate_limit(request.args.get("limit"), max_value=1000)
    if not ok:
        return error_response(code, message, 400)

    if limit is None:
        limit = 10

    try:
        data = get_statistics(user_id=g.user["id"], limit=limit)
        return success_response(data, 200)
    except ValueError as e:
        return error_response("INVALID_LIMIT", str(e), 400)
    except RuntimeError:
        return error_response("INTERNAL_ERROR", "Internal server error", 500)
    except Exception:
        return error_response("INTERNAL_ERROR", "Internal server error", 500)