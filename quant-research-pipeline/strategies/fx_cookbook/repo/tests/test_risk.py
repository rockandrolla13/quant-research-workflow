import numpy as np

import sys
sys.path.insert(0, "strategies/fx_cookbook/repo/src")

from fx_cookbook.risk import estimate_covariance, compute_asset_volatility, compute_usd_pc1
from .utils import make_returns, make_covariance


def test_compute_asset_volatility_identity():
    cov = make_covariance("identity_matrix_scaled_0.04")
    vol = compute_asset_volatility(cov)
    assert np.allclose(vol.values, 0.2)


def test_compute_asset_volatility_varied():
    cov = make_covariance("diagonal_matrix_varied")
    vol = compute_asset_volatility(cov)
    assert np.allclose(vol.values, [0.1, 0.2, 0.3])


def test_compute_usd_pc1_perfect_corr():
    returns = make_returns("perfectly_correlated_24_pairs")
    pc1 = compute_usd_pc1(returns, pca_window=252, n_components=1)
    explained = pc1.attrs.get("explained_variance_ratio", 0.0)
    assert explained > 0.99
    assert (np.sign(pc1) == np.sign(pc1.iloc[0])).all()


def test_compute_usd_pc1_independent():
    returns = make_returns("independent_noise_24_pairs")
    pc1 = compute_usd_pc1(returns, pca_window=252, n_components=1)
    explained = pc1.attrs.get("explained_variance_ratio", 0.0)
    assert 0.02 < explained < 0.08
    assert np.std(np.abs(pc1.values)) < 0.2


def test_estimate_covariance_identity_corr():
    returns = make_returns("identity_corr_returns")
    cov = estimate_covariance(returns, decay_diag=252, decay_offdiag=756)
    off_diag = cov - np.diag(np.diag(cov))
    assert np.abs(off_diag).mean() < 0.01


def test_estimate_covariance_perfect_pair():
    returns = make_returns("perfectly_correlated_pair")
    cov = estimate_covariance(returns, decay_diag=252, decay_offdiag=756)
    corr = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
    assert corr > 0.95
