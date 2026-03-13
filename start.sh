#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping all services..."
    # Kill all child processes in the current process group
    trap - SIGINT SIGTERM # Disable the trap to avoid recursion
    kill -- -$$ # Kill the process group
    exit
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# Function to check and kill process on a port
clear_port() {
    local port=$1
    local pid=$(lsof -t -i:$port)
    if [ ! -z "$pid" ]; then
        echo "Cleaning up port $port (PID: $pid)..."
        kill -9 $pid 2>/dev/null
    fi
}

echo "==============================================="
echo "   Starting Hybrid NLP-Expert Agent System"
echo "==============================================="

# Cleanup old processes
clear_port 8001
clear_port 5173
clear_port 3000

# Start Backend
echo "[1/3] Starting Backend (Expert_Agent)..."
cd Expert_Agent
# Check if python3 exists, else use python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

# Ensure dependencies are installed
if [ ! -f ".deps_installed" ]; then
    echo "-> Installing backend dependencies..."
    pip install -r requirements.txt > /dev/null 2>&1
    touch .deps_installed
fi

$PYTHON_CMD api_hybrid.py &
BACKEND_PID=$!
echo "-> Backend running on PID: $BACKEND_PID (Port: 8001)"
cd ..

# Wait a moment for backend to initialize
sleep 2

# Start Chatbot Frontend
echo "[2/3] Starting Chatbot Frontend..."
cd chatbot-frontend
if [ ! -d "node_modules" ]; then
    echo "-> Installing chatbot dependencies (npm install)..."
    npm install > /dev/null 2>&1
fi
npm run dev &
CHATBOT_PID=$!
echo "-> Chatbot running on PID: $CHATBOT_PID (Port: 5173)"
cd ..

# Start Admin Frontend
echo "[3/3] Starting Admin Frontend (Next.js)..."
cd admin-frontend
if [ ! -d "node_modules" ]; then
    echo "-> Installing admin dependencies (npm install)..."
    npm install > /dev/null 2>&1
fi
npm run dev &
ADMIN_PID=$!
echo "-> Admin UI running on PID: $ADMIN_PID (Port: 3000)"
cd ..

echo "==============================================="
echo "   All systems nominal."
echo "   Backend: localhost:8001"
echo "   Chatbot UI: localhost:5173"
echo "   Admin Console: localhost:3000"
echo "   Press Ctrl+C to stop."
echo "==============================================="

# Keep script running to maintain the trap
wait


