# tests/routes/test_run_battle_routes.py

def test_run_battle_invalid_json(client):
    response = client.post(
        "/api/run-battle",
        data="not-json",
        content_type="text/plain",
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body is not None
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"] is not None
    assert body["error"]["code"] == "INVALID_JSON"
    assert body["error"]["message"] == "JSON body is required"