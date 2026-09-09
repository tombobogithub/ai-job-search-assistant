from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_job():
    response = client.post(
        "/jobs",
        json={
            "company": "Test Company",
            "title": "Test Engineer",
            "location": "San Diego, CA",
            "Status": "saved",
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["company"] == "Test Company"
    assert data["title"] == "Test Engineer"
    assert data["location"] == "San Diego, CA"
    assert data["status"] == "saved"
    assert "id" in data
