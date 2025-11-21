"""
Postgres backend using Testcontainers for tests.
Creates a singleton container per test session to improve performance.

Features:
- KEEP_TEST_DB=1 keeps container running after tests (disables Ryuk)
- TEST_DB_CONTAINER_NAME sets a deterministic container name
- If KEEP_TEST_DB=1 and TEST_DB_PORT is provided, connects to an existing container
- Optional fixed host port via TEST_DB_PORT

Credentials are loaded exclusively from tests/.env.test via test_settings.
"""
from __future__ import annotations

import os
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from testcontainers.postgres import PostgresContainer

from tests.infrastructure.config.settings_test import test_settings

_container: Optional[PostgresContainer] = None
_engine: Optional[Engine] = None


def get_postgres_engine() -> Engine:
    """
    Get or create PostgreSQL engine using testcontainers.
    
    Configuration is loaded exclusively from test_settings (tests/.env.test).
    No default values are used - all credentials must be configured.
    
    If a container with the same name already exists, it will be reused.
    """
    global _container, _engine
    if _engine is not None:
        return _engine
    
    # Read configuration from test_settings (loaded from tests/.env.test)
    keep_db = test_settings.KEEP_TEST_DB == "1"
    username = test_settings.TEST_DB_USER
    password = test_settings.TEST_DB_PASSWORD
    dbname = test_settings.TEST_DB_NAME
    container_name = test_settings.TEST_DB_CONTAINER_NAME
    host_port_str = test_settings.TEST_DB_PORT
    host_port = int(host_port_str) if host_port_str and host_port_str.isdigit() else None

    # If we want to keep the DB, disable Ryuk (resource reaper) so container persists
    if keep_db:
        os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"
    else:
        os.environ.pop("TESTCONTAINERS_RYUK_DISABLED", None)

    # Create container configuration
    container = PostgresContainer("postgres:15-alpine")
    container = container.with_env("POSTGRES_USER", username)
    container = container.with_env("POSTGRES_PASSWORD", password)
    container = container.with_env("POSTGRES_DB", dbname)
    container = container.with_env("POSTGRES_INITDB_ARGS", "--encoding=UTF8")
    container = container.with_name(container_name)
    
    # If host_port is specified, map container port to that fixed port on host
    if host_port:
        container = container.with_bind_ports(5432, host_port)
    
    # Start the container (testcontainers will reuse if it exists with same name)
    try:
        container.start()
    except Exception as e:
        # If container already exists, try to get the existing one
        # This can happen when KEEP_TEST_DB=1 and container persists
        if "409" in str(e) or "Conflict" in str(e):
            # Container with same name exists, try to connect to it
            if host_port:
                # Use fixed port to connect to existing container
                url = f"postgresql+psycopg2://{username}:{password}@localhost:{host_port}/{dbname}"
                _engine = create_engine(url)
                # Try to connect to verify it's working
                with _engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                return _engine
            else:
                raise RuntimeError(
                    f"Container {container_name} already exists but no port mapping was provided. "
                    "Please set TEST_DB_PORT in tests/.env.test when using KEEP_TEST_DB=1"
                ) from e
        raise
    
    _container = container
    
    # Get connection URL from container
    url = container.get_connection_url()  # e.g. postgresql+psycopg2://...
    _engine = create_engine(url)
    return _engine


def stop_postgres_container() -> None:
    """
    Stop PostgreSQL container and dispose engine.
    Respects KEEP_TEST_DB setting to persist container for debugging.
    """
    global _container, _engine
    keep_db = test_settings.KEEP_TEST_DB == "1"
    if _engine is not None:
        _engine.dispose()
        _engine = None
    if _container is not None and not keep_db:
        try:
            _container.stop()
        finally:
            _container = None


