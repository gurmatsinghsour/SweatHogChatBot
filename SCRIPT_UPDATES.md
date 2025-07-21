# Start and Test Script Updates - Ollama Integration

## Overview
Updated the `start_and_test.sh` script to include comprehensive Ollama management for the local LLM fallback system.

## Changes Made

### 1. **Global Variables**
- Added `OLLAMA_PID=""` to track Ollama process
- Added `OLLAMA_STARTED_BY_SCRIPT=false` to track if we started Ollama

### 2. **Prerequisites Check**
- Added Ollama availability check
- Validates if Ollama service is running
- Checks if `llama3.2:1b` model is installed
- Provides installation guidance if missing

### 3. **New Function: `start_ollama_service()`**
- Checks if Ollama is already running (avoids duplicate processes)
- Starts Ollama service in background if needed
- Waits for service to be ready (API endpoint check)
- Automatically pulls `llama3.2:1b` model if missing
- Tracks whether script started Ollama vs. was already running

### 4. **Enhanced Cleanup Function**
- Gracefully stops Ollama if script started it
- Uses multiple methods: kill PID, `ollama stop`, and `pkill`
- Preserves existing Ollama instances that were running before script

### 5. **API Tests Enhancement**
- Added Ollama service health check
- Validates `llama3.2:1b` model availability
- Provides appropriate test results and status

### 6. **Service Status Check**
- Includes Ollama in service status display
- Shows all running services: Rasa, Actions, Frontend, Ollama

### 7. **Interactive Menu Updates**
- Updated descriptions to mention Ollama inclusion
- All service start options now include Ollama automatically

### 8. **Final Status Display**
- Shows Ollama API URL when available
- Enhanced with emojis and better formatting
- Lists all running service PIDs

## Script Execution Flow

### When Starting Services:
1. Check prerequisites (including Ollama)
2. Train model if needed
3. **Start Ollama service** ← NEW
4. Start Rasa server
5. Start Actions server
6. Start Frontend
7. Run tests (including Ollama tests)

### When Stopping (Ctrl+C or exit):
1. Stop Frontend
2. Stop Actions server
3. Stop Rasa server
4. **Stop Ollama (if started by script)** ← NEW
5. Clean up logs and processes

## Benefits

### ✅ **Complete Automation**
- No manual Ollama management required
- Automatic model installation if missing
- Intelligent detection of existing Ollama instances

### ✅ **Safe Process Management**
- Won't interfere with existing Ollama instances
- Graceful cleanup on script termination
- Multiple fallback cleanup methods

### ✅ **Comprehensive Testing**
- Validates LLM service availability
- Tests model accessibility
- Includes in overall system health checks

### ✅ **User-Friendly**
- Clear status messages and progress indicators
- Helpful installation guidance
- Enhanced service status display

## Usage Examples

### Start Everything (including Ollama):
```bash
./start_and_test.sh --full
```

### Interactive Mode:
```bash
./start_and_test.sh
# Choose option 1, 2, 3, or 4 - all include Ollama
```

### Check Service Status:
```bash
./start_and_test.sh
# Choose option 6 to see all services including Ollama
```

## Technical Details

### Ollama Process Detection:
```bash
pgrep -f "ollama serve" > /dev/null
```

### Health Check:
```bash
curl -s http://localhost:11434/api/tags > /dev/null
```

### Model Verification:
```bash
ollama list | grep -q "llama3.2:1b"
```

### Cleanup Strategy:
```bash
# Primary: Kill tracked PID
kill $OLLAMA_PID 2>/dev/null

# Secondary: Stop via Ollama command
ollama stop llama3.2:1b 2>/dev/null

# Fallback: Force kill process
pkill -f "ollama serve" 2>/dev/null
```

## Error Handling

- **Ollama not installed**: Graceful degradation with warning
- **Model not available**: Automatic installation attempt
- **Service start failure**: Continues with warnings
- **Cleanup failure**: Multiple fallback methods

The script now provides complete end-to-end management of the entire chatbot ecosystem including the local LLM fallback system.
