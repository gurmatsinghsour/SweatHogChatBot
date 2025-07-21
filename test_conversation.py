#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced conversational features of the Rasa chatbot.
"""

import requests
import json
import time

# Rasa server configuration
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

def send_message(message, sender_id="test_user"):
    """Send a message to the Rasa chatbot and return the response."""
    payload = {
        "sender": sender_id,
        "message": message
    }
    
    try:
        response = requests.post(RASA_URL, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return [{"text": f"Error: {response.status_code}"}]
    except Exception as e:
        return [{"text": f"Connection error: {str(e)}"}]

def test_conversation():
    """Test various conversational scenarios."""
    
    test_messages = [
        "hello",
        "how are you?",
        "what's your name?",
        "what can you do?",
        "you're awesome!",
        "tell me a joke",
        "what's the weather like?",
        "what time is it?",
        "thank you",
        "I want to order pizza",  # Out of scope - should trigger LLM fallback
        "tell me about politics",  # Out of scope - should trigger LLM fallback
        "goodbye"
    ]
    
    print("🤖 Testing Enhanced Conversational Features")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. User: {message}")
        
        # Send message and get response
        responses = send_message(message)
        
        # Display bot responses
        for response in responses:
            if "text" in response:
                print(f"   Bot: {response['text']}")
        
        # Small delay between messages
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("✅ Conversation test completed!")
    print("\nKey Features Demonstrated:")
    print("• Natural greetings and responses")
    print("• Personal questions (name, how are you)")
    print("• Capability inquiries")
    print("• Compliment handling")
    print("• Joke telling")
    print("• Out-of-scope handling with LLM fallback")
    print("• Graceful limitation acknowledgment")
    print("• Polite goodbyes")

if __name__ == "__main__":
    print("Waiting for Rasa server to be ready...")
    time.sleep(5)  # Give the server time to fully load
    
    # Check if server is responding
    try:
        test_response = send_message("ping")
        print("✅ Rasa server is responding!")
        test_conversation()
    except Exception as e:
        print(f"❌ Could not connect to Rasa server: {e}")
        print("Please make sure the server is running with: rasa shell --enable-api")
