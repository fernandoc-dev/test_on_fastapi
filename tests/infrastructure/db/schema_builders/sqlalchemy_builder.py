"""
Helper to declare SQLAlchemy strategy configuration.
"""
from dataclasses import dataclass
from ..manager import SchemaStrategy


def sqlalchemy_strategy(module: str, base_attribute: str = "Base") -> SchemaStrategy:
    return SchemaStrategy(type="sqlalchemy", module=module, base_attribute=base_attribute)


