from pathlib import Path
import os

from dotenv import load_dotenv
from flask import Flask

from app.routes.page_routes import page_bp
from app.routes.api_routes import api_bp
from app.routes.auth_routes import auth_bp


BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file(config_name: str) -> None:
    if config_name == "testing":
        env_path = BASE_DIR / ".env.test"
    elif config_name == "production":
        env_path = BASE_DIR / ".env.production"
    else:
        env_path = BASE_DIR / ".env"

    if env_path.exists():
        load_dotenv(env_path, override=True)


def create_app(config_name: str | None = None) -> Flask:
    config_name = config_name or os.getenv("APP_ENV", "development")

    if config_name not in {"development", "testing", "production"}:
        raise RuntimeError(f"Unknown config name: {config_name}")

    # config.py を import する前に env を読む
    _load_env_file(config_name)

    from app.config import config_by_name

    app = Flask(__name__)

    config_class = config_by_name[config_name]
    app.config.from_object(config_class)
    config_class.validate()

    app.register_blueprint(page_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    return app