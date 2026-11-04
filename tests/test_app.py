import pytest

from app import main


@pytest.fixture()
def client():
    main.TASKS.clear()
    main._next_id = 1
    main.app.config["TESTING"] = True
    with main.app.test_client() as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_create_and_list_task(client):
    r = client.post("/tasks", json={"title": "Write pipeline"})
    assert r.status_code == 201
    assert r.get_json()["title"] == "Write pipeline"
    assert len(client.get("/tasks").get_json()) == 1


def test_rejects_empty_title(client):
    assert client.post("/tasks", json={"title": "  "}).status_code == 400


def test_rejects_oversized_title(client):
    assert client.post("/tasks", json={"title": "x" * 201}).status_code == 400


def test_complete_task(client):
    client.post("/tasks", json={"title": "Scan image"})
    r = client.patch("/tasks/1")
    assert r.get_json()["done"] is True


def test_missing_task_returns_404(client):
    assert client.patch("/tasks/99").status_code == 404


def test_security_headers_present(client):
    r = client.get("/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
