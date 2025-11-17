# Project Structure

## Summary of Created Files

### FastAPI Application
- `app/main.py` - FastAPI application with basic endpoints (/, /health)
- `app/requirements.txt` - Application dependencies
- `app/Dockerfile` - Dockerfile to build the application image
- `docker-compose.yml` - Docker Compose configuration for the application

### Tests
- `tests/requirements.test.txt` - Testing dependencies
- `tests/configtest.py` - Basic test configuration
- `tests/conftest.py` - Global pytest configuration
- `tests/pytest.ini` - Pytest configuration

#### Unit Tests
- `tests/unit/test_hello_world.py` - Example unit tests

#### Integration Tests
- `tests/integration/` - Folder for integration tests

#### E2E Tests
- `tests/e2e/test_hello_world_e2e.py` - Example E2E tests

#### Load Tests
- `tests/load/locustfile.py` - Locust configuration for load testing

#### Test Infrastructure
- `tests/infrastructure/db/docker/docker-compose.test.yml` - Docker Compose for test DB
- `tests/infrastructure/db/factories/mission_factory.py` - Mission factory
- `tests/infrastructure/db/factories/user_factory.py` - User factory
- `tests/infrastructure/external_apis/providers/dronesuite_mock.py` - Dronesuite mock
- `tests/infrastructure/external_apis/providers/payments_mock.py` - Payments mock
- `tests/infrastructure/external_apis/payloads/` - Example payloads for mocks
- `tests/infrastructure/fixtures/` - Reusable JSON fixtures
- `tests/infrastructure/config/settings_test.py` - Pydantic settings for tests

### Configuration
- `Makefile` - Useful commands (run, stop, test, env-test, clean)
- `.env.example` - Environment variables example
- `.gitignore` - Files to ignore in git
- `README.md` - Project documentation

## Next Steps

1. Install system dependencies: `sudo apt install make python3-venv docker.io`
2. Create virtual environment: `make env-test`
3. Activate environment: `source venv_test/bin/activate`
4. Start application: `make run`
5. Run tests: `make test`
