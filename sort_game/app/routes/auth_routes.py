from flask import Blueprint, current_app, jsonify, request

from app.services.auth_service import login_user

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "email and password are required"
            }
        }), 400

    result = login_user(
        email=email,
        password=password,
        secret_key=current_app.config["SECRET_KEY"],
    )

    if not result:
        return jsonify({
            "success": False,
            "error": {
                "code": "AUTH_INVALID_CREDENTIALS",
                "message": "メールアドレスまたはパスワードが違います"
            }
        }), 401

    return jsonify({
        "success": True,
        "data": result
    }), 200