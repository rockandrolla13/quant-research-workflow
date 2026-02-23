from __future__ import annotations

import numpy as np
import pandas as pd


def estimate_covariance(returns: pd.DataFrame, decay_diag: int, decay_offdiag: int) -> np.ndarray:
    """Estimate covariance matrix (simplified EWMA approximation)."""
    if returns.empty:
        raise ValueError("returns is empty")

    values = returns.values
    values = values - np.nanmean(values, axis=0, keepdims=True)
    cov = np.cov(values, rowvar=False, bias=False)
    return cov


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
