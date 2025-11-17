"""
Postgres backend using Testcontainers for tests.
Creates a singleton container per test session to improve performance.

Features:
- KEEP_TEST_DB=1 keeps container running after tests (disables Ryuk)
- TEST_DB_CONTAINER_NAME sets a deterministic container name
- If KEEP_TEST_DB=1 and TEST_DB_PORT is provided, connects to an existing container
- Optional fixed host port via TEST_DB_PORT
"""
from __future__ import annotations

import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from testcontainers.postgres import PostgresContainer

_container: Optional[PostgresContainer] = None
_engine: Optional[Engine] = None


def get_postgres_engine() -> Engine:
    global _container, _engine
    if _engine is not None:
        return _engine
    # Read env configuration
    keep_db = os.getenv("KEEP_TEST_DB", "0") == "1"
    username = os.getenv("TEST_DB_USER", "test")
    password = os.getenv("TEST_DB_PASSWORD", "test")
    dbname = os.getenv("TEST_DB_NAME", "test")
    container_name = os.getenv("TEST_DB_CONTAINER_NAME", "fastapi_test_db_tc")
    host_port_str = os.getenv("TEST_DB_PORT", "")
    host_port = int(host_port_str) if host_port_str.isdigit() else None

    # If we want to keep the DB, disable Ryuk (resource reaper) so container persists
    if keep_db:
        os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"
    else:
        os.environ.pop("TESTCONTAINERS_RYUK_DISABLED", None)

    # If KEEP_TEST_DB=1 and a host port is defined, assume an existing container is running
    if keep_db and host_port:
        url = f"postgresql+psycopg2://{username}:{password}@localhost:{host_port}/{dbname}"
        _engine = create_engine(url)
        return _engine

    # Otherwise start a new container
    container = PostgresContainer("postgres:15-alpine")
    container = container.with_env("POSTGRES_USER", username)
    container = container.with_env("POSTGRES_PASSWORD", password)
    container = container.with_env("POSTGRES_DB", dbname)
    container = container.with_env("POSTGRES_INITDB_ARGS", "--encoding=UTF8")
    container = container.with_name(container_name)
    if host_port:
        # Map container port 5432 to host_port
        container = container.with_bind_ports("5432/tcp", host_port)
    container.start()
    _container = container
    url = container.get_connection_url()  # e.g. postgresql+psycopg2://...
    _engine = create_engine(url)
    return _engine


def stop_postgres_container() -> None:
    global _container, _engine
    keep_db = os.getenv("KEEP_TEST_DB", "0") == "1"
    if _engine is not None:
        _engine.dispose()
        _engine = None
    if _container is not None and not keep_db:
        try:
            _container.stop()
        finally:
            _container = None


