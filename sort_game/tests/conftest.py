import bcrypt
import pytest

from app import create_app
from app.db.mysql_pool import get_connection, reset_pool


TEST_LOGIN_EMAIL = "test@1234.com"
TEST_LOGIN_PASSWORD = "app_password"
TEST_LOGIN_USERNAME = "testuser1234"


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    app.config.update(TESTING=True)

    yield app

    reset_pool()


@pytest.fixture()
def app_ctx(app):
    with app.app_context():
        yield app


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture()
def clean_db(app_ctx):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE battle_results")
        cursor.execute("TRUNCATE TABLE battles")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        yield
    finally:
        cursor.close()
        conn.close()


@pytest.fixture()
def auth_user(app_ctx):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        password_hash = bcrypt.hashpw(
            TEST_LOGIN_PASSWORD.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        cursor.execute("DELETE FROM users WHERE email = %s", (TEST_LOGIN_EMAIL,))
        cursor.execute("DELETE FROM users WHERE username = %s", (TEST_LOGIN_USERNAME,))
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            (TEST_LOGIN_USERNAME, TEST_LOGIN_EMAIL, password_hash),
        )
        conn.commit()
        yield
    finally:
        cursor.close()
        conn.close()


@pytest.fixture()
def valid_results():
    return [
        {"algorithm": "quick", "duration_ms": 0.058, "rank": 1},
        {"algorithm": "merge", "duration_ms": 0.084, "rank": 2},
        {"algorithm": "heap", "duration_ms": 0.110, "rank": 3},
        {"algorithm": "insertion", "duration_ms": 0.286, "rank": 4},
        {"algorithm": "selection", "duration_ms": 3.495, "rank": 5},
        {"algorithm": "bubble", "duration_ms": 5.934, "rank": 6},
    ]


@pytest.fixture()
def valid_battle_payload(valid_results):
    return {
        "user_id": None,
        "array_size": 40,
        "benchmark_size": 2000,
        "results": valid_results,
    }


@pytest.fixture()
def valid_run_battle_payload():
    return {
        "benchmark_size": 2000,
    }

###############test