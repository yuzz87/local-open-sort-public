import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in ("1", "true", "yes", "on")


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    DEBUG = False
    TESTING = False

    # Database
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = _get_int("DB_PORT", 3306)
    DB_USER = os.getenv("DB_USER", "")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "")

    # OpenAPI / Swagger
    OPENAPI_PATH = os.getenv(
        "OPENAPI_PATH",
        str(BASE_DIR / "openapi" / "openapi.yaml")
    )
    SWAGGER_ENABLED = _get_bool("SWAGGER_ENABLED", True)

    # App options
    ALLOW_PUBLIC_SIGNUP = _get_bool("ALLOW_PUBLIC_SIGNUP", True)
    GUEST_SAVE_ENABLED = _get_bool("GUEST_SAVE_ENABLED", False)

    # Flask
    MAX_CONTENT_LENGTH = _get_int("MAX_CONTENT_LENGTH", 1024 * 1024)
    JSON_AS_ASCII = False

    # API validation settings
    RUN_BATTLE_ARRAY_SIZE_MIN = _get_int("RUN_BATTLE_ARRAY_SIZE_MIN", 100)
    RUN_BATTLE_ARRAY_SIZE_MAX = _get_int("RUN_BATTLE_ARRAY_SIZE_MAX", 1000000)

    SAVE_BATTLE_ARRAY_SIZE_MIN = _get_int("SAVE_BATTLE_ARRAY_SIZE_MIN", 5)
    SAVE_BATTLE_ARRAY_SIZE_MAX = _get_int("SAVE_BATTLE_ARRAY_SIZE_MAX", 100)

    SAVE_BATTLE_BENCHMARK_SIZE_MIN = _get_int("SAVE_BATTLE_BENCHMARK_SIZE_MIN", 100)
    SAVE_BATTLE_BENCHMARK_SIZE_MAX = _get_int("SAVE_BATTLE_BENCHMARK_SIZE_MAX", 10000)

    BATTLES_LIMIT_MIN = _get_int("BATTLES_LIMIT_MIN", 1)
    BATTLES_LIMIT_MAX = _get_int("BATTLES_LIMIT_MAX", 50)

    STATISTICS_LIMIT_MIN = _get_int("STATISTICS_LIMIT_MIN", 1)
    STATISTICS_LIMIT_MAX = _get_int("STATISTICS_LIMIT_MAX", 1000)

    REQUIRED_DB_FIELDS = ("DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME")

    @classmethod
    def validate(cls) -> None:
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SWAGGER_ENABLED = _get_bool("SWAGGER_ENABLED", True)
    ALLOW_PUBLIC_SIGNUP = _get_bool("ALLOW_PUBLIC_SIGNUP", True)
    GUEST_SAVE_ENABLED = _get_bool("GUEST_SAVE_ENABLED", False)

    @classmethod
    def validate(cls) -> None:
        missing = []

        if not cls.DB_HOST:
            missing.append("DB_HOST")
        if not cls.DB_USER:
            missing.append("DB_USER")
        if not cls.DB_NAME:
            missing.append("DB_NAME")

        if missing:
            raise RuntimeError(
                f"Missing required development settings: {', '.join(missing)}"
            )


class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY", "test-secret")
    SWAGGER_ENABLED = False
    ALLOW_PUBLIC_SIGNUP = _get_bool("ALLOW_PUBLIC_SIGNUP", True)
    GUEST_SAVE_ENABLED = _get_bool("GUEST_SAVE_ENABLED", False)

    # テストではやや小さめの制限にしてもよい
    RUN_BATTLE_ARRAY_SIZE_MAX = _get_int("RUN_BATTLE_ARRAY_SIZE_MAX", 10000)
    SAVE_BATTLE_BENCHMARK_SIZE_MAX = _get_int("SAVE_BATTLE_BENCHMARK_SIZE_MAX", 1000)

    @classmethod
    def validate(cls) -> None:
        missing = []

        if not cls.DB_HOST:
            missing.append("DB_HOST")
        if not cls.DB_USER:
            missing.append("DB_USER")
        if cls.DB_PASSWORD in (None, ""):
            missing.append("DB_PASSWORD")
        if not cls.DB_NAME:
            missing.append("DB_NAME")

        if missing:
            raise RuntimeError(
                f"Missing required testing settings: {', '.join(missing)}"
            )


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SWAGGER_ENABLED = _get_bool("SWAGGER_ENABLED", False)
    ALLOW_PUBLIC_SIGNUP = _get_bool("ALLOW_PUBLIC_SIGNUP", False)
    GUEST_SAVE_ENABLED = _get_bool("GUEST_SAVE_ENABLED", False)

    @classmethod
    def validate(cls) -> None:
        missing = []

        if cls.SECRET_KEY in (None, "", "dev-secret-change-me"):
            missing.append("SECRET_KEY")
        if not cls.DB_HOST:
            missing.append("DB_HOST")
        if not cls.DB_USER:
            missing.append("DB_USER")
        if cls.DB_PASSWORD in (None, ""):
            missing.append("DB_PASSWORD")
        if not cls.DB_NAME:
            missing.append("DB_NAME")

        if missing:
            raise RuntimeError(
                f"Missing required production settings: {', '.join(missing)}"
            )


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}