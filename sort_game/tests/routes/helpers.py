# tests/routes/helpers.py

TEST_LOGIN_EMAIL = "test@1234.com"
TEST_LOGIN_PASSWORD = "app_password"


def login_and_get_auth_headers(client):
    response = client.post(
        "/api/auth/login",
        json={
            "email": TEST_LOGIN_EMAIL,
            "password": TEST_LOGIN_PASSWORD,
        },
    )

    assert response.status_code == 200

    body = response.get_json()
    assert body is not None
    assert body["success"] is True
    assert body["data"] is not None
    assert "accessToken" in body["data"]

    token = body["data"]["accessToken"]

    return {
        "Authorization": f"Bearer {token}",
    }