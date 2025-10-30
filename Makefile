.PHONY: help install dev clean build test docker-up docker-down

help:
	@echo "Gunpowder Splash - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make install     - Install all dependencies"
	@echo "  make dev         - Start development servers"
	@echo "  make build       - Build for production"
	@echo "  make clean       - Clean build artifacts"
	@echo "  make docker-up   - Start with Docker Compose"
	@echo "  make docker-down - Stop Docker containers"
	@echo "  make test        - Run tests"

install:
	@echo "Installing backend dependencies..."
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Installation complete!"

dev:
	@echo "Starting development environment..."
	./start-dev.sh

build:
	@echo "Building frontend..."
	cd frontend && npm run build
	@echo "Build complete! Frontend is in frontend/dist/"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf backend/__pycache__
	rm -rf backend/app/__pycache__
	rm -rf backend/venv
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	@echo "Clean complete!"

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up --build

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

test:
	@echo "Running tests..."
	@echo "Tests not yet implemented"

