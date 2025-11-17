"""
Helper to declare SQLModel strategy configuration.
"""
from ..manager import SchemaStrategy


def sqlmodel_strategy(module: str, model_attribute: str = "SQLModel") -> SchemaStrategy:
    # SQLModel exposes metadata via SQLModel.metadata
    return SchemaStrategy(type="sqlmodel", module=module, base_attribute=model_attribute)


