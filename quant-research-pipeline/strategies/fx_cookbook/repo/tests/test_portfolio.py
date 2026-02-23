import sys
sys.path.insert(0, "strategies/fx_cookbook/repo/src")

import pytest

from fx_cookbook.portfolio import build_cs_weights
from .utils import make_signals, make_betas


def test_build_cs_weights_beta_neutral():
    signals = make_signals("monotonic_ranking")
    betas = make_betas("uniform_betas")
    weights = build_cs_weights(signals, betas, max_position=0.15)

    w = weights.iloc[0]
    beta_exposure = float((w * betas).sum())
    assert abs(beta_exposure) < 1e-6
    assert abs(w).sum() == pytest.approx(1.0, rel=1e-6)


def test_build_cs_weights_equal_signals():
    signals = make_signals("all_equal")
    betas = make_betas("varied_betas")
    weights = build_cs_weights(signals, betas, max_position=0.15)

    w = weights.iloc[0]
    beta_exposure = float((w * betas).sum())
    assert abs(beta_exposure) < 1e-6
    assert abs(w).sum() == pytest.approx(1.0, rel=1e-6)
