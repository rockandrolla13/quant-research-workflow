import numpy as np
import pandas as pd

import sys
sys.path.insert(0, "strategies/fx_cookbook/repo/src")

from fx_cookbook.risk import estimate_covariance, compute_asset_volatility, compute_usd_pc1
from .utils import make_returns, make_covariance


def _alpha_from_decay(decay: int) -> float:
    return 1.0 - np.exp(-1.0 / float(decay))


def _non_overlapping_returns(returns: pd.DataFrame, offset: int) -> pd.DataFrame:
    sub = returns.iloc[offset:]
    n_blocks = sub.shape[0] // 3
    if n_blocks == 0:
        return sub.iloc[:0]
    trimmed = sub.iloc[: n_blocks * 3]
    values = trimmed.values.reshape(n_blocks, 3, trimmed.shape[1]).sum(axis=1)
    index = trimmed.index[2::3]
    return pd.DataFrame(values, index=index, columns=returns.columns)


def _ewma_cov(block: pd.DataFrame, decay_diag: int, decay_offdiag: int) -> np.ndarray:
    alpha_diag = _alpha_from_decay(decay_diag)
    alpha_off = _alpha_from_decay(decay_offdiag)
    n_assets = block.shape[1]
    var = np.zeros(n_assets, dtype=float)
    corr = np.eye(n_assets, dtype=float)
    for row in block.values:
        var = var * (1.0 - alpha_diag) + (row**2) * alpha_diag
        vol = np.sqrt(np.maximum(var, 0.0))
        safe_vol = np.where(vol == 0.0, 1.0, vol)
        z = row / safe_vol
        corr = corr * (1.0 - alpha_off) + np.outer(z, z) * alpha_off
        corr = np.clip(corr, -1.0, 1.0)
    return corr * np.outer(vol, vol)


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


def test_estimate_covariance_ewma_1d_matches_manual():
    data = pd.DataFrame({"A": [0.01, -0.02, 0.03, -0.01, 0.0, 0.02, -0.01, 0.01, -0.02]})
    cov = estimate_covariance(data, decay_diag=5, decay_offdiag=10)

    cov_offsets = []
    for offset in (0, 1, 2):
        block = _non_overlapping_returns(data, offset)
        if block.empty:
            continue
        cov_offsets.append(_ewma_cov(block, decay_diag=5, decay_offdiag=10))
    expected = np.mean(cov_offsets, axis=0)

    assert np.allclose(cov, expected, atol=1e-12)


def test_estimate_covariance_psd_and_symmetric():
    rng = np.random.default_rng(0)
    returns = pd.DataFrame(rng.normal(0, 0.01, size=(120, 4)))
    cov = estimate_covariance(returns, decay_diag=252, decay_offdiag=756)
    assert np.allclose(cov, cov.T, atol=1e-10)
    eigvals = np.linalg.eigvalsh(cov)
    assert (eigvals >= -1e-10).all()


def test_estimate_covariance_three_offset_average():
    rng = np.random.default_rng(1)
    returns = pd.DataFrame(rng.normal(0, 0.01, size=(90, 3)))
    cov = estimate_covariance(returns, decay_diag=10, decay_offdiag=20)

    cov_offsets = []
    for offset in (0, 1, 2):
        block = _non_overlapping_returns(returns, offset)
        if block.empty:
            continue
        cov_offsets.append(_ewma_cov(block, decay_diag=10, decay_offdiag=20))
    expected = np.mean(cov_offsets, axis=0)

    assert np.allclose(cov, expected, atol=1e-12)
