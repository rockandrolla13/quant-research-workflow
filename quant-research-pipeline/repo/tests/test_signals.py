import numpy as np
import pandas as pd
import sys

sys.path.insert(0, "repo/src")

from fx_cookbook.signals import compute_momentum_signal, compute_carry_signal, compute_mso_signal
from conftest import make_returns_all_positive, make_returns_alternating


def test_compute_momentum_signal_all_positive():
    returns = make_returns_all_positive(days=252, n_assets=4)
    result = compute_momentum_signal(returns, lookback_min=21, lookback_max=252, hysteresis_threshold=0.333)
    latest = result[result["date"] == returns.index[-1]]
    assert (latest["raw_signal"] > 0.9).all()


def test_compute_momentum_signal_alternating_hysteresis():
    returns = make_returns_alternating(days=252, n_assets=4)
    result = compute_momentum_signal(returns, lookback_min=21, lookback_max=252, hysteresis_threshold=0.333)
    latest = result[result["date"] == returns.index[-1]]
    assert (latest["raw_signal"].abs() < 0.1).all()


def test_compute_carry_signal_positive_negative():
    carry = compute_carry_signal(spot=1.0, forward=0.99, volatility=0.10)
    assert abs(float(carry.iloc[-1]) - 0.1010101) < 1e-3

    carry_neg = compute_carry_signal(spot=1.0, forward=1.01, volatility=0.10)
    assert float(carry_neg.iloc[-1]) < 0


def test_compute_mso_signal_basic():
    ir_spread = pd.Series([0.0, 0.1, 0.2, 0.3, 0.4])
    signal = compute_mso_signal(ir_spread, windows=[2, 3])
    assert signal.isna().sum() > 0
    assert signal.dropna().iloc[-1] > 0


def test_momentum_signal_bounded_before_dispersion_deflation():
    returns = make_returns_all_positive(days=252, n_assets=4)
    result = compute_momentum_signal(returns, lookback_min=21, lookback_max=252, hysteresis_threshold=0.333)
    assert (result["raw_signal"] <= 1.0 + 1e-9).all()
    assert (result["raw_signal"] >= -1.0 - 1e-9).all()
