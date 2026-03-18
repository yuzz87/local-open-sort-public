# tests/routes/test_page_routes.py

def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_select_page(client):
    response = client.get("/select")
    assert response.status_code == 200


def test_game_a_description_page(client):
    response = client.get("/game-a-Description")
    assert response.status_code == 200


def test_game_b_description_start_page(client):
    response = client.get("/game-b-Description/start")
    assert response.status_code == 200


def test_game_a_description_start_page(client):
    response = client.get("/game-a-Description/start")
    assert response.status_code == 200