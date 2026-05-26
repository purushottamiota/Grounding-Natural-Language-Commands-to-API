import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.nlp_model import nlp_pipeline

client = TestClient(app)

# We need to mock the model generation for API tests so we don't need to load the real model
# which is slow and requires GPU/weights.

@pytest.fixture(autouse=True)
def mock_nlp_pipeline(monkeypatch):
    def mock_generate(self, command: str):
        if "sync" in command.lower():
            return '{"action": "insert", "title": "Sync", "start_time": "10:00"}'
        elif "cancel" in command.lower():
            return '{"action": "delete", "title": "Meeting"}'
        elif "malformed" in command.lower():
            return '{"action": "insert", "title": ' # Broken JSON
        return '{"action": "unknown"}'

    monkeypatch.setattr(nlp_pipeline.__class__, "generate", mock_generate)

def test_parse_valid_command():
    response = client.post("/api/v1/parse", json={"command": "Schedule a sync at 10am"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["parsed_json"]["action"] == "insert"
    assert data["parsed_json"]["title"] == "Sync"
    assert data["parsed_json"]["start_time"] == "10:00"

def test_parse_cancel_command():
    response = client.post("/api/v1/parse", json={"command": "Cancel my meeting"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["parsed_json"]["action"] == "delete"
    
def test_parse_malformed_json_fallback():
    # Even if model outputs malformed JSON, the regex postprocessor/salvager should try to handle it or fail gracefully.
    # In our mock, "malformed" returns '{"action": "insert", "title": '
    # The API should catch JSONDecodeError and return a 422 if it can't salvage it.
    response = client.post("/api/v1/parse", json={"command": "Make a malformed request"})
    assert response.status_code == 422
    assert "Could not generate valid JSON" in response.json()["detail"]["message"]

def test_missing_command_field():
    # Testing FastAPI validation
    response = client.post("/api/v1/parse", json={"not_command": "hello"})
    assert response.status_code == 422 # Unprocessable Entity
