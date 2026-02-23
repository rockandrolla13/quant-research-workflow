from __future__ import annotations

import numpy as np
import pandas as pd


def _ewma_covariance(returns: pd.DataFrame, decay: int) -> np.ndarray:
    if returns.empty:
        return np.zeros((0, 0))
    x = returns.values
    n = x.shape[0]
    weights = np.exp(-np.arange(n)[::-1] / decay)
    weights = weights / weights.sum()
    mean = (weights[:, None] * x).sum(axis=0)
    xc = x - mean
    cov = (xc.T * weights) @ xc / weights.sum()
    return cov


def estimate_covariance(returns: pd.DataFrame, decay_diag: int, decay_offdiag: int) -> np.ndarray:
    """Estimate EWMA covariance using 3-day non-overlapping returns, averaged over 3 offsets."""
    if not isinstance(returns, pd.DataFrame):
        raise TypeError("returns must be a DataFrame")

    covs = []
    for offset in range(3):
        subset = returns.iloc[offset::3]
        if subset.empty:
            continue
        cov = _ewma_covariance(subset, decay_offdiag)
        diag_cov = _ewma_covariance(subset, decay_diag)
        if cov.size and diag_cov.size:
            np.fill_diagonal(cov, np.diag(diag_cov))
        covs.append(cov)

    if not covs:
        return np.zeros((returns.shape[1], returns.shape[1]))
    return sum(covs) / len(covs)


def compute_asset_volatility(covariance: np.ndarray) -> pd.Series:
    """Extract per-asset volatility as sqrt of diagonal of covariance matrix."""
    diag = np.diag(covariance)
    return pd.Series(np.sqrt(np.clip(diag, 0.0, None)))


def compute_usd_pc1(returns: pd.DataFrame, pca_window: int, n_components: int) -> pd.Series:
    """Compute PC1 factor loadings from correlation matrix of returns."""
    if not isinstance(returns, pd.DataFrame):
        raise TypeError("returns must be a DataFrame")
    if n_components < 1:
        raise ValueError("n_components must be >= 1")

    window = returns.tail(pca_window).dropna()
    corr = np.corrcoef(window.values, rowvar=False)
    eigvals, eigvecs = np.linalg.eigh(corr)
    order = np.argsort(eigvals)[::-1]
    pc1 = eigvecs[:, order[0]]
    if pc1.sum() < 0:
        pc1 = -pc1
    return pd.Series(pc1, index=returns.columns)


def compute_usd_beta(returns: pd.DataFrame, lookback: int) -> pd.Series:
    """Compute rolling beta of each currency to USD PC1."""
    window = returns.tail(lookback).dropna()
    loadings = compute_usd_pc1(window, pca_window=len(window), n_components=1)
    scale = loadings.abs().sum()
    if scale > 0:
        loadings = loadings / scale
    factor = window.values @ loadings.values
    var_factor = np.var(factor)
    betas = {}
    for i, col in enumerate(window.columns):
        cov = np.cov(window.iloc[:, i].values, factor)[0, 1]
        betas[col] = cov / var_factor if var_factor > 0 else 0.0
    return pd.Series(betas)
