from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_case_returns_one_open_task():
    payload = {"title": "Fraud Investigation", "about": "Customer reported unauthorized charges", "priority": "high"}
    response = client.post("/cases/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Fraud Investigation"
    assert data["about"] == "Customer reported unauthorized charges"
    assert data["status"] == "open"
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["status"] == "open"
    assert data["tasks"][0]["title"] == "Initial review"


def test_get_case_includes_tasks():
    payload = {"title": "Support Request", "about": "User cannot log in", "priority": "medium"}
    case_id = client.post("/cases/", json=payload).json()["id"]

    response = client.get(f"/cases/{case_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == case_id
    assert len(data["tasks"]) == 1


def test_list_tasks_for_case():
    payload = {"title": "Compliance Review", "about": "Annual audit", "priority": "low"}
    case_id = client.post("/cases/", json=payload).json()["id"]

    response = client.get(f"/cases/{case_id}/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["case_id"] == case_id


def test_update_task_status():
    payload = {"title": "Close Task", "about": "Something to close", "priority": "low"}
    case_data = client.post("/cases/", json=payload).json()
    case_id = case_data["id"]
    task_id = case_data["tasks"][0]["id"]

    response = client.patch(f"/cases/{case_id}/tasks/{task_id}", json={"status": "closed"})
    assert response.status_code == 200
    assert response.json()["status"] == "closed"


def test_update_case():
    payload = {"title": "Update Me", "about": "Original description", "priority": "low"}
    case_id = client.post("/cases/", json=payload).json()["id"]

    update_resp = client.patch(f"/cases/{case_id}", json={"status": "closed", "about": "Updated description"})
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["status"] == "closed"
    assert data["about"] == "Updated description"


def test_delete_case_removes_tasks():
    payload = {"title": "Delete Me", "about": "To be removed", "priority": "low"}
    case_id = client.post("/cases/", json=payload).json()["id"]

    assert client.delete(f"/cases/{case_id}").status_code == 204
    assert client.get(f"/cases/{case_id}").status_code == 404
    assert client.get(f"/cases/{case_id}/tasks").status_code == 404


def test_case_not_found():
    assert client.get("/cases/99999").status_code == 404
