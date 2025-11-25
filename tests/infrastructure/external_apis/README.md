# External API Mocking Infrastructure

This directory contains the infrastructure for mocking external APIs in tests. The system is designed to be **specification-driven**, using OpenAPI (Swagger) or Postman Collections as the source of truth for API contracts.

## Overview

The mocking system follows these principles:

1. **Specification-First**: API contracts are defined in OpenAPI or Postman Collection format
2. **Payload Mapping**: Endpoints are mapped to JSON payload files via specification extensions
3. **Maintainability**: When the API changes, update the spec and payloads - tests automatically reflect changes
4. **Reusability**: The same pattern works for any external API

## Directory Structure

```
external_apis/
├── README.md                    # This file
├── posts/                       # Example: Posts API mock
│   ├── openapi.yaml            # OpenAPI specification
│   ├── spec_loader.py          # Loads and parses OpenAPI spec
│   ├── mock.py                 # Mock provider class
│   └── payloads/               # JSON response files
│       ├── GET_posts_200.json
│       ├── GET_posts_1_200.json
│       ├── GET_posts_999_404.json
│       ├── POST_posts_request.json
│       ├── POST_posts_201.json
│       └── ...
└── [other_api]/                # Additional APIs follow same pattern
```

## How It Works

### 1. OpenAPI Specification

The OpenAPI spec (`openapi.yaml`) defines:
- API endpoints and methods
- Request/response schemas
- **Extension fields** (`x-mock-payload`, `x-mock-request`) that map to payload files

Example:

```yaml
paths:
  /posts/{id}:
    get:
      responses:
        '200':
          x-mock-payload: payloads/GET_posts_1_200.json
        '404':
          x-mock-payload: payloads/GET_posts_999_404.json
    post:
      requestBody:
        content:
          application/json:
            x-mock-request: payloads/POST_posts_request.json
      responses:
        '201':
          x-mock-payload: payloads/POST_posts_201.json
```

### 2. Spec Loader

The `spec_loader.py` module:
- Parses the OpenAPI YAML file
- Extracts endpoint-to-payload mappings
- Provides methods to resolve payload paths for any endpoint

### 3. Mock Provider

The `mock.py` module:
- Uses `spec_loader` to find payload files
- Loads JSON payloads dynamically
- Provides methods like `get_post_by_id()`, `get_all_posts()`, etc.
- Handles edge cases (missing files, dynamic IDs, etc.)

### 4. Payload Files

JSON files in `payloads/` contain:
- **Response payloads**: Actual API responses (200, 201, 404, etc.)
- **Request examples**: Sample request bodies for documentation

Naming convention:
- `{METHOD}_{path}_{status}.json` (e.g., `GET_posts_200.json`)
- `{METHOD}_{path}_{id}_{status}.json` (e.g., `GET_posts_1_200.json`)
- `{METHOD}_{path}_request.json` (e.g., `POST_posts_request.json`)

## Usage in Tests

### Basic Example

```python
from tests.infrastructure.external_apis.posts.mock import PostsMock

def test_get_post(mock_external_api, posts_mock):
    # Mock is automatically set up via fixture
    # Use posts_mock to access payloads if needed
    post_data = posts_mock.get_post_by_id(1)
    assert post_data is not None
```

### Mock Fixture

The `mock_external_api` fixture (in test files) intercepts HTTP calls and returns mocked responses:

```python
@pytest.fixture
def mock_external_api(posts_mock):
    """Mock external API calls"""
    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock responses based on posts_mock
        ...
        yield
```

## Creating a New API Mock

### Step 1: Create Directory Structure

```bash
mkdir -p tests/infrastructure/external_apis/my_api/payloads
```

### Step 2: Create OpenAPI Specification

Create `my_api/openapi.yaml`:

```yaml
openapi: 3.0.3
info:
  title: My API
  version: 1.0.0
paths:
  /resource:
    get:
      responses:
        '200':
          x-mock-payload: payloads/GET_resource_200.json
```

### Step 3: Create Spec Loader

Copy and adapt `posts/spec_loader.py` (usually no changes needed).

### Step 4: Create Mock Provider

Create `my_api/mock.py`:

```python
from .spec_loader import OpenAPISpecLoader
from pathlib import Path

class MyAPIMock:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.spec_loader = OpenAPISpecLoader(self.base_dir / "openapi.yaml")
        self.payloads_dir = self.base_dir / "payloads"
    
    def get_resource(self):
        # Implement based on your API
        ...
```

### Step 5: Create Payload Files

**Recommended approach: Use real API responses from Postman**

1. Execute the collection in Postman with valid parameters
2. For successful responses (200, 201, etc.):
   - Right-click on the response → "Save Response" → "Save as Example"
   - Or manually copy the response body
3. Create JSON files in `payloads/` directory using the real responses
4. Name files according to the mapping in `openapi.yaml` (e.g., `GET_posts_200.json`)

**Why use real responses?**
- Mocks reflect exactly what the API returns
- Captures real data structures and edge cases
- Easier to maintain when API changes
- More realistic test scenarios

**Alternative**: Create example payloads based on OpenAPI schemas (less realistic but faster for initial setup)

### Step 6: Use in Tests

```python
from tests.infrastructure.external_apis.my_api.mock import MyAPIMock

@pytest.fixture
def my_api_mock():
    return MyAPIMock()
```

## Benefits

### 1. **Single Source of Truth**
- API contract is defined once in OpenAPI
- Payloads are explicitly mapped
- Changes to API are reflected in one place

### 2. **Easy Maintenance**
- Update OpenAPI spec when API changes
- Add/update payload files as needed
- Tests automatically use new payloads

### 3. **Professional Standard**
- OpenAPI is industry standard
- Can be generated from Postman Collections
- Compatible with API documentation tools

### 4. **Type Safety**
- OpenAPI schemas can be validated
- Payloads can be checked against schemas
- Reduces errors from manual mock setup

## Alternative: Postman Collections

If you have a Postman Collection instead of OpenAPI:

1. **Convert to OpenAPI**: Use tools like `postman-to-openapi`
2. **Or extend spec_loader**: Add support for Postman Collection format

Example conversion:
```bash
npm install -g postman-to-openapi
postman-to-openapi collection.json -o openapi.yaml
```

## Best Practices

1. **Keep specs up to date**: Update OpenAPI when API changes
2. **Use meaningful payload names**: `GET_posts_1_200.json` not `response1.json`
3. **Include error cases**: Add 404, 422, 500 payloads
4. **Document edge cases**: Add comments in spec for special handling
5. **Version control**: Commit both spec and payloads together

## Mock HTTP Server

In addition to code-level mocking, the system provides a **real HTTP mock server** that can be used for more realistic integration testing.

### Benefits of Mock Server

1. **Real HTTP requests**: Tests make actual HTTP calls, closer to production
2. **Manual debugging**: Server is accessible via browser/Postman during tests
3. **E2E testing**: Can be used for end-to-end tests that require real HTTP
4. **State management**: Server maintains state across requests (e.g., deleted resources)

### Using the Mock Server

#### Basic Usage

```python
import pytest
from httpx import AsyncClient
from tests.infrastructure.external_apis.server import MockAPIServer

@pytest.mark.asyncio
async def test_with_mock_server(posts_mock_server: MockAPIServer):
    """Test using real HTTP mock server"""
    # Get the base URL of the running server
    base_url = posts_mock_server.get_base_url()
    # e.g., "http://127.0.0.1:54321"
    
    # Make requests to the mock server
    import httpx
    async with httpx.AsyncClient(base_url=base_url) as client:
        response = await client.get("/posts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
```

#### Fixture Scopes

The mock server fixtures support different scopes:

- **Function scope** (default): Server starts/stops for each test
  ```python
  def test_one(posts_mock_server):
      # Server started for this test
      ...
  ```

- **Session scope**: Server starts once and is reused across all tests
  ```python
  def test_one(posts_mock_server_session):
      # Server started once per test session
      ...
  ```

#### State Management

The server maintains state across requests (e.g., tracking deleted resources):

```python
@pytest.mark.asyncio
async def test_delete_then_get(posts_mock_server: MockAPIServer):
    base_url = posts_mock_server.get_base_url()
    
    async with httpx.AsyncClient(base_url=base_url) as client:
        # Delete a resource
        response = await client.delete("/posts/1")
        assert response.status_code == 204
        
        # Subsequent GET should return 404
        response = await client.get("/posts/1")
        assert response.status_code == 404
```

#### Resetting State

Reset server state between tests if needed:

```python
def test_with_clean_state(posts_mock_server: MockAPIServer):
    # Reset state (clears deleted resources, etc.)
    posts_mock_server.reset_state()
    # ... your test
```

### Server Architecture

The mock server:
- **Dynamically creates routes** from OpenAPI specifications
- **Serves responses** from payload files mapped via `x-mock-payload`
- **Handles path parameters** (e.g., `/posts/{id}` → `/posts/123`)
- **Supports all HTTP methods** (GET, POST, PUT, DELETE, PATCH)
- **Runs in background thread** during tests

### Choosing Between Mock Approaches

**Use code-level mocking** (`mock_external_api` fixture) when:
- Tests need to be very fast
- You don't need real HTTP behavior
- You want to test error scenarios easily

**Use mock HTTP server** (`posts_mock_server` fixture) when:
- You need real HTTP integration testing
- You want to debug manually (access server in browser)
- You're writing E2E tests
- You need to test network-related behavior

Both approaches use the same OpenAPI specs and payload files, so you can switch between them easily.

## Example: Posts API

See `posts/` directory for a complete working example:
- OpenAPI spec with all CRUD operations
- Mock provider with helper methods
- Payload files for success and error cases
- Used in `tests/test_types/integration/test_posts_crud.py` (code-level mocking)
- Used in `tests/test_types/integration/test_posts_crud_with_server.py` (HTTP server)

## Future Enhancements

Potential improvements:
- [x] **Mock HTTP server** - Real HTTP server for integration testing
- [ ] Support for Postman Collection format natively
- [ ] Automatic payload validation against OpenAPI schemas
- [ ] Generate mock provider from OpenAPI spec
- [ ] Support for dynamic parameter substitution in payloads (templates)
- [ ] Integration with API documentation tools

