.PHONY: help run stop test env-test clean

help:
	@echo "Available commands:"
	@echo "  make run       - Start application container"
	@echo "  make stop      - Stop and remove container"
	@echo "  make test      - Run tests"
	@echo "  make env-test  - Create virtual environment with test dependencies"
	@echo "  make clean     - Clean containers and volumes"

run:
	@echo "Starting FastAPI application..."
	docker-compose up -d
	@echo "Application available at http://localhost:8000"
	@echo "Documentation available at http://localhost:8000/docs"

stop:
	@echo "Stopping application..."
	docker-compose down

test:
	@echo "Running tests..."
	@if [ -d "venv_test" ] && [ -f "venv_test/bin/pytest" ]; then \
		echo "Using virtual environment pytest..."; \
		PYTHONPATH=$$(pwd) venv_test/bin/pytest tests/ -v; \
	elif command -v pytest >/dev/null 2>&1; then \
		echo "Using system pytest..."; \
		PYTHONPATH=$$(pwd) pytest tests/ -v; \
	else \
		echo "Error: pytest not found. Please run 'make env-test' first to create the test environment."; \
		exit 1; \
	fi

env-test:
	@echo "Creating virtual environment for tests..."
	python3 -m venv venv_test
	@echo "Activating virtual environment..."
	@echo "To activate manually run: source venv_test/bin/activate"
	venv_test/bin/pip install --upgrade pip
	venv_test/bin/pip install -r app/requirements.txt
	venv_test/bin/pip install -r tests/requirements.test.txt
	@echo "Virtual environment created. To activate: source venv_test/bin/activate"

clean:
	@echo "Cleaning containers and volumes..."
	docker-compose down -v
	@echo "Cleaning test virtual environment..."
	rm -rf venv_test
	@echo "Cleaning Python files..."
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -r {} + 2>/dev/null || true

