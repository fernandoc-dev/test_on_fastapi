# Testing Infrastructure Guide

This document explains the testing structure, infrastructure organization, and best practices for using this testing template.

## Table of Contents

- [Test Structure](#test-structure)
- [Infrastructure Organization](#infrastructure-organization)
- [External API Mocking](#external-api-mocking)
- [Test Schemas](#test-schemas)
- [Database Testing](#database-testing)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Test Structure

The test suite is organized into distinct layers, each serving a specific purpose:

```
tests/
├── unit/              # Pure logic tests (domain, use cases, helpers)
├── integration/       # Tests that touch real DB/testcontainers, queues, etc.
├── e2e/              # Tests that start the complete FastAPI app
├── load/             # Scripts for load testing (Locust)
└── infrastructure/   # Factories, fixtures, mocks and configuration
```

### Test Layers

#### Unit Tests (`tests/unit/`)
- **Purpose**: Test pure business logic without external dependencies
- **Characteristics**: Fast, isolated, no I/O operations
- **Example**: Domain models, utility functions, validators

#### Integration Tests (`tests/integration/`)
- **Purpose**: Test components working together (API + DB, API + external services)
- **Characteristics**: Use testcontainers, mocks for external APIs
- **Example**: CRUD operations, API endpoints with database

#### E2E Tests (`tests/e2e/`)
- **Purpose**: Test complete user flows end-to-end
- **Characteristics**: Full application stack, slower execution
- **Example**: Complete user registration flow, payment processing

#### Load Tests (`tests/load/`)
- **Purpose**: Performance and stress testing
- **Characteristics**: Use Locust, simulate high traffic
- **Example**: API endpoint performance under load

## Infrastructure Organization

The `tests/infrastructure/` directory encapsulates all reusable testing resources:

```
infrastructure/
├── config/              # Test-specific configuration
│   └── settings_test.py # Pydantic settings for tests
├── db/                  # Database testing utilities
│   ├── docker/          # Docker Compose for test DB
│   ├── factories/       # Test data factories
│   ├── migrations/      # Database schema migrations
│   └── manager.py       # Database connection manager
├── external_apis/       # External API mocking
│   ├── assets/          # JSON assets for API responses
│   ├── payloads/        # Legacy payloads (deprecated, use assets/)
│   └── providers/       # Mock provider classes
├── fixtures/            # Reusable static test data
└── schemas/             # Test specification schemas
```

### Key Principles

1. **Encapsulation**: All test infrastructure is isolated in `infrastructure/`
2. **Reusability**: Components can be reused across different test types
3. **Non-centralization**: Mock data is stored in assets, not hardcoded
4. **Independence**: Test schemas are independent from app schemas

## External API Mocking

### Architecture

External API mocks use a two-layer approach:

1. **Assets Layer** (`infrastructure/external_apis/assets/`): JSON files with API response examples
2. **Provider Layer** (`infrastructure/external_apis/providers/`): Classes that load and serve assets

### Creating a New API Mock

#### Step 1: Create Assets Directory

```bash
mkdir -p tests/infrastructure/external_apis/assets/my_api/
```

#### Step 2: Add JSON Assets

Create JSON files for different API responses:

```json
// tests/infrastructure/external_apis/assets/my_api/get_resource_1.json
{
  "id": 1,
  "name": "Example Resource",
  "status": "active"
}
```

```json
// tests/infrastructure/external_apis/assets/my_api/get_resources_all.json
[
  {
    "id": 1,
    "name": "Resource 1",
    "status": "active"
  },
  {
    "id": 2,
    "name": "Resource 2",
    "status": "inactive"
  }
]
```

#### Step 3: Create Mock Provider

```python
# tests/infrastructure/external_apis/providers/my_api_mock.py
from typing import Dict, Any, List
import json
from pathlib import Path


class MyAPIMock:
    """Mock for MyAPI service"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "assets" / "my_api"
    
    def _load_json_file(self, filename: str) -> Any:
        """Load JSON file from assets directory"""
        file_path = self.base_path / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Asset file not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_resource_by_id(self, resource_id: int) -> Dict[str, Any]:
        """Returns resource by ID from assets"""
        return self._load_json_file(f"get_resource_{resource_id}.json")
    
    def get_all_resources(self) -> List[Dict[str, Any]]:
        """Returns list of all resources from assets"""
        return self._load_json_file("get_resources_all.json")
```

#### Step 4: Use in Tests

```python
# tests/integration/test_my_api.py
import pytest
from unittest.mock import patch, MagicMock
from tests.infrastructure.external_apis.providers.my_api_mock import MyAPIMock


@pytest.fixture
def my_api_mock():
    """Fixture that provides MyAPIMock instance"""
    return MyAPIMock()


@pytest.fixture
def mock_external_api(my_api_mock):
    """Fixture that mocks the external API"""
    with patch('app.services.my_api_service.httpx.AsyncClient') as mock_client:
        # Configure mock responses based on assets
        async def mock_get(url, **kwargs):
            mock_response = MagicMock()
            if "/resources/" in url:
                resource_id = int(url.split("/resources/")[-1])
                data = my_api_mock.get_resource_by_id(resource_id)
                mock_response.status_code = 200
                mock_response.json = MagicMock(return_value=data)
                mock_response.raise_for_status = MagicMock()
            return mock_response
        
        mock_client.return_value.__aenter__.return_value.get = mock_get
        yield mock_client


@pytest.mark.asyncio
async def test_get_resource(client, mock_external_api, my_api_mock):
    """Test that uses assets loaded dynamically"""
    response = await client.get("/api/resources/1")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate using assets
    expected = my_api_mock.get_resource_by_id(1)
    assert data["id"] == expected["id"]
    assert data["name"] == expected["name"]
```

### Benefits of Asset-Based Mocking

1. **Non-centralized**: Mock data is stored in JSON files, not in code
2. **Dynamic loading**: Assets are loaded at test execution time
3. **Easy maintenance**: Update JSON files without touching test code
4. **Reusability**: Same assets can be used across multiple test files
5. **Version control**: Changes to mock data are tracked in git

## Test Schemas

Test schemas (`infrastructure/schemas/`) are **independent specification models** that define the expected API contract.

### Purpose

- Define what the API **should** return (specification)
- Validate that app implementation satisfies requirements
- Ensure tests validate against requirements, not just internal consistency

### Creating Test Schemas

```python
# tests/infrastructure/schemas/resource.py
from pydantic import BaseModel
from typing import Optional


class ResourceSpec(BaseModel):
    """
    Resource specification model for API responses.
    
    This is the target model - what we expect to receive from the API.
    Tests validate that the app response satisfies this contract.
    """
    id: int
    name: str
    status: str
    created_at: str  # ISO 8601 datetime string
    updated_at: Optional[str] = None
    
    model_config = {"from_attributes": True}


class ResourceCreateSpec(BaseModel):
    """Resource creation request specification"""
    name: str
    status: str = "active"


class ResourceUpdateSpec(BaseModel):
    """Resource update request specification"""
    name: Optional[str] = None
    status: Optional[str] = None
```

### Using Test Schemas

```python
# tests/integration/test_resource_crud.py
from tests.infrastructure.schemas.resource import ResourceSpec


@pytest.mark.asyncio
async def test_get_resource(client):
    """Test validates response against ResourceSpec"""
    response = await client.get("/api/resources/1")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response matches ResourceSpec specification
    resource = ResourceSpec(**data)
    
    # Additional business logic validation
    assert resource.status in ["active", "inactive"]
```

### TDD Workflow with Schemas

1. **Requirement changes**: Update test schema first (add new field)
2. **Run tests**: Tests will fail (RED phase) - expected
3. **Implement in app**: Update app code to satisfy the test schema
4. **Tests pass**: Implementation matches specification (GREEN phase)
5. **Refactor**: Improve code while keeping tests green

### Naming Convention

- Suffix with `Spec`: `UserSpec`, `ResourceSpec`, `PostSpec`
- Keep structure aligned with API responses, not internal app structure
- Avoid "Test" prefix (pytest collects classes starting with "Test")

## Database Testing

### Testcontainers Integration

The template uses Testcontainers to provide isolated PostgreSQL databases for testing.

### Configuration

Database configuration is managed in:
- `tests/infrastructure/config/settings_test.py`: Test settings
- `tests/infrastructure/db/manager.py`: Database connection manager
- `tests/conftest.py`: Pytest fixtures

### Using Database in Tests

```python
# tests/integration/test_user_crud.py
import pytest
from sqlalchemy import text
from datetime import datetime


@pytest.mark.asyncio
async def test_create_user(client, db_session):
    """Test that uses database session"""
    # Create user directly in database
    result = db_session.execute(
        text("""
            INSERT INTO users (email, username, is_active, created_at)
            VALUES (:email, :username, :is_active, :created_at)
            RETURNING id
        """),
        {
            "email": "test@example.com",
            "username": "testuser",
            "is_active": True,
            "created_at": datetime.now()
        }
    )
    user_id = result.scalar()
    db_session.commit()
    
    # Test API endpoint
    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200
```

### Database Factories

Use factories to create test data:

```python
# tests/infrastructure/db/factories/user_factory.py
from tests.infrastructure.db.factories.base import BaseFactory
from app.database.models import UserModel


class UserFactory(BaseFactory):
    """Factory for creating User test data"""
    
    @classmethod
    def create(cls, db_session, **kwargs):
        """Create a user in the database"""
        defaults = {
            "email": "user@example.com",
            "username": "testuser",
            "is_active": True
        }
        defaults.update(kwargs)
        
        user = UserModel(**defaults)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
```

## Best Practices

### 1. Test Organization

- **One test file per resource/feature**: `test_user_crud.py`, `test_posts_crud.py`
- **Group related tests**: Use comments to separate test groups
- **Descriptive test names**: `test_get_user_by_id_not_found` not `test_get_user_404`

### 2. Mock Management

- **Use assets for mock data**: Store JSON files in `assets/` directory
- **Load dynamically**: Use providers to load assets at runtime
- **Maintain state when needed**: Use fixtures to track state across calls

### 3. Schema Validation

- **Always validate against Spec schemas**: Ensures API contract compliance
- **Keep schemas independent**: Don't import from `app/schemas/`
- **Update schemas first in TDD**: Change spec, then implementation

### 4. Test Isolation

- **Each test is independent**: No shared state between tests
- **Use fixtures for setup**: `db_session`, `client`, etc.
- **Clean up after tests**: Database transactions are rolled back automatically

### 5. Error Testing

- **Test both success and error cases**: 200, 404, 422, 500, etc.
- **Validate error responses**: Check status codes and error messages
- **Test edge cases**: Invalid IDs, missing fields, etc.

## Examples

### Complete Example: Posts CRUD with External API

See `tests/integration/test_posts_crud.py` for a complete example that demonstrates:

- Asset-based mocking (`tests/infrastructure/external_apis/assets/posts/`)
- Mock provider (`tests/infrastructure/external_apis/providers/posts_mock.py`)
- Test schemas (`tests/infrastructure/schemas/post.py`)
- State management in mocks (deleted posts tracking)
- Complete CRUD test coverage

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/integration/test_posts_crud.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v
```

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Testcontainers Python](https://testcontainers-python.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Contributing

When adding new test infrastructure:

1. Follow the existing directory structure
2. Document your additions in this README
3. Add examples for complex patterns
4. Ensure tests are isolated and reusable
5. Use conventional commits for changes

