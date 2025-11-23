# Mock HTTP Server - Quick Start Guide

## Overview

The mock HTTP server provides a **real HTTP server** that serves API responses based on OpenAPI specifications. This is an alternative to code-level mocking that provides more realistic integration testing.

## Quick Example

```python
import pytest
import httpx
from tests.infrastructure.external_apis.server import MockAPIServer

@pytest.mark.asyncio
async def test_example(posts_mock_server: MockAPIServer):
    """Test using real HTTP mock server"""
    base_url = posts_mock_server.get_base_url()
    
    async with httpx.AsyncClient(base_url=base_url) as client:
        response = await client.get("/posts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
```

## Features

✅ **Real HTTP Server**: Actual HTTP requests, not code-level mocks  
✅ **OpenAPI-Driven**: Routes created automatically from OpenAPI specs  
✅ **Dynamic Path Parameters**: Handles `/posts/{id}` → `/posts/123`  
✅ **State Management**: Tracks deleted resources, maintains state  
✅ **Background Process**: Runs in separate thread during tests  
✅ **Auto Cleanup**: Server stops automatically after tests  

## Available Fixtures

### Function Scope (Default)

```python
def test_one(posts_mock_server: MockAPIServer):
    """Server starts for this test, stops after"""
    base_url = posts_mock_server.get_base_url()
    # ... your test
```

### Session Scope

```python
def test_one(posts_mock_server_session: MockAPIServer):
    """Server starts once per test session, reused across tests"""
    base_url = posts_mock_server.get_base_url()
    # ... your test
```

## Server Methods

### `get_base_url() -> str`
Get the base URL of the running server.

```python
base_url = posts_mock_server.get_base_url()
# Returns: "http://127.0.0.1:54321"
```

### `reset_state()`
Reset server state (clears deleted resources, etc.).

```python
posts_mock_server.reset_state()
```

### `start() -> int`
Manually start the server (usually done by fixture).

```python
port = posts_mock_server.start()
```

### `stop()`
Manually stop the server (usually done by fixture).

```python
posts_mock_server.stop()
```

## State Management

The server maintains state across requests. For example, deleted resources are tracked:

```python
async with httpx.AsyncClient(base_url=base_url) as client:
    # Delete a resource
    await client.delete("/posts/1")
    
    # Subsequent GET returns 404
    response = await client.get("/posts/1")
    assert response.status_code == 404
```

## Creating Custom Mock Servers

To create a mock server for a new API:

1. **Ensure OpenAPI spec exists** in `tests/infrastructure/external_apis/{api_name}/openapi.yaml`

2. **Create fixture** (optional, or use factory):

```python
from tests.infrastructure.external_apis.fixtures import create_mock_server_fixture

# Create fixture for your API
my_api_mock_server = create_mock_server_fixture(
    "my_api",
    "my_api/openapi.yaml",
    scope="function"
)
```

3. **Use in tests**:

```python
def test_my_api(my_api_mock_server: MockAPIServer):
    base_url = my_api_mock_server.get_base_url()
    # ... your test
```

## Comparison: Mock Server vs Code-Level Mocking

| Feature | Mock Server | Code-Level Mock |
|---------|-------------|-----------------|
| **Speed** | Slower (real HTTP) | Faster (in-memory) |
| **Realism** | High (real HTTP) | Low (mocked) |
| **Debugging** | Can access in browser | Code-only |
| **E2E Tests** | ✅ Yes | ❌ No |
| **Network Testing** | ✅ Yes | ❌ No |
| **Setup Complexity** | Medium | Low |

**Recommendation**: Use mock server for integration/E2E tests, code-level mocking for unit tests.

## Troubleshooting

### Server won't start
- Check that port is available (use `port=0` for random port)
- Ensure FastAPI and uvicorn are installed

### Routes not found
- Verify OpenAPI spec has correct paths
- Check that `x-mock-payload` extensions are set
- Ensure payload files exist

### State not persisting
- Use session-scoped fixture for state across tests
- Call `reset_state()` to clear state between tests

## See Also

- `README.md` - Full documentation
- `test_posts_crud_with_server.py` - Complete examples
- `server.py` - Server implementation

