import numpy as np
import pandas as pd
import sys

sys.path.insert(0, "repo/src")

from fx_cookbook.risk import estimate_covariance, compute_asset_volatility, compute_usd_pc1, compute_usd_beta
from conftest import make_perfectly_correlated, make_independent_noise


def test_compute_asset_volatility_identity():
    cov = np.eye(3) * 0.04
    vols = compute_asset_volatility(cov)
    assert np.allclose(vols.values, 0.2)


def test_compute_asset_volatility_varied():
    cov = np.diag([0.01, 0.04, 0.09])
    vols = compute_asset_volatility(cov)
    assert np.allclose(vols.values, [0.1, 0.2, 0.3])


def test_compute_usd_pc1_perfect_corr():
    returns = make_perfectly_correlated()
    loadings = compute_usd_pc1(returns, pca_window=252, n_components=1)
    assert (np.sign(loadings).sum() == len(loadings)) or (np.sign(loadings).sum() == -len(loadings))


def test_compute_usd_pc1_independent():
    returns = make_independent_noise()
    loadings = compute_usd_pc1(returns, pca_window=252, n_components=1)
    assert np.isfinite(loadings).all()


def test_estimate_covariance_identity_corr():
    returns = make_independent_noise(n_days=252, n_assets=4)
    cov = estimate_covariance(returns, decay_diag=252, decay_offdiag=756)
    offdiag = cov - np.diag(np.diag(cov))
    assert np.allclose(offdiag, 0.0, atol=1e-2)


def test_estimate_covariance_perfect_pair():
    base = np.linspace(0.0, 0.01, 300)
    returns = pd.DataFrame({"A": base, "B": base, "C": np.random.normal(0, 0.01, size=300)})
    cov = estimate_covariance(returns, decay_diag=252, decay_offdiag=756)
    corr = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
    assert corr > 0.9


def test_compute_usd_beta_basic():
    returns = make_perfectly_correlated(n_days=300, n_assets=5)
    betas = compute_usd_beta(returns, lookback=252)
    assert (betas > 0.4).all()
