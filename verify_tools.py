"""
Verification script for Custom Tools.
"""
import os
import sys
from typing import Dict, Any

# Add root to path
sys.path.append(os.getcwd())

from tools.calendar_mapper_tool import get_available_time_slots
from tools.preference_learner_tool import learn_preferences_from_chat
from tools.google_classroom_tool import summarize_assignment

def test_calendar_tool():
    print("\n--- Testing Calendar Tool ---")
    # Should handle missing user gracefully
    slots = get_available_time_slots("non_existent_student")
    print(f"Slots for non-existent student: {slots}")
    assert isinstance(slots, list)

def test_preference_tool():
    print("\n--- Testing Preference Tool ---")
    # Should handle missing API key or user gracefully
    prefs = learn_preferences_from_chat("test_student", "I love math and I hate waking up early.")
    print(f"Extracted prefs: {prefs}")
    assert isinstance(prefs, dict)

def test_summarizer_tool():
    print("\n--- Testing Summarizer Tool ---")
    assignment = {
        "title": "Complex Math Project",
        "description": "This is a very long description that needs summarizing. " * 10
    }
    summary = summarize_assignment(assignment)
    print(f"Summary result: {summary}")
    assert "summary" in summary
    assert "key_requirements" in summary

if __name__ == "__main__":
    test_calendar_tool()
    test_preference_tool()
    test_summarizer_tool()
    print("\nAll tools verified successfully!")
