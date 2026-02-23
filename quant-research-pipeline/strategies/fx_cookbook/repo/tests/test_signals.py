import math

import numpy as np
import pandas as pd

import sys
sys.path.insert(0, "strategies/fx_cookbook/repo/src")

from fx_cookbook.signals import compute_momentum_signal, compute_carry_signal
from .utils import make_returns


def test_compute_momentum_signal_all_positive():
    returns = make_returns("all_positive_returns_252d")
    result = compute_momentum_signal(returns, lookback_min=21, lookback_max=252, hysteresis_threshold=0.333)
    last_date = result["date"].max()
    subset = result[result["date"] == last_date]
    assert (subset["raw_signal"] > 0.95).all()


def test_compute_momentum_signal_alternating_hysteresis():
    returns = make_returns("alternating_sign_returns")
    result = compute_momentum_signal(returns, lookback_min=21, lookback_max=252, hysteresis_threshold=0.333)

    currency = result["currency"].iloc[0]
    currency_rows = result[result["currency"] == currency].sort_values("date")
    last = currency_rows.iloc[-1]
    prev = currency_rows.iloc[-2]
    ffill_final = currency_rows["final_signal"].ffill()
    last_final = ffill_final.iloc[-1]
    prev_final = ffill_final.iloc[-2]

    assert abs(last["raw_signal"]) < 0.25
    assert last_final == prev_final


def test_compute_carry_signal():
    spot = pd.Series([1.0])
    forward = pd.Series([0.99])
    vol = pd.Series([0.1])
    signal = compute_carry_signal(spot, forward, vol)
    assert math.isclose(signal.iloc[0], (1.0 - 0.99) / 0.99 / 0.1, rel_tol=1e-3)

    spot = pd.Series([1.0])
    forward = pd.Series([1.01])
    vol = pd.Series([0.1])
    signal = compute_carry_signal(spot, forward, vol)
    assert signal.iloc[0] < 0


def test_momentum_signal_bounds():
    returns = make_returns("all_positive_returns_252d")
    result = compute_momentum_signal(returns, lookback_min=21, lookback_max=252, hysteresis_threshold=0.333)
    raw = result["raw_signal"].dropna()
    assert (raw >= -1.0).all()
    assert (raw <= 1.0).all()
