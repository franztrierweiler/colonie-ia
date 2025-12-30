# Colonie-IA Development Makefile

.PHONY: help install dev backend frontend docker-up docker-down docker-build docker-logs rebuild rebuild-all test lint clean db-init db-migrate db-upgrade

# Default target
help:
	@echo "Colonie-IA Development Commands"
	@echo ""
	@echo "  make install        - Install all dependencies"
	@echo "  make dev            - Start development servers (backend + frontend)"
	@echo "  make backend        - Start backend only (local)"
	@echo "  make frontend       - Start frontend only (local)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up      - Start all services with Docker"
	@echo "  make docker-down    - Stop Docker services"
	@echo "  make docker-logs    - Follow Docker logs"
	@echo "  make rebuild        - Rebuild and restart backend"
	@echo "  make rebuild-all    - Rebuild and restart all services"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate msg='description'      - Create new migration (local)"
	@echo "  make db-upgrade                        - Apply migrations (local)"
	@echo "  make docker-db-migrate msg='desc'      - Create migration (Docker)"
	@echo "  make docker-db-upgrade                 - Apply migrations (Docker)"
	@echo ""
	@echo "  make test           - Run all tests"
	@echo "  make lint           - Run linters"
	@echo "  make clean          - Clean generated files"

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Development servers
dev:
	@echo "Starting development servers..."
	$(MAKE) -j2 backend frontend

backend:
	@echo "Starting Flask backend..."
	cd backend && FLASK_ENV=development python run.py

frontend:
	@echo "Starting React frontend..."
	cd frontend && npm run dev

# Docker commands (V2 syntax: "docker compose" sans tiret)
docker-up:
	@echo "Starting Docker services..."
	docker compose up -d

docker-down:
	@echo "Stopping Docker services..."
	docker compose down

docker-logs:
	docker compose logs -f

docker-build:
	docker compose build

# Rebuild and restart backend
rebuild:
	@echo "Rebuilding and restarting backend..."
	docker compose build backend
	docker compose up -d backend
	@echo "Waiting for backend to start..."
	@sleep 3
	docker compose logs backend --tail 20

rebuild-all:
	@echo "Rebuilding all services..."
	docker compose build
	docker compose up -d
	@echo "Waiting for services to start..."
	@sleep 3
	docker compose logs --tail 20

# Testing
test:
	@echo "Running backend tests..."
	cd backend && python -m pytest -v
	@echo "Running frontend tests..."
	cd frontend && npm test

test-backend:
	cd backend && python -m pytest -v --cov=app

test-frontend:
	cd frontend && npm test

# Database migrations (local)
db-init:
	cd backend && flask db init

db-migrate:
	cd backend && flask db migrate -m "$(msg)"

db-upgrade:
	cd backend && flask db upgrade

db-downgrade:
	cd backend && flask db downgrade

# Database migrations (Docker)
docker-db-migrate:
	docker compose exec backend flask db migrate -m "$(msg)"

docker-db-upgrade:
	docker compose exec backend flask db upgrade

docker-db-downgrade:
	docker compose exec backend flask db downgrade

docker-shell:
	docker compose exec backend bash

# Linting
lint:
	@echo "Linting backend..."
	cd backend && python -m flake8 app/
	@echo "Linting frontend..."
	cd frontend && npm run lint

# Clean
clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/colonie_dev.db 2>/dev/null || true
	rm -rf frontend/dist 2>/dev/null || true
