import time
import mysql.connector
from mysql.connector import pooling
from flask import current_app

_pool = None
_pool_settings = None


def _build_pool_settings():
    return {
        "host": current_app.config["DB_HOST"],
        "port": current_app.config["DB_PORT"],
        "user": current_app.config["DB_USER"],
        "password": current_app.config["DB_PASSWORD"],
        "database": current_app.config["DB_NAME"],
    }


def _create_pool(settings):
    return pooling.MySQLConnectionPool(
        pool_name="sort_portfolio_pool",
        pool_size=10,
        pool_reset_session=True,
        host=settings["host"],
        port=settings["port"],
        user=settings["user"],
        password=settings["password"],
        database=settings["database"],
        charset="utf8mb4",
        autocommit=False,
        connect_timeout=5,
    )


def _ensure_pool():
    global _pool, _pool_settings

    settings = _build_pool_settings()

    if _pool is None or _pool_settings != settings:
        retry = 5

        for _ in range(retry):
            try:
                _pool = _create_pool(settings)
                _pool_settings = settings
                print(
                    "MySQL connection pool created: "
                    f'{settings["host"]}:{settings["port"]}/{settings["database"]}'
                )
                break
            except mysql.connector.Error as e:
                print(f"MySQL connection failed: {e}")
                time.sleep(2)
        else:
            raise RuntimeError("MySQL connection failed after retries")

# 変更する際注意（他のモジュールへの影響を確認）
def get_conn():
    _ensure_pool()

    try:
        conn = _pool.get_connection()
        conn.set_charset_collation("utf8mb4", "utf8mb4_unicode_ci")
        return conn
    except mysql.connector.Error as e:
        raise RuntimeError(f"Failed to get MySQL connection from pool: {e}") from e


def get_connection():
    return get_conn()


def reset_pool():
    global _pool, _pool_settings
    _pool = None
    _pool_settings = None