from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app, get_db

TEST_DATABASE_URL = "postgresql+psycopg://localhost/job_search_test"

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
        db.closed()

app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=test_engine)

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

'''
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
'''