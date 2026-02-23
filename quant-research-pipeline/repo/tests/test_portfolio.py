import numpy as np
import pandas as pd
import sys
from hypothesis import given, strategies as st

sys.path.insert(0, "repo/src")

from fx_cookbook.portfolio import build_ts_weights, build_cs_weights, apply_tranching


def test_build_cs_weights_beta_neutral_monotonic():
    signals = pd.DataFrame([np.arange(1, 25)], columns=[f"C{i}" for i in range(24)])
    betas = pd.Series(1.0, index=signals.columns)
    weights = build_cs_weights(signals, betas, max_position=0.15)
    exposure = float((weights.iloc[0] * betas).sum())
    assert abs(exposure) < 1e-6
    assert abs(weights.iloc[0].abs().sum() - 1.0) < 1e-6


def test_build_cs_weights_equal_signals():
    signals = pd.DataFrame([np.ones(24)], columns=[f"C{i}" for i in range(24)])
    betas = pd.Series([0.5, 1.0, 1.5, 0.5, 1.0, 1.5] * 4, index=signals.columns)
    weights = build_cs_weights(signals, betas, max_position=0.15)
    exposure = float((weights.iloc[0] * betas).sum())
    assert abs(exposure) < 1e-6


def test_apply_tranching_shape():
    target = pd.DataFrame(np.arange(20).reshape(10, 2), columns=["A", "B"])
    tr = apply_tranching(target, n_tranches=2)
    assert tr.shape == target.shape


@given(
    signals=st.lists(st.lists(st.floats(min_value=-1, max_value=1), min_size=24, max_size=24), min_size=5, max_size=5),
    vols=st.lists(st.lists(st.floats(min_value=0.01, max_value=1.0), min_size=24, max_size=24), min_size=5, max_size=5),
)
def test_ts_weights_abs_sum_and_caps(signals, vols):
    signals_df = pd.DataFrame(signals, columns=[f"C{i}" for i in range(24)])
    vols_df = pd.DataFrame(vols, columns=[f"C{i}" for i in range(24)])
    weights = build_ts_weights(signals_df, vols_df, max_position=0.15)
    abs_sum = weights.abs().sum(axis=1)
    assert np.allclose(abs_sum.values, 1.0, atol=1e-6)
    assert (weights.abs() <= 0.15 + 1e-9).all().all()


@given(
    signals=st.lists(st.lists(st.floats(min_value=-1, max_value=1), min_size=6, max_size=6), min_size=3, max_size=3),
    betas=st.lists(st.floats(min_value=0.5, max_value=1.5), min_size=6, max_size=6),
)
def test_cs_weights_beta_neutral_property(signals, betas):
    signals_df = pd.DataFrame(signals, columns=[f"C{i}" for i in range(6)])
    betas_s = pd.Series(betas, index=signals_df.columns)
    weights = build_cs_weights(signals_df, betas_s, max_position=1.0)
    exposure = (weights * betas_s).sum(axis=1).abs()
    assert (exposure <= 0.01 + 1e-6).all()
