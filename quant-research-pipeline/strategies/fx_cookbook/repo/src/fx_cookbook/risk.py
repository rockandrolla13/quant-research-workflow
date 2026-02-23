from __future__ import annotations

import numpy as np
import pandas as pd


def _alpha_from_decay(decay: int) -> float:
    if decay <= 0:
        raise ValueError("decay must be positive")
    return 1.0 - np.exp(-1.0 / float(decay))


def _non_overlapping_returns(returns: pd.DataFrame, offset: int) -> pd.DataFrame:
    """Aggregate to non-overlapping 3-day returns using a given starting offset."""
    if offset < 0 or offset > 2:
        raise ValueError("offset must be 0, 1, or 2")
    sub = returns.iloc[offset:]
    n_blocks = sub.shape[0] // 3
    if n_blocks == 0:
        return sub.iloc[:0]
    trimmed = sub.iloc[: n_blocks * 3]
    values = trimmed.values.reshape(n_blocks, 3, trimmed.shape[1]).sum(axis=1)
    index = trimmed.index[2::3]
    return pd.DataFrame(values, index=index, columns=returns.columns)


def estimate_covariance(returns: pd.DataFrame, decay_diag: int, decay_offdiag: int) -> np.ndarray:
    """Estimate EWMA covariance with 3-offset averaging to reduce discretisation bias."""
    if returns.empty:
        raise ValueError("returns is empty")

    alpha_diag = _alpha_from_decay(decay_diag)
    alpha_off = _alpha_from_decay(decay_offdiag)

    covariances = []
    for offset in (0, 1, 2):
        block = _non_overlapping_returns(returns, offset)
        if block.empty:
            continue

        n_assets = block.shape[1]
        var = np.zeros(n_assets, dtype=float)
        corr = np.eye(n_assets, dtype=float)

        # "offset" defines the starting day for the 3-day non-overlapping blocks.
        # Averaging across offsets reduces discretisation bias from arbitrary start dates.
        for row in block.values:
            var = var * (1.0 - alpha_diag) + (row**2) * alpha_diag
            vol = np.sqrt(np.maximum(var, 0.0))
            safe_vol = np.where(vol == 0.0, 1.0, vol)
            z = row / safe_vol

            corr = corr * (1.0 - alpha_off) + np.outer(z, z) * alpha_off
            corr = np.clip(corr, -1.0, 1.0)

        cov = corr * np.outer(vol, vol)
        covariances.append(cov)

    if not covariances:
        return np.zeros((returns.shape[1], returns.shape[1]), dtype=float)

    return np.mean(covariances, axis=0)


def compute_asset_volatility(covariance: np.ndarray) -> pd.Series:
    """Extract per-asset volatility as sqrt of diagonal of covariance matrix."""
    diag = np.diag(covariance)
    vol = np.sqrt(np.maximum(diag, 0))
    return pd.Series(vol)


def compute_usd_pc1(returns: pd.DataFrame, pca_window: int, n_components: int) -> pd.Series:
    """Compute PC1 factor loadings from correlation matrix of returns."""
    if returns.shape[0] < 2:
        raise ValueError("returns must have at least 2 rows")

    windowed = returns.tail(pca_window)
    corr = windowed.corr().values
    eigvals, eigvecs = np.linalg.eigh(corr)
    order = np.argsort(eigvals)[::-1]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]

    pc1 = eigvecs[:, 0]
    if pc1.sum() < 0:
        pc1 = -pc1

    explained = float(eigvals[0] / eigvals.sum()) if eigvals.sum() > 0 else 0.0
    series = pd.Series(pc1, index=returns.columns)
    series.attrs["explained_variance_ratio"] = explained
    return series


def compute_usd_beta(returns: pd.DataFrame, lookback: int) -> pd.Series:
    """Compute rolling beta of each currency to USD PC1."""
    loadings = compute_usd_pc1(returns, pca_window=lookback, n_components=1)
    factor = returns.dot(loadings)
    windowed = returns.tail(lookback)
    factor = factor.tail(lookback)

    betas = {}
    factor_var = factor.var()
    for col in windowed.columns:
        cov = windowed[col].cov(factor)
        betas[col] = cov / factor_var if factor_var != 0 else 0.0

    return pd.Series(betas)
