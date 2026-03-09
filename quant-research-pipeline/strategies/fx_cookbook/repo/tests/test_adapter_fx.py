"""Tests for FxAdapter."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from fx_cookbook.adapters.fx import FxAdapter
from fx_cookbook.adapters.base import CANONICAL_COLUMNS


def _make_fx_raw() -> pd.DataFrame:
    """Minimal FX raw data with 2 pairs, 3 dates."""
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06"] * 2),
            "currency_pair": ["EURUSD"] * 3 + ["GBPUSD"] * 3,
            "spot_rate": [1.10, 1.11, 1.12, 1.30, 1.31, 1.32],
            "forward_1m": [1.099, 1.109, 1.119, 1.299, 1.309, 1.319],
            "forward_6m": [1.095, 1.105, 1.115, 1.295, 1.305, 1.315],
            "bid_ask_spread": [0.0002] * 3 + [0.0003] * 3,
        }
    )


class TestFxAdapterCanonical:
    def test_output_has_canonical_columns(self):
        adapter = FxAdapter()
        result = adapter.adapt(_make_fx_raw())
        for col in CANONICAL_COLUMNS:
            assert col in result.columns, f"missing: {col}"

    def test_currency_pair_renamed_to_asset(self):
        adapter = FxAdapter()
        result = adapter.adapt(_make_fx_raw())
        assert "asset" in result.columns
        assert "currency_pair" not in result.columns

    def test_total_return_computed(self):
        adapter = FxAdapter()
        result = adapter.adapt(_make_fx_raw())
        assert result["total_return"].notna().any()

    def test_preserves_extra_columns(self):
        raw = _make_fx_raw()
        raw["forward_6m"] = 1.0
        adapter = FxAdapter()
        result = adapter.adapt(raw)
        assert "forward_6m" in result.columns


class TestFxAdapterQuoteConvention:
    def test_usd_per_fx_is_identity(self):
        adapter = FxAdapter(quote_convention="USD_per_FX")
        raw = _make_fx_raw()
        result = adapter.adapt(raw)
        # spot_rate should be unchanged
        assert np.isclose(result["spot_rate"].iloc[0], 1.10)

    def test_fx_per_usd_inverts_rates(self):
        adapter = FxAdapter(quote_convention="FX_per_USD")
        raw = _make_fx_raw()
        result = adapter.adapt(raw)
        assert np.isclose(result["spot_rate"].iloc[0], 1.0 / 1.10, atol=1e-6)

    def test_unknown_convention_raises(self):
        adapter = FxAdapter(quote_convention="INVALID")
        with pytest.raises(ValueError, match="unknown quote_convention"):
            adapter.adapt(_make_fx_raw())


class TestFxAdapterValidation:
    def test_missing_required_column_raises(self):
        raw = _make_fx_raw().drop(columns=["spot_rate"])
        adapter = FxAdapter()
        with pytest.raises(ValueError, match="spot_rate"):
            adapter.adapt(raw)

    def test_does_not_mutate_input(self):
        raw = _make_fx_raw()
        original_cols = list(raw.columns)
        adapter = FxAdapter()
        adapter.adapt(raw)
        assert list(raw.columns) == original_cols
        assert "asset" not in raw.columns
