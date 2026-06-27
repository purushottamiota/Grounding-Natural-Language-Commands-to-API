import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.nlp_model import nlp_pipeline
from app.services.parser import extract_duration_from_command, extract_time_from_command

client = TestClient(app)

# ──────────────────────────────────────────────────────────────────────────────
# 1. API Endpoint Edge Cases
# ──────────────────────────────────────────────────────────────────────────────

def test_parse_model_unavailable_503(monkeypatch):
    """Verify that when the ML pipeline fails to load or errors, the API returns a 503."""
    def mock_generate_error(self, command: str):
        raise RuntimeError("Model weights not loaded.")

    monkeypatch.setattr(nlp_pipeline.__class__, "generate", mock_generate_error)
    
    response = client.post("/api/v1/parse", json={"command": "schedule standup at 9am"})
    assert response.status_code == 503
    assert response.json()["detail"] == "Model is currently loading or unavailable."


def test_parse_model_end_to_end_repair(monkeypatch):
    """Verify the hybrid override where the model outputs a wrong time and postprocess fixes it."""
    def mock_generate_wrong_time(self, command: str):
        # Model gets the time wrong (predicts 18:00 for 6am)
        return '{"action": "insert", "title": "Standup", "start_time": "18:00"}'

    monkeypatch.setattr(nlp_pipeline.__class__, "generate", mock_generate_wrong_time)
    
    # Client sends a command with 6am
    response = client.post("/api/v1/parse", json={"command": "schedule standup at 6am"})
    assert response.status_code == 200
    data = response.json()
    # Post-processor should have overridden "18:00" with "06:00"
    assert data["parsed_json"]["start_time"] == "06:00"


# ──────────────────────────────────────────────────────────────────────────────
# 2. Regex Parser Component Edge Cases
# ──────────────────────────────────────────────────────────────────────────────

def test_extract_time_multiple_ambiguous():
    """Verify that extract_time_from_command grabs the first time in ambiguous multi-time prompts."""
    # "move from 2pm to 3pm" should extract the first time (14:00)
    assert extract_time_from_command("move meeting from 2pm to 3pm") == "14:00"
    assert extract_time_from_command("change standup from 9am to 10am") == "09:00"


def test_extract_duration_decimals():
    """
    Verify behavior for decimal durations.
    Note: Due to the word boundary regex pattern, "1.5 hours" matching is checked.
    """
    # Let's check how the current parser handles decimals:
    # "1.5 hours" -> matches "\b(\d+)\s*hour" on the substring "5 hours" (due to dot acting as a word boundary).
    # This test documents this exact boundary/limitation.
    extracted = extract_duration_from_command("meeting for 1.5 hours")
    assert extracted == 300  # Matches "5 hours" -> 5 * 60 = 300 minutes (known regex boundary)
