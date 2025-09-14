#!/usr/bin/env python3
"""
Unit tests for MedMitra actions.
Run with pytest: `pytest tests/test_actions.py`
"""

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.actions import ActionProvidePreventiveHealthcare, ActionProvideDiseaseSymptoms
from typing import Any, Dict, List, Text
import json

# Mock functions and classes for testing
def get_tracker_with_message(message, slots=None):
    if slots is None:
        slots = {}
    return Tracker(
        "test_sender",
        slots,
        {"entities": []},
        [{"text": message}],
        False,
        None,
        {},
        "action_listen"
    )

# Test preventive healthcare action
def test_action_provide_preventive_healthcare():
    # Mock a dispatcher
    dispatcher = CollectingDispatcher()
    
    # Create a test tracker
    tracker = get_tracker_with_message("How can I stay healthy?")
    
    # Create an action instance
    action = ActionProvidePreventiveHealthcare()
    
    # Execute the action
    action.run(dispatcher, tracker, {})
    
    # Assert that messages were sent
    assert len(dispatcher.messages) > 0
    
    # Check that the response is not empty
    for message in dispatcher.messages:
        assert "text" in message
        assert message["text"].strip()
        print(f"Response: {message['text']}")

# Test disease symptoms action
def test_action_provide_disease_symptoms():
    # Mock a dispatcher
    dispatcher = CollectingDispatcher()
    
    # Create a test tracker with a disease slot
    tracker = get_tracker_with_message(
        "What are the symptoms of malaria?",
        {"disease": "malaria"}
    )
    
    # Create an action instance
    action = ActionProvideDiseaseSymptoms()
    
    # Execute the action
    action.run(dispatcher, tracker, {})
    
    # Assert that messages were sent
    assert len(dispatcher.messages) > 0
    
    # Check that the response is not empty and contains the disease name
    for message in dispatcher.messages:
        assert "text" in message
        assert message["text"].strip()
        print(f"Response: {message['text']}")
        assert "malaria" in message["text"].lower()

if __name__ == "__main__":
    print("Running tests...")
    test_action_provide_preventive_healthcare()
    test_action_provide_disease_symptoms()
    print("Tests completed.")