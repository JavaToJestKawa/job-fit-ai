from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analyze_endpoint_creates_application():
    payload = {
        "company": "Example Corp",
        "job_title": "Junior Backend Developer",
        "job_description": "We need Python, FastAPI, Docker, PostgreSQL and REST API skills.",
        "cv_text": "I know Python, FastAPI, SQL and Git. I built a backend API project.",
    }

    response = client.post("/api/applications/analyze", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["company"] == "Example Corp"
    assert data["job_title"] == "Junior Backend Developer"
    assert data["status"] == "saved"
    assert data["fit_score"] > 0

    cleanup_response = client.delete(f"/api/applications/{data['id']}")
    assert cleanup_response.status_code == 204
