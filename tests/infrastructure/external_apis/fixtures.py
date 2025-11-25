"""
Pytest fixtures for external API mock servers.

These fixtures provide mock HTTP servers that can be used in tests
instead of (or in addition to) code-level mocking.
"""
import pytest
from pathlib import Path
from typing import Generator

from .server import MockAPIServer


@pytest.fixture(scope="function")
def posts_mock_server() -> Generator[MockAPIServer, None, None]:
    """
    Fixture that provides a running mock HTTP server for Posts API.
    
    The server is started before the test and stopped after.
    Use server.get_base_url() to get the URL to use in your application.
    
    Example:
        def test_with_mock_server(posts_mock_server):
            base_url = posts_mock_server.get_base_url()
            # Configure your app to use base_url for Posts API
            response = httpx.get(f"{base_url}/posts")
            assert response.status_code == 200
    """
    spec_path = Path(__file__).parent / "posts" / "openapi.yaml"
    server = MockAPIServer("posts", spec_path, port=0)
    
    try:
        port = server.start()
        yield server
    finally:
        server.stop()


@pytest.fixture(scope="session")
def posts_mock_server_session() -> Generator[MockAPIServer, None, None]:
    """
    Session-scoped fixture for Posts API mock server.
    
    The server is started once per test session and reused across tests.
    Use this for better performance when running many tests.
    
    Note: State is reset between tests using server.reset_state()
    """
    spec_path = Path(__file__).parent / "posts" / "openapi.yaml"
    server = MockAPIServer("posts", spec_path, port=0)
    
    try:
        port = server.start()
        yield server
    finally:
        server.stop()


@pytest.fixture(scope="function")
def nasa_mock_server() -> Generator[MockAPIServer, None, None]:
    """
    Fixture that provides a running mock HTTP server for NASA API.
    
    The server is started before the test and stopped after.
    Use server.get_base_url() to get the URL to use in your application.
    
    Example:
        def test_with_mock_server(nasa_mock_server):
            base_url = nasa_mock_server.get_base_url()
            # Configure your app to use base_url for NASA API
            response = httpx.get(f"{base_url}/planetary/apod?api_key=test")
            assert response.status_code == 200
    """
    spec_path = Path(__file__).parent / "nasa" / "openapi.yaml"
    server = MockAPIServer("nasa", spec_path, port=0)
    
    try:
        port = server.start()
        yield server
    finally:
        server.stop()


@pytest.fixture(scope="session")
def nasa_mock_server_session() -> Generator[MockAPIServer, None, None]:
    """
    Session-scoped fixture for NASA API mock server.
    
    The server is started once per test session and reused across tests.
    Use this for better performance when running many tests.
    
    Note: State is reset between tests using server.reset_state()
    """
    spec_path = Path(__file__).parent / "nasa" / "openapi.yaml"
    server = MockAPIServer("nasa", spec_path, port=0)
    
    try:
        port = server.start()
        yield server
    finally:
        server.stop()


def create_mock_server_fixture(api_name: str, spec_relative_path: str, scope: str = "function"):
    """
    Factory function to create mock server fixtures for any API.
    
    Args:
        api_name: Name of the API (e.g., "payments")
        spec_relative_path: Relative path to OpenAPI spec from this file
        scope: Pytest fixture scope ("function", "class", "module", "session")
    
    Returns:
        Pytest fixture function
    
    Example:
        payments_mock_server = create_mock_server_fixture(
            "payments", 
            "payments/openapi.yaml",
            scope="function"
        )
    """
    def _fixture() -> Generator[MockAPIServer, None, None]:
        base_dir = Path(__file__).parent
        spec_path = base_dir / spec_relative_path
        server = MockAPIServer(api_name, spec_path, port=0)
        
        try:
            port = server.start()
            yield server
        finally:
            server.stop()
    
    _fixture.__name__ = f"{api_name}_mock_server"
    return pytest.fixture(scope=scope)(_fixture)

