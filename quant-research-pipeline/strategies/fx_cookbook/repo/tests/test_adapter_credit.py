"""Tests for CreditAdapter."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from fx_cookbook.adapters.credit import CreditAdapter
from fx_cookbook.adapters.base import CANONICAL_COLUMNS


def _make_credit_raw(spread_unit_bps: bool = True) -> pd.DataFrame:
    """Minimal credit data: 2 bonds, 4 dates.

    Spreads in basis points by default (e.g. 150 = 1.50%).
    """
    dates = pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06", "2020-01-07"])
    return pd.DataFrame(
        {
            "date": list(dates) * 2,
            "bond_id": ["AAPL_5Y"] * 4 + ["MSFT_5Y"] * 4,
            "spread": [150.0, 155.0, 148.0, 152.0,   # AAPL: +5, -7, +4 bp changes
                       200.0, 195.0, 190.0, 192.0],   # MSFT: -5, -5, +2 bp changes
            "duration": [4.5] * 4 + [5.0] * 4,
            "bid_ask": [5.0] * 4 + [8.0] * 4,  # 5bp and 8bp bid-ask
        }
    )


class TestCreditAdapterCanonical:
    def test_output_has_canonical_columns(self):
        adapter = CreditAdapter()
        result = adapter.adapt(_make_credit_raw())
        for col in CANONICAL_COLUMNS:
            assert col in result.columns, f"missing: {col}"

    def test_bond_id_renamed_to_asset(self):
        adapter = CreditAdapter()
        result = adapter.adapt(_make_credit_raw())
        assert "asset" in result.columns
        assert "bond_id" not in result.columns

    def test_assets_preserved(self):
        adapter = CreditAdapter()
        result = adapter.adapt(_make_credit_raw())
        assert set(result["asset"]) == {"AAPL_5Y", "MSFT_5Y"}


class TestCreditReturnCalculation:
    def test_first_observation_is_nan(self):
        """First observation per bond has no Δspread, so total_return is NaN."""
        adapter = CreditAdapter()
        result = adapter.adapt(_make_credit_raw())
        aapl = result[result["asset"] == "AAPL_5Y"].sort_values("date")
        assert np.isnan(aapl["total_return"].iloc[0])

    def test_spread_widening_negative_return(self):
        """When spread widens (+5bp), return should be negative (before carry)."""
        adapter = CreditAdapter()
        result = adapter.adapt(_make_credit_raw())
        aapl = result[result["asset"] == "AAPL_5Y"].sort_values("date")
        # Day 2: spread 150→155 (+5bp), duration=4.5
        # MTM = -4.5 * 5 * 0.0001 = -0.00225
        # Carry = 155 * 0.0001 / 252 ≈ 0.0000615
        # Total ≈ -0.00219 (negative)
        assert aapl["total_return"].iloc[1] < 0

    def test_spread_tightening_positive_return(self):
        """When spread tightens (-5bp), return should be positive."""
        adapter = CreditAdapter()
        result = adapter.adapt(_make_credit_raw())
        msft = result[result["asset"] == "MSFT_5Y"].sort_values("date")
        # Day 2: spread 200→195 (-5bp), duration=5.0
        # MTM = -5.0 * (-5) * 0.0001 = +0.0025
        # Carry = 195 * 0.0001 / 252 ≈ 0.0000774
        # Total ≈ +0.00258 (positive)
        assert msft["total_return"].iloc[1] > 0

    def test_return_magnitude(self):
        """Verify return calculation against manual computation."""
        adapter = CreditAdapter(bdays_per_year=252, spread_unit=0.0001)
        result = adapter.adapt(_make_credit_raw())
        aapl = result[result["asset"] == "AAPL_5Y"].sort_values("date")

        # Day 2: Δspread = +5bp, duration = 4.5, spread = 155bp
        delta_spread = 5.0 * 0.0001  # 0.0005
        mtm = -4.5 * delta_spread    # -0.00225
        carry = 155.0 * 0.0001 / 252  # ~0.0000615
        expected = mtm + carry

        assert np.isclose(aapl["total_return"].iloc[1], expected, atol=1e-8)

    def test_carry_always_positive_for_positive_spread(self):
        """Carry component should be positive when spread > 0."""
        adapter = CreditAdapter()
        result = adapter.adapt(_make_credit_raw())
        # All spreads are positive, so carry contribution is always positive.
        # We can't isolate carry easily, but with zero spread change, return = carry > 0.
        # Use a custom dataset with no spread change:
        raw = pd.DataFrame({
            "date": pd.to_datetime(["2020-01-02", "2020-01-03"]),
            "bond_id": ["TEST"] * 2,
            "spread": [100.0, 100.0],  # No change
            "duration": [5.0, 5.0],
            "bid_ask": [5.0, 5.0],
        })
        result = adapter.adapt(raw)
        test = result[result["asset"] == "TEST"].sort_values("date")
        # Return should be pure carry = 100bp * 0.0001 / 252
        expected_carry = 100.0 * 0.0001 / 252
        assert np.isclose(test["total_return"].iloc[1], expected_carry, atol=1e-10)


class TestCreditAdapterBidAsk:
    def test_bid_ask_converted(self):
        adapter = CreditAdapter(spread_unit=0.0001)
        result = adapter.adapt(_make_credit_raw())
        aapl = result[result["asset"] == "AAPL_5Y"]
        # 5bp * 0.0001 = 0.0005
        assert np.isclose(aapl["bid_ask_spread"].iloc[0], 5.0 * 0.0001)

    def test_spread_unit_decimal(self):
        """If spreads are already in decimal, spread_unit=1.0."""
        raw = pd.DataFrame({
            "date": pd.to_datetime(["2020-01-02", "2020-01-03"]),
            "bond_id": ["TEST"] * 2,
            "spread": [0.0150, 0.0155],  # Already decimal
            "duration": [5.0, 5.0],
            "bid_ask": [0.0005, 0.0005],
        })
        adapter = CreditAdapter(spread_unit=1.0)
        result = adapter.adapt(raw)
        assert np.isclose(result["bid_ask_spread"].iloc[0], 0.0005)


class TestCreditAdapterValidation:
    def test_missing_required_column_raises(self):
        raw = _make_credit_raw().drop(columns=["duration"])
        adapter = CreditAdapter()
        with pytest.raises(ValueError, match="duration"):
            adapter.adapt(raw)

    def test_does_not_mutate_input(self):
        raw = _make_credit_raw()
        original_cols = list(raw.columns)
        adapter = CreditAdapter()
        adapter.adapt(raw)
        assert list(raw.columns) == original_cols
        assert "asset" not in raw.columns
