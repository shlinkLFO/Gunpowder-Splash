#!/bin/bash

# Gunpowder Splash Setup Verification Script
# Checks that all prerequisites and dependencies are properly installed

echo "======================================"
echo "Gunpowder Splash - Setup Verification"
echo "======================================"
echo ""

ERRORS=0
WARNINGS=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        if [ ! -z "$2" ]; then
            VERSION=$($1 $2 2>&1 | head -n 1)
            echo "  Version: $VERSION"
        fi
        return 0
    else
        echo -e "${RED}✗${NC} $1 is NOT installed"
        ((ERRORS++))
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 NOT found"
        ((ERRORS++))
        return 1
    fi
}

check_directory() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 directory exists"
        return 0
    else
        echo -e "${YELLOW}!${NC} $1 directory NOT found (will be created)"
        ((WARNINGS++))
        return 1
    fi
}

# Check Python
echo "Checking Python..."
if check_command python3 "--version"; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    REQUIRED_VERSION="3.11"
    if (( $(echo "$PYTHON_VERSION >= $REQUIRED_VERSION" | bc -l) )); then
        echo -e "${GREEN}✓${NC} Python version is sufficient ($PYTHON_VERSION >= $REQUIRED_VERSION)"
    else
        echo -e "${RED}✗${NC} Python version too old ($PYTHON_VERSION < $REQUIRED_VERSION)"
        ((ERRORS++))
    fi
fi
echo ""

# Check Node.js
echo "Checking Node.js..."
if check_command node "--version"; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -ge 20 ]; then
        echo -e "${GREEN}✓${NC} Node.js version is sufficient (>= 20)"
    else
        echo -e "${RED}✗${NC} Node.js version too old (< 20)"
        ((ERRORS++))
    fi
fi
echo ""

# Check npm
echo "Checking npm..."
check_command npm "--version"
echo ""

# Check pip
echo "Checking pip..."
check_command pip3 "--version"
echo ""

# Optional: Docker
echo "Checking Docker (optional)..."
if check_command docker "--version"; then
    check_command docker-compose "--version"
else
    echo -e "${YELLOW}!${NC} Docker not found (optional, but recommended)"
    ((WARNINGS++))
fi
echo ""

# Check project structure
echo "Checking project structure..."
check_directory "backend"
check_directory "backend/app"
check_directory "frontend"
check_directory "frontend/src"
echo ""

# Check configuration files
echo "Checking configuration files..."
check_file "backend/requirements.txt"
check_file "frontend/package.json"
check_file "frontend/vite.config.ts"
check_file "websocket_server.py"
check_file "start-dev.sh"
check_file "docker-compose.yml"
echo ""

# Check if dependencies are installed
echo "Checking installed dependencies..."

# Backend dependencies
if [ -d "backend/venv" ]; then
    echo -e "${GREEN}✓${NC} Python virtual environment exists"
else
    echo -e "${YELLOW}!${NC} Python virtual environment not found"
    echo "  Run: cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    ((WARNINGS++))
fi

# Frontend dependencies
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓${NC} Node modules are installed"
else
    echo -e "${YELLOW}!${NC} Node modules not found"
    echo "  Run: cd frontend && npm install"
    ((WARNINGS++))
fi
echo ""

# Check ports availability
echo "Checking port availability..."
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}!${NC} Port $1 is in use"
        echo "  Process using port: $(lsof -Pi :$1 -sTCP:LISTEN | tail -n 1)"
        ((WARNINGS++))
        return 1
    else
        echo -e "${GREEN}✓${NC} Port $1 is available"
        return 0
    fi
}

check_port 8000  # Backend
check_port 8001  # WebSocket
check_port 5173  # Frontend
echo ""

# Summary
echo "======================================"
echo "Summary"
echo "======================================"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    echo "You're ready to run Gunpowder Splash."
    echo ""
    echo "To start the application, run:"
    echo "  ./start-dev.sh"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}Setup complete with $WARNINGS warning(s)${NC}"
    echo "You should be able to run the application, but check the warnings above."
    exit 0
else
    echo -e "${RED}Setup incomplete: $ERRORS error(s), $WARNINGS warning(s)${NC}"
    echo "Please fix the errors above before running the application."
    exit 1
fi

