import math

import pandas as pd
import numpy as np
from hypothesis import given, strategies as st

import sys
sys.path.insert(0, "repo/src")

from momentum_strategy_v1.signals import calculate_rsi


def test_calculate_rsi_case_0():
    prices = pd.Series([10, 11, 12, 11, 10, 9, 10, 11, 12, 13, 14, 13, 12, 11, 10], dtype=float)
    period = 3
    expected = [
        None,
        None,
        100.0,
        66.67,
        33.33,
        0.0,
        33.33,
        66.67,
        100.0,
        100.0,
        100.0,
        66.67,
        33.33,
        0.0,
        0.0,
    ]

    result = calculate_rsi(prices, period)
    result_list = [None if (v is None or (isinstance(v, float) and math.isnan(v))) else float(v) for v in result.tolist()]
    assert result_list == expected


@given(
    prices=st.lists(st.floats(min_value=1.0, max_value=1000.0, allow_nan=False, allow_infinity=False), min_size=5, max_size=50),
    period=st.integers(min_value=2, max_value=10),
)
def test_rsi_between_0_and_100(prices, period):
    series = pd.Series(prices, dtype=float)
    rsi = calculate_rsi(series, period)
    rsi = rsi.dropna()
    if not rsi.empty:
        assert (rsi >= 0).all()
        assert (rsi <= 100).all()


@given(
    start=st.floats(min_value=1.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    increments=st.lists(st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False), min_size=5, max_size=30),
    period=st.integers(min_value=2, max_value=10),
)
def test_rsi_non_decreasing_for_increasing_prices(start, increments, period):
    prices = [start]
    for inc in increments:
        prices.append(prices[-1] + inc)
    series = pd.Series(prices, dtype=float)
    rsi = calculate_rsi(series, period).dropna()
    if len(rsi) > 1:
        diffs = np.diff(rsi.values)
        assert (diffs >= -1e-9).all()
