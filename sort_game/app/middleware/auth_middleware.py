from functools import wraps

import jwt
from flask import current_app, g, jsonify, request


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "error": {
                    "code": "AUTH_UNAUTHORIZED",
                    "message": "Authentication required"
                }
            }), 401

        token = auth_header.split(" ", 1)[1]

        try:
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
            g.user = {
                "id": int(payload["sub"]),
                "email": payload["email"],
            }
        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "error": {
                    "code": "AUTH_TOKEN_EXPIRED",
                    "message": "Token expired"
                }
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "error": {
                    "code": "AUTH_INVALID_TOKEN",
                    "message": "Invalid token"
                }
            }), 401

        return func(*args, **kwargs)

    return wrapper