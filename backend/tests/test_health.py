from fastapi.testclient import TestClient

# This test requires a working test database configuration.
# It is intentionally small so you can expand it with pytest fixtures.

def test_health():
    from app.main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
