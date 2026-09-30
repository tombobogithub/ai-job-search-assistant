import os
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.main import app, get_db

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://localhost/job_search_test",
)

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_database():
    db = TestingSessionLocal()

    try:
        db.query(models.Job).delete()
        db.commit()
    finally:
        db.close()


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
            "job_url": "https://example.com/jobs/1"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["company"] == "Test Company"
    assert data["title"] == "Test Engineer"
    assert data["location"] == "San Diego, CA"
    assert data["status"] == "saved"
    assert data["job_url"] == "https://example.com/jobs/1"
    assert "id" in data
    assert "created_at" in data

def test_get_job():
    create_response = client.post(
        "/jobs",
        json={
            "company": "Google",
            "title": "Software Engineer",
            "location": "Mountain View, CA",
            "status": "saved",
        },
    )

    job_id = create_response.json()["id"]

    response = client.get(f"/jobs/{job_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == job_id
    assert data["company"] == "Google"
    assert data["title"] == "Software Engineer"

def test_patch_job():
    create_response = client.post(
        "/jobs",
        json={
            "company": "Microsoft",
            "title": "Software Engineer",
            "location": "Redmond, WA",
            "status": "saved,"
        },
    )

    job_id = create_response.json()["id"]

    response = client.patch(
        f"/jobs/{job_id}",
        json={
            "status": "applied",
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == job_id
    assert data["company"] == "Microsoft"
    assert data["title"] == "Software Engineer"
    assert data["status"] == "applied"


def test_delete_job():
    create_response = client.post(
        "/jobs",
        json={
            "company": "Amazon",
            "title": "Software Engineer",
            "location": "Seattle, WA",
            "status": "saved",
         },
    )

    job_id = create_response.json()["id"]

    delete_response = client.delete(f"/jobs/{job_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Job deleted"

    get_response = client.get(f"/jobs/{job_id}")

    assert get_response.status_code == 404


def test_job_not_found():
    response = client.get("/jobs/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Job not found"}