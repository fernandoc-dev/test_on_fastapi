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

Add JSON files to `payloads/` directory matching the spec mappings.

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

## Example: Posts API

See `posts/` directory for a complete working example:
- OpenAPI spec with all CRUD operations
- Mock provider with helper methods
- Payload files for success and error cases
- Used in `tests/test_types/integration/test_posts_crud.py`

## Future Enhancements

Potential improvements:
- [ ] Support for Postman Collection format natively
- [ ] Automatic payload validation against OpenAPI schemas
- [ ] Generate mock provider from OpenAPI spec
- [ ] Support for dynamic parameter substitution in payloads
- [ ] Integration with API documentation tools

