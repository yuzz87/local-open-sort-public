# tests/routes/test_statistics_routes.py

from tests.routes.helpers import login_and_get_auth_headers


def test_get_statistics_requires_auth(client):
    response = client.get("/api/statistics")
    assert response.status_code == 401


def test_get_statistics_empty(client, clean_db, auth_user):
    headers = login_and_get_auth_headers(client)

    response = client.get("/api/statistics", headers=headers)
    assert response.status_code == 200

    body = response.get_json()
    assert body is not None
    assert body["success"] is True
    assert body["error"] is None
    assert isinstance(body["data"], dict)
    assert body["data"] == {}