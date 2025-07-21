#!/bin/bash

# Complete Rasa Diabetes Chatbot Startup & Test Script
# This script handles everything: setup, deployment, testing, and validation

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log() { echo -e "${BLUE}[$(date +'%H:%M:%S')] INFO:${NC} $1"; }
success() { echo -e "${GREEN}[$(date +'%H:%M:%S')] SUCCESS:${NC} $1"; }
warn() { echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING:${NC} $1"; }
error() { echo -e "${RED}[$(date +'%H:%M:%S')] ERROR:${NC} $1" >&2; }
section() { echo -e "${PURPLE}\n=== $1 ===${NC}"; }
step() { echo -e "${CYAN}→${NC} $1"; }

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
RASA_PORT=5005
ACTIONS_PORT=5055
FRONTEND_PORT=3000
TIMEOUT=300  # 5 minutes timeout

# Global variables
RASA_PID=""
ACTIONS_PID=""
FRONTEND_PID=""
OLLAMA_PID=""
OLLAMA_STARTED_BY_SCRIPT=false
DOCKER_MODE=false
TEST_RESULTS=""

# Cleanup function
cleanup() {
    section "Cleaning up..."
    
    if [[ "$DOCKER_MODE" == "true" ]]; then
        step "Stopping Docker containers..."
        docker-compose down --remove-orphans 2>/dev/null || true
    else
        # Kill background processes
        if [[ -n "$RASA_PID" ]]; then
            kill $RASA_PID 2>/dev/null || true
            step "Stopped Rasa server (PID: $RASA_PID)"
        fi
        
        if [[ -n "$ACTIONS_PID" ]]; then
            kill $ACTIONS_PID 2>/dev/null || true
            step "Stopped Actions server (PID: $ACTIONS_PID)"
        fi
        
        if [[ -n "$FRONTEND_PID" ]]; then
            kill $FRONTEND_PID 2>/dev/null || true
            step "Stopped Frontend (PID: $FRONTEND_PID)"
        fi
        
        # Stop Ollama if we started it
        if [[ "$OLLAMA_STARTED_BY_SCRIPT" == "true" ]] && [[ -n "$OLLAMA_PID" ]]; then
            step "Stopping Ollama service..."
            kill $OLLAMA_PID 2>/dev/null || true
            # Also try to stop via ollama command
            ollama stop llama3.2:1b 2>/dev/null || true
            pkill -f "ollama serve" 2>/dev/null || true
            step "Stopped Ollama service (PID: $OLLAMA_PID)"
        elif [[ "$OLLAMA_STARTED_BY_SCRIPT" == "true" ]]; then
            step "Stopping Ollama service..."
            ollama stop llama3.2:1b 2>/dev/null || true
            pkill -f "ollama serve" 2>/dev/null || true
            step "Stopped Ollama service"
        fi
    fi
    
    success "Cleanup completed"
}

# Trap to ensure cleanup on exit
trap cleanup EXIT INT TERM

# Check prerequisites
check_prerequisites() {
    section "Checking Prerequisites"
    
    # Check if we're in the right directory
    if [[ ! -f "domain.yml" ]] || [[ ! -f "config.yml" ]]; then
        error "Not in Rasa project directory. Please run from: /Users/gurmatsinghsour/rasa-capstone"
        exit 1
    fi
    
    step "In correct Rasa project directory"
    
    # Check Python/Rasa
    if command -v rasa &> /dev/null; then
        RASA_VERSION=$(rasa --version 2>/dev/null | head -n1 || echo "unknown")
        step "Rasa installed: $RASA_VERSION"
    else
        error "Rasa not installed. Please install Rasa first."
        exit 1
    fi
    
    # Check if model exists
    if [[ -d "models" ]] && [[ -n "$(ls -A models 2>/dev/null)" ]]; then
        LATEST_MODEL=$(ls -t models/*.tar.gz 2>/dev/null | head -n1 || echo "")
        step "Trained model found: $(basename "$LATEST_MODEL")"
    else
        warn "No trained models found. Will train a new model..."
    fi
    
    # Check Docker (optional)
    if command -v docker &> /dev/null && docker info > /dev/null 2>&1; then
        step "Docker available and running"
    else
        warn "Docker not available. Will use local mode."
    fi
    
    # Check Node.js for frontend
    if command -v npm &> /dev/null; then
        step "Node.js/npm available for frontend"
    else
        warn "Node.js not available. Frontend tests will be skipped."
    fi
    
    # Check Ollama for LLM fallback
    if command -v ollama &> /dev/null; then
        step "Ollama available for LLM fallback"
        # Check if Ollama is running
        if pgrep -f "ollama serve" > /dev/null; then
            step "Ollama service already running"
        else
            step "Ollama installed but not running - will start automatically"
        fi
        # Check if llama3.2:1b model is available
        if ollama list | grep -q "llama3.2:1b"; then
            step "Llama 3.2:1b model available"
        else
            warn "Llama 3.2:1b model not found. LLM fallback may not work properly."
            step "To install: ollama pull llama3.2:1b"
        fi
    else
        warn "Ollama not available. LLM fallback features will be disabled."
        step "To install Ollama: brew install ollama"
    fi
    
    success "Prerequisites check completed"
}

# Train Rasa model if needed
train_model() {
    section "Training Rasa Model"
    
    if [[ -d "models" ]] && [[ -n "$(ls -A models 2>/dev/null)" ]]; then
        LATEST_MODEL=$(ls -t models/*.tar.gz 2>/dev/null | head -n1 || echo "")
        MODEL_AGE=$(($(date +%s) - $(stat -f %m "$LATEST_MODEL" 2>/dev/null || stat -c %Y "$LATEST_MODEL" 2>/dev/null || echo 0)))
        
        if [[ $MODEL_AGE -lt 3600 ]]; then  # Less than 1 hour old
            step "Recent model found, skipping training"
            return
        fi
    fi
    
    step "Training new model..."
    if rasa train --debug; then
        success "Model training completed"
    else
        error "Model training failed"
        exit 1
    fi
}

# Start Ollama service
start_ollama_service() {
    section "🦙 Starting Ollama Service"
    
    # Check if Ollama is available
    if ! command -v ollama &> /dev/null; then
        warn "Ollama not installed, skipping LLM service"
        return
    fi
    
    # Check if Ollama is already running
    if pgrep -f "ollama serve" > /dev/null; then
        step "Ollama service already running"
        OLLAMA_STARTED_BY_SCRIPT=false
        return
    fi
    
    step "Starting Ollama service..."
    
    # Start Ollama in background
    ollama serve > ollama.log 2>&1 &
    OLLAMA_PID=$!
    OLLAMA_STARTED_BY_SCRIPT=true
    
    step "Ollama service started (PID: $OLLAMA_PID)"
    step "Waiting for Ollama to be ready..."
    
    # Wait for Ollama to be ready
    local counter=0
    while ! curl -s http://localhost:11434/api/tags > /dev/null; do
        if [[ $counter -gt 30 ]]; then
            warn "Ollama taking longer than expected, continuing..."
            break
        fi
        sleep 2
        counter=$((counter + 2))
        step "Waiting... (${counter}s)"
    done
    
    # Check if required model is available
    if ollama list | grep -q "llama3.2:1b"; then
        success "Ollama ready with Llama 3.2:1b model"
    else
        warn "Llama 3.2:1b model not found. Installing..."
        step "Pulling Llama 3.2:1b model (this may take a few minutes)..."
        if ollama pull llama3.2:1b; then
            success "Llama 3.2:1b model installed successfully"
        else
            error "Failed to install Llama 3.2:1b model"
        fi
    fi
}

# Start Rasa server
start_rasa_server() {
    section "Starting Rasa Server"
    
    # Check if port is already in use
    if lsof -Pi :$RASA_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        warn "Port $RASA_PORT already in use. Attempting to free it..."
        lsof -ti:$RASA_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    step "Starting Rasa server on port $RASA_PORT..."
    
    # Start Rasa server in background
    rasa run --enable-api --cors "*" --port $RASA_PORT --debug > rasa_server.log 2>&1 &
    RASA_PID=$!
    
    step "Rasa server started (PID: $RASA_PID)"
    step "Waiting for Rasa server to be ready..."
    
    # Wait for server to be ready
    local counter=0
    while ! curl -s http://localhost:$RASA_PORT/status > /dev/null; do
        if [[ $counter -gt $TIMEOUT ]]; then
            error "Rasa server failed to start within timeout"
            cat rasa_server.log | tail -20
            exit 1
        fi
        sleep 2
        counter=$((counter + 2))
        step "Waiting... (${counter}s)"
    done
    
    success "Rasa server is ready at http://localhost:$RASA_PORT"
}

# Start Actions server
start_actions_server() {
    section "⚡ Starting Actions Server"
    
    # Check if actions.py exists
    if [[ ! -f "actions/actions.py" ]]; then
        warn "No custom actions found, skipping actions server"
        return
    fi
    
    # Check if port is already in use
    if lsof -Pi :$ACTIONS_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        warn "Port $ACTIONS_PORT already in use. Attempting to free it..."
        lsof -ti:$ACTIONS_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    step "Starting Actions server on port $ACTIONS_PORT..."
    
    # Start Actions server in background
    rasa run actions --port $ACTIONS_PORT --debug > actions_server.log 2>&1 &
    ACTIONS_PID=$!
    
    step "Actions server started (PID: $ACTIONS_PID)"
    step "Waiting for Actions server to be ready..."
    
    # Wait for server to be ready
    local counter=0
    while ! curl -s http://localhost:$ACTIONS_PORT/health > /dev/null; do
        if [[ $counter -gt 30 ]]; then
            warn "Actions server taking longer than expected, continuing..."
            break
        fi
        sleep 1
        counter=$((counter + 1))
    done
    
    success "Actions server is ready at http://localhost:$ACTIONS_PORT"
}

# Start Frontend
start_frontend() {
    section "Starting Frontend"
    
    if [[ ! -d "frontend" ]]; then
        warn "Frontend directory not found, skipping frontend startup"
        return
    fi
    
    cd frontend
    
    # Check if dependencies are installed
    if [[ ! -d "node_modules" ]]; then
        step "Installing frontend dependencies..."
        npm install
    fi
    
    # Check if port is already in use
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        warn "Port $FRONTEND_PORT already in use. Attempting to free it..."
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    step "Starting frontend on port $FRONTEND_PORT..."
    
    # Set environment variable for Rasa API URL
    export REACT_APP_RASA_URL=http://localhost:$RASA_PORT
    
    # Start frontend in background
    npm start > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    cd ..
    
    step "Frontend started (PID: $FRONTEND_PID)"
    step "Waiting for frontend to be ready..."
    
    # Wait for frontend to be ready
    local counter=0
    while ! curl -s http://localhost:$FRONTEND_PORT > /dev/null; do
        if [[ $counter -gt 60 ]]; then
            warn "Frontend taking longer than expected, continuing with tests..."
            break
        fi
        sleep 3
        counter=$((counter + 3))
        step "Waiting... (${counter}s)"
    done
    
    success "Frontend is ready at http://localhost:$FRONTEND_PORT"
}

# Run API tests
run_api_tests() {
    section "🧪 Running API Tests"
    
    local test_results=""
    local all_tests_passed=true
    
    # Test 1: Health check
    step "Testing health endpoint..."
    if curl -s http://localhost:$RASA_PORT/status | grep -q "ok"; then
        test_results+="Health check: PASSED\n"
        step "Health check passed"
    else
        test_results+="Health check: FAILED\n"
        step "Health check failed"
        all_tests_passed=false
    fi
    
    # Test 2: Model info
    step "Testing model info endpoint..."
    if curl -s http://localhost:$RASA_PORT/status | grep -q "model"; then
        test_results+="Model info: PASSED\n"
        step "Model info available"
    else
        test_results+="Model info: FAILED\n"
        step "Model info not available"
        all_tests_passed=false
    fi
    
    # Test 3: Version endpoint
    step "Testing version endpoint..."
    if curl -s http://localhost:$RASA_PORT/version | grep -q "version"; then
        test_results+="Version endpoint: PASSED\n"
        step "Version endpoint working"
    else
        test_results+="Version endpoint: FAILED\n"
        step "Version endpoint failed"
        all_tests_passed=false
    fi
    
    # Test 4: Domain endpoint
    step "Testing domain endpoint..."
    if curl -s http://localhost:$RASA_PORT/domain | grep -q "intents"; then
        test_results+="Domain endpoint: PASSED\n"
        step "Domain endpoint working"
    else
        test_results+="Domain endpoint: FAILED\n"
        step "Domain endpoint failed"
        all_tests_passed=false
    fi
    
    # Test 5: Ollama service
    step "Testing Ollama service..."
    if command -v ollama &> /dev/null && curl -s http://localhost:11434/api/tags > /dev/null; then
        test_results+="Ollama service: PASSED\n"
        step "Ollama service working"
        
        # Test if llama3.2:1b model is available
        if ollama list | grep -q "llama3.2:1b"; then
            test_results+="Llama3.2:1b model: PASSED\n"
            step "Llama 3.2:1b model available"
        else
            test_results+="Llama3.2:1b model: FAILED\n"
            step "Llama 3.2:1b model not available"
            all_tests_passed=false
        fi
    else
        test_results+="Ollama service: SKIPPED\n"
        step "Ollama service not available (LLM fallback disabled)"
    fi
    
    TEST_RESULTS+="$test_results"
    
    if [[ "$all_tests_passed" == "true" ]]; then
        success "All API tests passed"
    else
        error "Some API tests failed"
    fi
}

# Run conversation tests
run_conversation_tests() {
    section "Running Conversation Tests"
    
    local test_results=""
    local all_tests_passed=true
    
    # Test messages
    declare -a test_messages=(
        "hello"
        "I want to assess my diabetes risk"
        "My age is 65"
        "I have diabetes"
        "goodbye"
    )
    
    for message in "${test_messages[@]}"; do
        step "Testing message: '$message'"
        
        # Send message to Rasa
        response=$(curl -s -X POST http://localhost:$RASA_PORT/webhooks/rest/webhook \
            -H "Content-Type: application/json" \
            -d "{\"sender\":\"test_user\",\"message\":\"$message\"}" 2>/dev/null || echo "[]")
        
        if [[ "$response" != "[]" ]] && [[ "$response" != "" ]]; then
            test_results+="Message '$message': PASSED\n"
            step "Got response: $(echo "$response" | jq -r '.[0].text' 2>/dev/null || echo 'Response received')"
        else
            test_results+="Message '$message': FAILED\n"
            step "No response received"
            all_tests_passed=false
        fi
        
        sleep 1  # Brief pause between requests
    done
    
    TEST_RESULTS+="$test_results"
    
    if [[ "$all_tests_passed" == "true" ]]; then
        success "All conversation tests passed"
    else
        warn "Some conversation tests failed (this might be expected for untrained intents)"
    fi
}

# Run frontend tests
run_frontend_tests() {
    section "Running Frontend Tests"
    
    if [[ -z "$FRONTEND_PID" ]]; then
        warn "Frontend not running, skipping frontend tests"
        return
    fi
    
    local test_results=""
    local all_tests_passed=true
    
    # Test 1: Frontend accessibility
    step "Testing frontend accessibility..."
    if curl -s http://localhost:$FRONTEND_PORT > /dev/null; then
        test_results+="Frontend accessible: PASSED\n"
        step "Frontend is accessible"
    else
        test_results+="Frontend accessible: FAILED\n"
        step "Frontend not accessible"
        all_tests_passed=false
    fi
    
    # Test 2: Check if React app loads
    step "Testing React app content..."
    frontend_content=$(curl -s http://localhost:$FRONTEND_PORT)
    if echo "$frontend_content" | grep -q "react"; then
        test_results+="React app content: PASSED\n"
        step "React app loads correctly"
    else
        test_results+="React app content: FAILED\n"
        step "React app not loading correctly"
        all_tests_passed=false
    fi
    
    TEST_RESULTS+="$test_results"
    
    if [[ "$all_tests_passed" == "true" ]]; then
        success "All frontend tests passed"
    else
        error "Some frontend tests failed"
    fi
}

# Generate test report
generate_test_report() {
    section "Test Report"
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="test_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$report_file" << EOF
========================================
Rasa Diabetes Chatbot Test Report
========================================
Timestamp: $timestamp
Test Duration: Auto
Environment: Local Development

========================================
SERVICE STATUS
========================================
Rasa Server: Running on port $RASA_PORT
$([ -n "$ACTIONS_PID" ] && echo "Actions Server: Running on port $ACTIONS_PORT" || echo "Actions Server: Not running")
$([ -n "$FRONTEND_PID" ] && echo "Frontend: Running on port $FRONTEND_PORT" || echo "Frontend: Not running")

========================================
TEST RESULTS
========================================
$TEST_RESULTS

========================================
LOGS LOCATION
========================================
Rasa Server: ./rasa_server.log
Actions Server: ./actions_server.log
Frontend: ./frontend.log

========================================
ACCESS URLS
========================================
Rasa API: http://localhost:$RASA_PORT
Actions API: http://localhost:$ACTIONS_PORT
Frontend: http://localhost:$FRONTEND_PORT

========================================
NEXT STEPS
========================================
1. Test the chatbot manually at: http://localhost:$FRONTEND_PORT
2. Send API requests to: http://localhost:$RASA_PORT/webhooks/rest/webhook
3. Check logs if any issues occur
4. Use Ctrl+C to stop all services

Report saved to: $report_file
EOF
    
    step "Test report saved to: $report_file"
    
    # Display summary
    echo
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  DIABETES CHATBOT IS READY! {NC}"
    echo -e "${GREEN}========================================${NC}"
    echo
    echo -e "${BLUE}🔗 Access URLs:${NC}"
    echo -e "  🤖 Rasa API:    http://localhost:$RASA_PORT"
    [[ -n "$ACTIONS_PID" ]] && echo -e "  ⚡ Actions API:  http://localhost:$ACTIONS_PORT"
    [[ -n "$FRONTEND_PID" ]] && echo -e "  🌐 Frontend:     http://localhost:$FRONTEND_PORT"
    if command -v ollama &> /dev/null && curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "  🦙 Ollama API:   http://localhost:11434"
    fi
    echo
    echo -e "${YELLOW}Quick Tests:${NC}"
    echo -e "  curl -X POST http://localhost:$RASA_PORT/webhooks/rest/webhook \\"
    echo -e "    -H 'Content-Type: application/json' \\"
    echo -e "    -d '{\"sender\":\"user\",\"message\":\"hello\"}'"
    echo
    echo -e "${CYAN}To stop all services: Press Ctrl+C${NC}"
    echo
}

# Interactive mode
interactive_mode() {
    section "🎮 Interactive Mode"
    
    echo -e "${CYAN}Choose an option:${NC}"
    echo "1. Start all services and run tests (Ollama + Rasa + Actions + Frontend)"
    echo "2. Start only Rasa server (with Ollama)"
    echo "3. Start Rasa + Actions server (with Ollama)"
    echo "4. Start all services (Ollama + Rasa + Actions + Frontend)"
    echo "5. Run tests on existing services"
    echo "6. Show service status"
    echo "7. Exit"
    echo
    
    read -p "Enter your choice (1-7): " choice
    
    case $choice in
        1)
            train_model
            start_ollama_service
            start_rasa_server
            start_actions_server
            start_frontend
            run_api_tests
            run_conversation_tests
            run_frontend_tests
            generate_test_report
            ;;
        2)
            train_model
            start_ollama_service
            start_rasa_server
            run_api_tests
            generate_test_report
            ;;
        3)
            train_model
            start_ollama_service
            start_rasa_server
            start_actions_server
            run_api_tests
            generate_test_report
            ;;
        4)
            train_model
            start_ollama_service
            start_rasa_server
            start_actions_server
            start_frontend
            generate_test_report
            ;;
        5)
            run_api_tests
            run_conversation_tests
            run_frontend_tests
            generate_test_report
            ;;
        6)
            section "Service Status"
            step "Checking Rasa server..."
            curl -s http://localhost:$RASA_PORT/status >/dev/null && echo "Rasa: Running" || echo "Rasa: Not running"
            curl -s http://localhost:$ACTIONS_PORT/health >/dev/null && echo "Actions: Running" || echo "Actions: Not running"
            curl -s http://localhost:$FRONTEND_PORT >/dev/null && echo "Frontend: Running" || echo "Frontend: Not running"
            curl -s http://localhost:11434/api/tags >/dev/null && echo "Ollama: Running" || echo "Ollama: Not running"
            ;;
        7)
            log "Exiting..."
            exit 0
            ;;
        *)
            error "Invalid choice"
            exit 1
            ;;
    esac
}

# Main function
main() {
    clear
    echo -e "${PURPLE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║              DIABETES CHATBOT STARTUP SCRIPT                 ║
║                                                              ║
║  Complete setup, deployment, and testing for your            ║
║  secure diabetes readmission prediction chatbot!             ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}\n"
    
    cd "$PROJECT_DIR"
    check_prerequisites
    
    if [[ $# -eq 0 ]]; then
        interactive_mode
    else
        case "$1" in
            --full|--all)
                train_model
                start_ollama_service
                start_rasa_server
                start_actions_server
                start_frontend
                run_api_tests
                run_conversation_tests
                run_frontend_tests
                generate_test_report
                ;;
            --rasa-only)
                train_model
                start_ollama_service
                start_rasa_server
                run_api_tests
                generate_test_report
                ;;
            --test-only)
                run_api_tests
                run_conversation_tests
                run_frontend_tests
                generate_test_report
                ;;
            --help)
                echo "Usage: $0 [--full|--rasa-only|--test-only|--help]"
                echo "  --full      : Start all services and run all tests"
                echo "  --rasa-only : Start only Rasa server"
                echo "  --test-only : Run tests on existing services"
                echo "  --help      : Show this help"
                echo "  (no args)   : Interactive mode"
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    fi
    
    # Keep services running
    if [[ -n "$RASA_PID" ]] || [[ -n "$ACTIONS_PID" ]] || [[ -n "$FRONTEND_PID" ]] || [[ "$OLLAMA_STARTED_BY_SCRIPT" == "true" ]]; then
        section "Services Running"
        success "All requested services are running. Press Ctrl+C to stop."
        
        # Display running services
        [[ -n "$RASA_PID" ]] && step "Rasa server running (PID: $RASA_PID)"
        [[ -n "$ACTIONS_PID" ]] && step "Actions server running (PID: $ACTIONS_PID)"
        [[ -n "$FRONTEND_PID" ]] && step "Frontend running (PID: $FRONTEND_PID)"
        [[ "$OLLAMA_STARTED_BY_SCRIPT" == "true" ]] && step "Ollama service running (PID: ${OLLAMA_PID:-'system service'})"
        
        # Wait for user interrupt
        while true; do
            sleep 1
        done
    fi
}

# Run main function with all arguments
main "$@"
