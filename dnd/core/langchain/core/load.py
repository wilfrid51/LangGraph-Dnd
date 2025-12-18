"""Minimal shim for langchain_core.load used by project imports."""
from typing import Any


def load_resource(name: str) -> Any:
    return None


__all__ = ["load_resource"]
