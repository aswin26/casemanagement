from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_case():
    payload = {"title": "Test Case", "description": "A test case", "priority": "high"}
    response = client.post("/cases/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Case"
    assert data["status"] == "open"

    case_id = data["id"]
    response = client.get(f"/cases/{case_id}")
    assert response.status_code == 200
    assert response.json()["id"] == case_id


def test_update_case():
    payload = {"title": "Update Me", "description": "desc", "priority": "low"}
    create_resp = client.post("/cases/", json=payload)
    case_id = create_resp.json()["id"]

    update_resp = client.patch(f"/cases/{case_id}", json={"status": "closed"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "closed"


def test_delete_case():
    payload = {"title": "Delete Me", "description": "desc", "priority": "low"}
    case_id = client.post("/cases/", json=payload).json()["id"]

    assert client.delete(f"/cases/{case_id}").status_code == 204
    assert client.get(f"/cases/{case_id}").status_code == 404


def test_case_not_found():
    response = client.get("/cases/99999")
    assert response.status_code == 404
