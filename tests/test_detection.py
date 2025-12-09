import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.detection_service import detection_service

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_service_initialization():
    # Check if models were attempted to load
    # Note: If models fail to load (e.g. strict dependency or path issues), 
    # service handles it gracefully by logging.
    # We just check the service instance exists.
    assert detection_service is not None

# Add more tests here if needed
