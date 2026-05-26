import pytest
from app.services.parser import extract_time_from_command, extract_title_from_command, extract_duration_from_command, postprocess

# --- Small individual tests for extraction logic ---

def test_extract_time_from_command():
    # Standard times
    assert extract_time_from_command("meeting at 3pm") == "15:00"
    assert extract_time_from_command("sync at 9am") == "09:00"
    assert extract_time_from_command("review at 10:30am") == "10:30"
    assert extract_time_from_command("call at 4:45 PM") == "16:45"
    
    # Special keywords
    assert extract_time_from_command("lunch at noon") == "12:00"
    assert extract_time_from_command("party at midnight") == "00:00"
    
    # Edge cases
    assert extract_time_from_command("12am deploy") == "00:00"
    assert extract_time_from_command("12pm sync") == "12:00"
    
    # No time mentioned
    assert extract_time_from_command("no time mentioned") is None

def test_extract_title_from_command():
    # Exact known keywords
    assert extract_title_from_command("schedule a retrospective with Alice") == "Retrospective"
    assert extract_title_from_command("set up a sync for tomorrow") == "Sync"
    
    # Inferring title from verbs
    assert extract_title_from_command("book a quick chat with Bob") == "Quick Chat"
    assert extract_title_from_command("schedule an interview next week") == "Interview"
    
    # Should ignore irrelevant text
    assert extract_title_from_command("tell Alice hello") is None

def test_extract_duration_from_command():
    # Hours
    assert extract_duration_from_command("meeting for 2 hours") == 120
    assert extract_duration_from_command("call for 1 hour") == 60
    assert extract_duration_from_command("call for an hour") == 60
    
    # Minutes
    assert extract_duration_from_command("sync for 30 mins") == 30
    assert extract_duration_from_command("sync for 45 minutes") == 45
    assert extract_duration_from_command("session for 90 min") == 90
    
    # Fractional
    assert extract_duration_from_command("chat for half an hour") == 30

# --- Tests for the post-processor logic ---

def test_postprocess_correction():
    # Test time injection when model misses it
    parsed = {"action": "insert", "title": "Meeting"}
    command = "schedule meeting at 4pm"
    corrected = postprocess(parsed, command)
    assert corrected["start_time"] == "16:00"
    
    # Test time correction when model gets it wrong
    parsed = {"action": "insert", "start_time": "14:00", "title": "Meeting"}
    command = "schedule meeting at 4pm"
    corrected = postprocess(parsed, command)
    assert corrected["start_time"] == "16:00" # Regex should override model
    
    # Test duration injection
    parsed = {"action": "insert", "title": "Meeting"}
    command = "schedule meeting for 2 hours"
    corrected = postprocess(parsed, command)
    assert corrected["duration_minutes"] == 120
    
    # Duration shouldn't be added for non-insert actions
    parsed = {"action": "delete", "title": "Meeting"}
    command = "cancel meeting for 2 hours"
    corrected = postprocess(parsed, command)
    assert "duration_minutes" not in corrected
