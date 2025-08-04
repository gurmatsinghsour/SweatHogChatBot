
## Data Flow & Processing

### Conversation Flow Diagram

```
User Input
    │
    ▼
┌─────────────────┐
│   Tokenization  │
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│ Feature Extract │
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│ Intent Classify │ ──── DIET Model
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│ Entity Extract  │ ──── DIET Model
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│ Policy Decision │ ──── TED Policy
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│ Action Execute  │ ──── Custom Actions
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│ Response Gen    │
└─────┬───────────┘
      │
      ▼
User Response
```
