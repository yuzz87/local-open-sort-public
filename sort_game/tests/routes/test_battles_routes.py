# tests/routes/test_battles_routes.py

from tests.routes.helpers import login_and_get_auth_headers


def test_post_battles_requires_auth(client, valid_results):
    payload = {
        "array_size": 40,
        "benchmark_size": 2000,
        "results": valid_results,
    }

    response = client.post("/api/battles", json=payload)
    assert response.status_code == 401


def test_get_battles_requires_auth(client):
    response = client.get("/api/battles")
    assert response.status_code == 401


def test_post_battles_success(client, valid_results, auth_user):
    headers = login_and_get_auth_headers(client)

    payload = {
        "array_size": 40,
        "benchmark_size": 2000,
        "results": valid_results,
    }

    response = client.post("/api/battles", json=payload, headers=headers)

    assert response.status_code == 201

    body = response.get_json()
    assert body is not None
    assert body["success"] is True
    assert body["data"] is not None
    assert isinstance(body["data"]["battle_id"], int)
    assert body["data"]["battle_id"] >= 1
    assert body["error"] is None