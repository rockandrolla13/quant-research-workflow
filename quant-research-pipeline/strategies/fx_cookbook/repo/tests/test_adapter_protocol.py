"""Contract tests: any adapter output must satisfy canonical schema."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from fx_cookbook.adapters.base import CANONICAL_COLUMNS


def _make_canonical_df() -> pd.DataFrame:
    """Minimal valid canonical DataFrame."""
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2020-01-02", "2020-01-03"]),
            "asset": ["EURUSD", "EURUSD"],
            "total_return": [0.001, -0.002],
            "bid_ask_spread": [0.0002, 0.0002],
        }
    )


def validate_canonical_schema(df: pd.DataFrame) -> None:
    """Assert that df satisfies the canonical returns schema."""
    for col in CANONICAL_COLUMNS:
        assert col in df.columns, f"missing canonical column: {col}"
    assert pd.api.types.is_datetime64_any_dtype(df["date"]), "date must be datetime"
    assert pd.api.types.is_object_dtype(df["asset"]) or pd.api.types.is_string_dtype(df["asset"]), "asset must be string"
    assert pd.api.types.is_float_dtype(df["total_return"]), "total_return must be float"
    assert pd.api.types.is_float_dtype(df["bid_ask_spread"]), "bid_ask_spread must be float"


def test_canonical_columns_defined():
    assert CANONICAL_COLUMNS == ["date", "asset", "total_return", "bid_ask_spread"]


def test_valid_canonical_df_passes():
    df = _make_canonical_df()
    validate_canonical_schema(df)


def test_missing_column_fails():
    df = _make_canonical_df().drop(columns=["total_return"])
    with pytest.raises(AssertionError, match="missing canonical column"):
        validate_canonical_schema(df)


def test_extra_columns_allowed():
    df = _make_canonical_df()
    df["spot_rate"] = 1.1
    validate_canonical_schema(df)
