"""
Database manager for tests: encapsulated entrypoint to create engine,
prepare schema from different strategies, and run seeds.
"""
from __future__ import annotations

import importlib
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .dialects.postgres_testcontainers import get_postgres_engine, stop_postgres_container


@dataclass
class SchemaStrategy:
    """
    Strategy for building the database schema.
    type:
      - "sqlalchemy": import module and call Base.metadata.create_all(engine)
      - "sqlmodel": import module and call SQLModel.metadata.create_all(engine)
      - "sql_files": execute *.sql files in given directory (in order)
    """
    type: str
    module: Optional[str] = None
    base_attribute: Optional[str] = None  # e.g., "Base" or "SQLModel"
    sql_dir: Optional[str] = None


def _execute_sql_files(engine: Engine, directory: Path) -> None:
    files: Iterable[Path] = sorted(p for p in directory.glob("*.sql"))
    with engine.begin() as conn:
        for file in files:
            sql = file.read_text(encoding="utf-8")
            # Allow multiple statements separated by ';'
            for statement in filter(None, (s.strip() for s in sql.split(";"))):
                conn.execute(text(statement))


def apply_schema(engine: Engine, strategy: SchemaStrategy) -> None:
    """Apply schema to engine using provided strategy."""
    stype = strategy.type.lower()
    if stype == "sqlalchemy":
        if not strategy.module or not strategy.base_attribute:
            raise ValueError("sqlalchemy strategy requires 'module' and 'base_attribute'")
        module = importlib.import_module(strategy.module)
        base = getattr(module, strategy.base_attribute)
        base.metadata.create_all(engine)
        return
    if stype == "sqlmodel":
        if not strategy.module or not strategy.base_attribute:
            raise ValueError("sqlmodel strategy requires 'module' and 'base_attribute'")
        module = importlib.import_module(strategy.module)
        sqlmodel_meta = getattr(module, strategy.base_attribute).metadata  # type: ignore[attr-defined]
        sqlmodel_meta.create_all(engine)
        return
    if stype == "sql_files":
        if not strategy.sql_dir:
            raise ValueError("sql_files strategy requires 'sql_dir'")
        _execute_sql_files(engine, Path(strategy.sql_dir))
        return
    raise ValueError(f"Unknown schema strategy: {strategy.type}")


def run_seed_sql(engine: Engine, seeds_dir: str) -> None:
    """Execute .sql seed files in alphabetical order. Idempotence is up to SQL logic."""
    _execute_sql_files(engine, Path(seeds_dir))


def create_engine_and_schema(strategy: SchemaStrategy, seeds_dir: Optional[str] = None) -> Engine:
    """
    Create a Postgres engine via Testcontainers and build schema/seeds.
    Returns an SQLAlchemy Engine.
    """
    engine = get_postgres_engine()
    apply_schema(engine, strategy)
    # Run seeds if provided or if default directory exists
    if seeds_dir and Path(seeds_dir).exists():
        run_seed_sql(engine, seeds_dir)
    else:
        default_seeds = Path("tests/infrastructure/db/seed")
        if default_seeds.exists():
            run_seed_sql(engine, str(default_seeds))
    return engine


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def session_scope(engine: Engine):
    """Provide a transactional scope around a series of operations."""
    SessionLocal = create_session_factory(engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def shutdown_backends() -> None:
    """Shutdown any running containers (called at end of test session)."""
    stop_postgres_container()


