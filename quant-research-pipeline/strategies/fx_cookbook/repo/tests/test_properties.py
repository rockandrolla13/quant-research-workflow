import numpy as np
import pandas as pd
from hypothesis import HealthCheck, given, settings, strategies as st

import sys
sys.path.insert(0, "strategies/fx_cookbook/repo/src")

from fx_cookbook.portfolio import build_ts_weights, build_cs_weights
from fx_cookbook.signals import compute_momentum_signal
from fx_cookbook.validation import go_no_go


@given(
    st.lists(st.lists(st.floats(min_value=0.1, max_value=2.0), min_size=3, max_size=3), min_size=5, max_size=10),
    st.lists(st.lists(st.floats(min_value=0.1, max_value=1.0), min_size=3, max_size=3), min_size=5, max_size=10),
)
def test_ts_weights_abs_sum_one(signals_data, vol_data):
    n = min(len(signals_data), len(vol_data))
    dates = pd.date_range("2000-01-01", periods=n, freq="B")
    signals = pd.DataFrame(signals_data[:n], index=dates, columns=["A", "B", "C"])
    vol = pd.DataFrame(vol_data[:n], index=dates, columns=["A", "B", "C"])
    weights = build_ts_weights(signals, vol, max_position=1.0)
    abs_sum = weights.abs().sum(axis=1)
    assert np.allclose(abs_sum.values, 1.0)


@given(
    st.lists(st.lists(st.floats(min_value=-1.0, max_value=1.0), min_size=4, max_size=4), min_size=3, max_size=6),
    st.lists(st.floats(min_value=0.5, max_value=1.5), min_size=4, max_size=4),
)
def test_cs_weights_beta_neutral(signals_data, betas_list):
    dates = pd.date_range("2000-01-01", periods=len(signals_data), freq="B")
    signals = pd.DataFrame(signals_data, index=dates, columns=["A", "B", "C", "D"])
    betas = pd.Series(betas_list, index=["A", "B", "C", "D"])
    weights = build_cs_weights(signals, betas, max_position=0.5)
    exposure = (weights * betas).sum(axis=1)
    assert np.all(np.abs(exposure.values) < 0.01)


@given(
    st.lists(st.lists(st.floats(min_value=-2.0, max_value=2.0), min_size=3, max_size=3), min_size=5, max_size=10),
    st.lists(st.lists(st.floats(min_value=0.1, max_value=1.0), min_size=3, max_size=3), min_size=5, max_size=10),
    st.floats(min_value=0.05, max_value=0.5),
)
def test_positions_capped(signals_data, vol_data, max_pos):
    n = min(len(signals_data), len(vol_data))
    dates = pd.date_range("2000-01-01", periods=n, freq="B")
    signals = pd.DataFrame(signals_data[:n], index=dates, columns=["A", "B", "C"])
    vol = pd.DataFrame(vol_data[:n], index=dates, columns=["A", "B", "C"])
    weights = build_ts_weights(signals, vol, max_position=max_pos)
    assert (weights.abs() <= max_pos + 1e-9).all().all()


@given(
    st.lists(st.lists(st.floats(min_value=-0.02, max_value=0.02), min_size=3, max_size=3), min_size=260, max_size=300)
)
@settings(suppress_health_check=[HealthCheck.large_base_example], deadline=None)
def test_momentum_signal_bounds(returns_data):
    dates = pd.date_range("2000-01-01", periods=len(returns_data), freq="B")
    returns = pd.DataFrame(returns_data, index=dates, columns=["A", "B", "C"])
    result = compute_momentum_signal(returns, lookback_min=21, lookback_max=60, hysteresis_threshold=0.333)
    raw = result["raw_signal"].dropna()
    assert (raw >= -1.0).all() and (raw <= 1.0).all()


@given(
    st.booleans(),
    st.lists(st.booleans(), min_size=1, max_size=5),
)
def test_go_no_go_logic(hypothesis_pass, criteria_passes):
    hypothesis_result = {"reject_h0": hypothesis_pass}
    criteria_results = [{"pass": v} for v in criteria_passes]
    decision = go_no_go(hypothesis_result, criteria_results)
    expected = "GO" if (hypothesis_pass and all(criteria_passes)) else "NO_GO"
    assert decision["decision"] == expected
