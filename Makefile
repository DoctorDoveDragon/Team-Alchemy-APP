.PHONY: help install install-dev test lint format clean run docker-up docker-down migrate

help:
	@echo "Team Alchemy - Makefile commands"
	@echo "=================================="
	@echo "install        - Install production dependencies"
	@echo "install-dev    - Install development dependencies"
	@echo "test           - Run tests with coverage"
	@echo "lint           - Run linters (flake8, mypy, pylint)"
	@echo "format         - Format code with black and isort"
	@echo "clean          - Remove build artifacts and cache"
	@echo "run            - Run the development server"
	@echo "docker-up      - Start Docker containers"
	@echo "docker-down    - Stop Docker containers"
	@echo "init-db        - Initialize database"
	@echo "migrate        - Run database migrations"
	@echo "migration      - Create new migration"
	@echo "load-sample    - Load sample data"

install:
	pip install -r requirements.txt
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

test:
	pytest tests/ -v --cov=src/team_alchemy --cov-report=term-missing --cov-report=html

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

lint:
	flake8 src/ tests/
	mypy src/
	pylint src/team_alchemy/

format:
	black src/ tests/
	isort src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/

run:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

init-db:
	python scripts/setup_database.py

migrate:
	python scripts/migrate_database.py

migration:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

load-sample:
	python scripts/load_sample_data.py
