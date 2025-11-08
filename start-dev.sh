#!/bin/bash

# Gunpowder Splash Development Startup Script
# Starts all required services for local development

echo "Starting Gunpowder Splash Development Environment..."
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if Node is available
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Create workspace directory
mkdir -p backend/workspace

# Function to kill background processes on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend API
echo -e "${GREEN}[1/2] Starting Backend API (port 8000)...${NC}"
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..
sleep 2

# Start Frontend
echo -e "${GREEN}[2/2] Starting Frontend (port 5173)...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================="
echo -e "${GREEN}All services started successfully!${NC}"
echo ""
echo "Access the application at:"
echo "  Frontend:  http://localhost:5173"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=========================================="

# Wait for all background processes
wait

