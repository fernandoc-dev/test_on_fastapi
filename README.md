# FastAPI Testing Template

Modular and reusable testing template for FastAPI with organized structure for unit, integration, E2E and load tests.

This is a **testing template**, not a full application. The included FastAPI app is minimal (hello world) to serve as a testing target. The real value is in the comprehensive testing infrastructure.

## What’s included (high-level)

- Testing layers: unit, integration, e2e, load
- Centralized testing configuration with pytest and fixtures
- Encapsulated database backend for tests using Postgres + Testcontainers
- Flexible schema application strategies (SQLAlchemy, SQLModel, or raw SQL files)
- Deterministic, optionally persistent test database container for debugging
- Idempotent SQL seed execution

## Project Structure

```
tests/
    unit/              # Pure logic tests (domain, use cases, helpers)
    integration/       # Tests that touch real DB/testcontainers, queues, etc.
    e2e/              # Tests that start the complete FastAPI app
    load/             # Scripts for load testing (Locust)
    infrastructure/   # Factories, fixtures, mocks and configuration
        db/
            docker/   # docker-compose for test DB
            factories/
            migrations/
            seed/
        external_apis/
            providers/  # External API mocks
            payloads/   # Example responses
        fixtures/      # Reusable static data
        config/        # Test-specific configuration
    conftest.py
    pytest.ini
    requirements.test.txt
```

## Environment configuration (App vs Tests)

This template uses separate environment files to clearly split application concerns from testing concerns:

- Application runtime: `.env` (at repo root)
- Testing runtime: `tests/.env.test`

Only the testing stack reads `tests/.env.test` (via `tests/infrastructure/config/settings_test.py`). The application keeps using `.env` as usual.

### Testing environment: tests/.env.test

Create the file `tests/.env.test` (you can also create a `tests/.env.test.example` and copy it). Suggested content:

```env
# DB backend for tests
TEST_DB_BACKEND=postgres_testcontainers

# Seeds directory (optional)
TEST_DB_SEEDS_DIR=tests/infrastructure/db/seed

# Schema strategy (choose one)
# 1) Use raw SQL files (default example)
SQL_FILES_DIR=tests/infrastructure/db/migrations/sql
# 2) Or use SQLAlchemy models
# SQLALCHEMY_SCHEMA_MODULE=app.infrastructure.database.models
# SQLALCHEMY_BASE_ATTRIBUTE=Base
# 3) Or use SQLModel models
# SQLMODEL_SCHEMA_MODULE=app.infrastructure.database.sqlmodel_models
# SQLMODEL_ATTRIBUTE=SQLModel

# Testcontainers controls
# Keep the Postgres container alive after the test session (1=yes, 0=no)
KEEP_TEST_DB=0
# Deterministic container name (useful for debugging)
TEST_DB_CONTAINER_NAME=fastapi_test_db_tc
# Fixed host port mapping (optional, e.g., 5433). Leave empty for random.
TEST_DB_PORT=
# Credentials used by the test container (and to connect if persistent)
TEST_DB_USER=test
TEST_DB_PASSWORD=test
TEST_DB_NAME=test
```

### Application environment: .env

Keep using your standard `.env` for the application (not used by the testing DB manager). Database variables in `.env` are independent from the testing ones.

## Test database backend (encapsulated)

The tests use a centralized DB manager to start and configure a Postgres container via Testcontainers:

- File: `tests/infrastructure/db/dialects/postgres_testcontainers.py`
- Manager: `tests/infrastructure/db/manager.py`
- Fixtures: `tests/conftest.py` exposes:
  - `db_engine` (per session): creates schema and runs seeds once
  - `db_session` (per test): provides a SQLAlchemy session with transaction scope

Key features:
- Deterministic container name via `TEST_DB_CONTAINER_NAME`
- Optional persistence across runs with `KEEP_TEST_DB=1` (disables Ryuk so it won’t be auto-removed)
- Optional fixed host port via `TEST_DB_PORT`
- Flexible schema strategies:
  - SQL files: all `.sql` files in a directory are executed in order
  - SQLAlchemy: run `Base.metadata.create_all(engine)`
  - SQLModel: run `SQLModel.metadata.create_all(engine)`
- Seed execution: any `.sql` in `tests/infrastructure/db/seed` (or your custom dir) will be executed in order; prefer idempotent statements

Example workflows:
- Keep container for debugging:
  - Set in `tests/.env.test`: `KEEP_TEST_DB=1`, `TEST_DB_PORT=5433`
  - Run tests, then connect with your SQL client to `postgres://TEST_DB_USER:TEST_DB_PASSWORD@localhost:5433/TEST_DB_NAME`
- Fast ephemeral container:
  - Set `KEEP_TEST_DB=0` and leave `TEST_DB_PORT` empty for random mapping

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Make (optional, but recommended)

### System Dependencies Installation (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y make python3-venv docker.io docker-compose
```

## Quick Start

### 1. Create virtual environment for tests

```bash
make env-test
source venv_test/bin/activate
```

Or manually:

```bash
python3 -m venv venv_test
source venv_test/bin/activate
pip install --upgrade pip
pip install -r tests/requirements.test.txt
pip install -r app/requirements.txt
```

### 2. Start the application

```bash
make run
```

Or manually:

```bash
docker-compose up -d
```

The application will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- pgAdmin: http://localhost:5050 (email: admin@admin.com, password: admin)
- PostgreSQL: localhost:5432 (user: postgres, password: postgres, database: fastapi_db)

### 3. Run tests

```bash
make test
```

Or manually:

```bash
pytest tests/ -v
```

### 4. Stop the application

```bash
make stop
```

Or manually:

```bash
docker-compose down
```

## Available Make Commands

- `make run` - Start application container
- `make stop` - Stop and remove container
- `make test` - Run tests
- `make env-test` - Create virtual environment with test dependencies
- `make clean` - Clean containers, volumes and temporary files
- `make help` - Show help

## Test Structure

### Unit Tests (`tests/unit/`)

Pure logic tests without external dependencies:

```python
# tests/unit/test_<algo>_use_case.py
def test_something():
    # Use case test
    pass
```

### Integration Tests (`tests/integration/`)

Tests that interact with real services (DB, queues, etc.):

```python
# tests/integration/test_<servicio>_repository.py
async def test_repository():
    # Test with real DB or testcontainers
    pass
```

### E2E Tests (`tests/e2e/`)

Tests that start the complete FastAPI application:

```python
# tests/e2e/test_<caso_de_uso_principal>.py
async def test_full_flow():
    # Complete end-to-end test
    pass
```

### Load Tests (`tests/load/`)

Scripts for load testing with Locust:

```bash
# Install Locust
pip install locust

# Run load tests
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and adjust as needed:

```bash
cp .env.example .env
```

**Environment Variables:**
All configuration is managed through `.env` file. Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key variables:
- `API_PORT`: Application port (default: 8000)
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: Database credentials (DATABASE_URL is automatically constructed from these)
- `POSTGRES_PORT`: Database port (default: 5432)
- `PGADMIN_PORT`: pgAdmin port (default: 5050)
- `PGADMIN_DEFAULT_EMAIL`, `PGADMIN_DEFAULT_PASSWORD`: pgAdmin credentials

**Note:** `DATABASE_URL` is automatically built from the individual PostgreSQL variables in `docker-compose.yml` to ensure consistency. You don't need to set it manually.

**Default Services:**
- PostgreSQL: `localhost:${POSTGRES_PORT:-5432}` (user: `postgres`, password: `postgres`, database: `fastapi_db`)
- pgAdmin: `http://localhost:${PGADMIN_PORT:-5050}` (email: `admin@admin.com`, password: `admin`)

### Test Configuration

Test configuration is in:
- `tests/configtest.py` - Basic configuration
- `tests/infrastructure/config/settings_test.py` - Pydantic settings for tests
- `tests/pytest.ini` - Pytest configuration

## Development

### Add new dependencies

**For the application:**
```bash
# Edit app/requirements.txt
pip install -r app/requirements.txt
```

**For tests:**
```bash
# Edit tests/requirements.test.txt
pip install -r tests/requirements.test.txt
```

### Run specific tests

```bash
# Only unit tests
pytest tests/unit/ -v

# Only integration tests
pytest tests/integration/ -v

# Only E2E tests
pytest tests/e2e/ -v

# Specific test
pytest tests/unit/test_hello_world.py -v
```

### With coverage

```bash
pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

## Next Steps

1. Add unit tests for your business logic
2. Configure test database (see `tests/infrastructure/db/docker/docker-compose.test.yml`)
3. Add factories for test data (see `tests/infrastructure/db/factories/`)
4. Configure external API mocks (see `tests/infrastructure/external_apis/`)
5. Add reusable fixtures (see `tests/infrastructure/fixtures/`)

## License

See LICENSE file
