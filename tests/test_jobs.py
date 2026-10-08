from datetime import datetime
import time

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
        db.query(models.JobStatiusHistory).delete()
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
            "status": "saved",
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


def test_create_job_invalid_status():
    response = client.post(
        "/jobs",
        json={
            "company": "Google",
            "title": "Software Engineer",
            "location": "Mountain View, CA",
            "status": "banana",
        },
    )

    assert response.status_code == 422


def test_patch_job_invalid_status():
    create_response = client.post(
        "/jobs",
        json={
            "company": "Microsoft",
            "title": "Software Engineer",
            "location": "Redmond, WA",
            "status": "saved",
        },
    )

    job_id = create_response.json()["id"]

    patch_response = client.patch(
        f"/jobs/{job_id}",
        json={
            "status": "banana",
        },
    )

    assert patch_response.status_code == 422


def test_patch_job_preserves_unset_fields():
    create_response = client.post(
        "/jobs",
        json={
            "company": "Google",
            "title": "Backend Engineer",
            "location": "Mountain View, CA",
            "status": "saved",
        },
    )

    job_id = create_response.json()["id"]

    patch_response = client.patch(
        f"/jobs/{job_id}",
        json={
            "status": "interview",
        },
    )

    assert patch_response.status_code == 200

    updated_job = patch_response.json()

    assert updated_job["status"] == "interview"
    assert updated_job["company"] == "Google"
    assert updated_job["title"] == "Backend Engineer"
    assert updated_job["location"] == "Mountain View, CA"


def test_filter_jobs_invalid_status():
    response = client.get(
        "/jobs",
        params={"status": "banana"},
    )

    assert response.status_code == 422


def test_updated_at_changes_after_patch():
    create_response = client.post(
        "/jobs",
        json={
            "company": "Test Company",
            "title": "Software Engineer",
            "location": "San Diego",
        },
    )

    assert create_response.status_code == 200

    created_job = create_response.json()
    original_updated_at = datetime.fromisoformat(
        created_job["updated_at"]
    )

    time.sleep(0.05)

    patch_response = client.patch(
        f"/jobs/{created_job['id']}",
        json={"status": "applied"},
    )

    assert patch_response.status_code == 200

    patched_job = patch_response.json()
    new_updated_at = datetime.fromisoformat(
        patched_job["updated_at"]
    )

    assert new_updated_at > original_updated_at


def test_create_job_records_initial_status():
    response = client.post(
        "jobs",
        json={
            "company": "Google",
            "title": "Software Engineer",
            "location": "California",
        },
    )

    assert response.status_code == 200

    job_id = response.json()["id"]

    db = TestingSessionLocal()

    try:
        history = (
            db.query(models.JobStatiusHistory)
            .filter(models.JobStatiusHistory.job_id == job_id)
            .all()
        )

        assert len(history) == 1
        assert history[0].status == "saved"

    finally:
        db.close()


def test_patch_job_records_status_history():
    # Create a job
    response = client.post(
        "/jobs",
        json={
            "company": "Google",
            "title": "Software Engineer",
            "location": "California",
            "status": "saved",
        },
    )

    assert response.status_code == 200
    job_id = response.json()["id"]

    # Change status: saved -> applied
    response = client.patch(
        f"/jobs/{job_id}",
        json={"status": "applied"},
    )

    assert response.status_code == 200

    # Check history in PostgreSQL
    db = TestingSessionLocal()

    try:
        history = (
            db.query(models.JobStatiusHistory)
            .filter(models.JobStatiusHistory.job_id == job_id)
            .order_by(models.JobStatiusHistory.id)
            .all()
        )

        assert len(history) == 2
        assert history[0].status == "saved"
        assert history[1].status == "applied"

    finally:
        db.close()


def test_patch_without_status_change_does_not_add_history():
    # Create a job with initial status "saved"
    response = client.post(
        "/jobs",
        json={
            "company": "Google",
            "title": "Software Engineer",
            "location": "California",
        },
    )

    assert response.status_code == 200
    job_id = response.json()["id"]

    # Update title only
    response = client.patch(
        f"/jobs/{job_id}",
        json={"title": "Senior Software Engineer"},
    )

    assert response.status_code == 200

    # PATCH the same status
    response = client.patch(
        f"/jobs/{job_id}",
        json={"status": "saved"},
    )

    assert response.status_code == 200

    # Check history
    db = TestingSessionLocal()

    try:
        history = (
            db.query(models.JobStatiusHistory)
            .filter(models.JobStatiusHistory.job_id == job_id)
            .all()
        )

        # Only the initial "saved" record should exist
        assert len(history) == 1
        assert history[0].status == "saved"

    finally:
        db.close()


def test_get_job_status_history():
    response = client.post(
        "/jobs",
        json={
            "company": "Google",
            "title": "Software Engineer",
            "location": "California",
        },
    )

    assert response.status_code == 200
    job_id = response.json()["id"]

    response = client.patch(
        f"/jobs/{job_id}",
        json={"status": "applied"},
    )

    assert response.status_code == 200

    response = client.patch(
        f"/jobs/{job_id}",
        json={"status": "interview"},
    )

    assert response.status_code == 200

    # Retrieve status history through API
    response = client.get(f"/jobs/{job_id}/history")

    assert response.status_code == 200

    history = response.json()

    # Verifying history
    assert len(history) == 3

    assert [record["status"] for record in history] == [
        "saved",
        "applied",
        "interview",
    ]

    assert all(record["job_id"] == job_id for record in history)
    assert all(record["changed_at"] is not None for record in history)

