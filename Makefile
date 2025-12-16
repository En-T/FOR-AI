.PHONY: help build up down logs clean test lint format migrate createsuperuser

# Default target
help:
	@echo "Available commands:"
	@echo "  build        - Build all Docker images"
	@echo "  up           - Start all services"
	@echo "  down         - Stop all services"
	@echo "  logs         - Show logs from all services"
	@echo "  restart      - Restart all services"
	@echo "  clean        - Clean up containers and images"
	@echo "  test         - Run tests for all services"
	@echo "  test-auth    - Run tests for auth service only"
	@echo "  test-admin   - Run tests for admin service only"
	@echo "  test-edu     - Run tests for education service only"
	@echo "  lint         - Run linting on all services"
	@echo "  format       - Format code with black and isort"
	@echo "  migrate      - Run migrations for all services"
	@echo "  superuser    - Create superusers for all services"
	@echo "  health       - Check health of all services"

build:
	docker compose build

up:
	docker compose up --build

up-detached:
	docker compose up --build -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

logs-auth:
	docker compose logs -f auth_service

logs-admin:
	docker compose logs -f admin_service

logs-edu:
	docker compose logs -f education_service

clean:
	docker compose down -v
	docker system prune -f

test:
	docker compose exec auth_service python manage.py test || true
	docker compose exec admin_service python manage.py test || true
	docker compose exec education_service python manage.py test || true

test-auth:
	docker compose exec auth_service python manage.py test

test-admin:
	docker compose exec admin_service python manage.py test

test-edu:
	docker compose exec education_service python manage.py test

lint:
	docker compose exec auth_service flake8 . || true
	docker compose exec admin_service flake8 . || true
	docker compose exec education_service flake8 . || true

format:
	docker compose exec auth_service black . || true
	docker compose exec admin_service black . || true
	docker compose exec education_service black . || true
	docker compose exec auth_service isort . || true
	docker compose exec admin_service isort . || true
	docker compose exec education_service isort . || true

migrate:
	docker compose exec auth_service python manage.py migrate || true
	docker compose exec admin_service python manage.py migrate || true
	docker compose exec education_service python manage.py migrate || true

makemigrations:
	docker compose exec auth_service python manage.py makemigrations || true
	docker compose exec admin_service python manage.py makemigrations || true
	docker compose exec education_service python manage.py makemigrations || true

superuser:
	docker compose exec auth_service python manage.py createsuperuser || true
	docker compose exec admin_service python manage.py createsuperuser || true
	docker compose exec education_service python manage.py createsuperuser || true

health:
	@echo "Checking service health..."
	@curl -s http://localhost:8001/health/ | python -m json.tool || echo "Auth service not responding"
	@curl -s http://localhost:8002/health/ | python -m json.tool || echo "Admin service not responding"
	@curl -s http://localhost:8003/health/ | python -m json.tool || echo "Education service not responding"
	@echo "Redis ping:"
	@docker compose exec redis redis-cli ping || echo "Redis not responding"

# Development shortcuts
dev-setup: up-detached
	@echo "Waiting for services to start..."
	@sleep 10
	@make migrate
	@make superuser
	@echo "Development environment ready!"

shell-auth:
	docker compose exec auth_service bash

shell-admin:
	docker compose exec admin_service bash

shell-edu:
	docker compose exec education_service bash