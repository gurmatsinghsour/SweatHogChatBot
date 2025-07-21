# Enhanced Conversational Features for Rasa Diabetes Chatbot

## Overview

Your Rasa chatbot has been significantly enhanced with more human-like conversational abilities and an intelligent LLM fallback system. The bot can now handle casual conversation, small talk, and out-of-scope questions while maintaining its core focus on diabetes health assessment.

## New Features Added

### 1. Conversational Intents

The following new intents have been added to make the bot more engaging:

- **`ask_how_are_you`** - Responds to "how are you" type questions
- **`ask_name`** - Answers questions about the bot's identity
- **`ask_capabilities`** - Explains what the bot can do
- **`small_talk`** - Handles casual conversation
- **`compliment_bot`** - Responds gracefully to compliments
- **`ask_weather`** - Politely explains it can't provide weather info
- **`ask_time`** - Explains it can't tell time but relates to health timing
- **`express_thanks`** - Responds to gratitude expressions
- **`ask_joke`** - Tells health-related jokes
- **`out_of_scope`** - Identifies clearly off-topic requests

### 2. LLM Fallback Integration

**Local LLM Integration**: The bot now integrates with Ollama running locally to provide intelligent responses to unexpected or out-of-scope queries.

**Fallback Action**: `action_llm_fallback` uses Llama 3.2 (1B model) to generate contextually appropriate responses that:
- Stay friendly and conversational
- Gently redirect to health topics when appropriate
- Provide general information while noting the bot's specialization
- Maintain the health-focused personality

### 3. Enhanced Responses

Each new intent has multiple response variations to make conversations feel more natural and less repetitive. The responses are:
- Friendly and engaging
- Health-focused when appropriate
- Encouraging and supportive
- Professional yet personable

## Example Conversations

### Basic Conversation
```
User: How are you?
Bot: I'm having a great day! My algorithms are running smoothly and I'm ready to tackle any health questions you have. How are things with you?

User: What's your name?
Bot: Great question! I'm your Diabetes Risk Assessment AI. I don't have a fancy name, but I like to think of myself as your digital health companion!
```

### Compliments and Thanks
```
User: You're awesome!
Bot: You're too kind! Comments like that make all my programming worthwhile. I'm glad I can be both helpful and pleasant to chat with!

User: Thank you
Bot: You're absolutely welcome! It's genuinely my pleasure to help. That's exactly what I'm here for - making health information accessible and useful!
```

### Out-of-Scope with LLM Fallback
```
User: I want to order pizza
Bot: 🤖 Pizza sounds delicious! But before you head out for delivery, have you been managing your blood sugar levels after dinner? It's always a good idea to talk to your healthcare provider about finding healthy ways to satisfy that late-night craving.
```

### Limitations Handled Gracefully
```
User: What's the weather like?
Bot: Sorry, weather forecasting isn't in my skill set - I'm focused on health assessments! But I can say that getting outside when it's nice is great for your overall wellbeing!
```

## Technical Implementation

### Files Modified
- **`domain.yml`** - Added new intents and responses
- **`data/nlu.yml`** - Added training examples for new intents
- **`data/rules.yml`** - Added rules for handling new intents
- **`data/stories.yml`** - Added conversation flows
- **`actions/actions.py`** - Added `ActionLLMFallback` class
- **`config.yml`** - Updated fallback configuration
- **`requirements-actions.txt`** - Added ollama dependency

### Dependencies
- **Ollama** - Local LLM server
- **Llama 3.2:1b** - Lightweight model for fast responses
- **ollama Python package** - API client for Ollama

## Setup Instructions

### 1. Install Ollama
```bash
brew install ollama
brew services start ollama
```

### 2. Download LLM Model
```bash
ollama pull llama3.2:1b
```

### 3. Install Python Dependencies
```bash
pip install ollama==0.3.3
```

### 4. Train and Run
```bash
rasa train
rasa run actions --auto-reload &
rasa shell --enable-api
```

## Testing

Use the provided test script to verify all features:
```bash
python test_conversation.py
```

## Fallback Behavior

1. **Intent Recognition** - Rasa first tries to match user input to known intents
2. **Fallback Threshold** - If confidence is below 0.25, fallback is triggered
3. **LLM Processing** - Ollama processes the query with health-focused context
4. **Contextual Response** - Returns helpful response that steers toward health topics
5. **Graceful Degradation** - If LLM fails, uses predefined generic responses

## Benefits

- **More Engaging** - Users feel like they're talking to a real assistant
- **Better User Experience** - Handles unexpected inputs gracefully
- **Maintains Focus** - Always tries to redirect to health topics
- **Intelligent Fallback** - Uses AI to handle novel situations
- **Professional Yet Friendly** - Balances medical expertise with approachability

## Future Enhancements

- Add more specialized health topics
- Integrate with external health APIs
- Implement user personalization
- Add multilingual support
- Enhance LLM prompting for better health guidance
