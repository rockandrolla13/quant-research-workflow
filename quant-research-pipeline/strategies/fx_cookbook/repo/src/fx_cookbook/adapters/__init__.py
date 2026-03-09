"""Adapter layer — transforms asset-class-specific data into canonical returns schema."""

from __future__ import annotations

from .base import CANONICAL_COLUMNS, ReturnsAdapter
from .credit import CreditAdapter
from .fx import FxAdapter

_REGISTRY: dict[str, type] = {
    "fx": FxAdapter,
    "credit": CreditAdapter,
}


def get_adapter(name: str, **params) -> ReturnsAdapter:
    """Look up adapter by name and instantiate with params."""
    cls = _REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"unknown adapter: {name!r} (available: {list(_REGISTRY)})")
    return cls(**params)


__all__ = ["CANONICAL_COLUMNS", "CreditAdapter", "ReturnsAdapter", "FxAdapter", "get_adapter"]
