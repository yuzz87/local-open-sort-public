import datetime

import bcrypt
import jwt

from app.repositories.user_repository import find_user_by_email


def login_user(email: str, password: str, secret_key: str):
    user = find_user_by_email(email)

    if not user or not user["is_active"]:
        return None

    password_ok = bcrypt.checkpw(
        password.encode("utf-8"),
        user["password_hash"].encode("utf-8"),
    )

    if not password_ok:
        return None

    now = datetime.datetime.utcnow()

    payload = {
        "sub": str(user["id"]),
        "email": user["email"],
        "exp": now + datetime.timedelta(days=1),
        "iat": now,
    }

    token = jwt.encode(payload, secret_key, algorithm="HS256")

    return {
        "accessToken": token,
        "expiresIn": 86400,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
        },
    }