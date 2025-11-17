"""
Helper to declare raw SQL files strategy configuration.
"""
from pathlib import Path
from ..manager import SchemaStrategy


def sql_files_strategy(sql_dir: str) -> SchemaStrategy:
    return SchemaStrategy(type="sql_files", sql_dir=str(Path(sql_dir)))


