from __future__ import annotations

import numpy as np
import pandas as pd


def build_ts_weights(signals: pd.DataFrame, volatilities: pd.DataFrame, max_position: float) -> pd.DataFrame:
    """Build time-series portfolio weights using inverse volatility weighting."""
    if not isinstance(signals, pd.DataFrame) or not isinstance(volatilities, pd.DataFrame):
        raise TypeError("signals and volatilities must be DataFrames")

    vol = volatilities.replace(0.0, np.nan)
    weights = signals.div(vol)
    weights = weights.replace([np.inf, -np.inf], 0.0).fillna(0.0)

    abs_sum = weights.abs().sum(axis=1)
    weights = weights.div(abs_sum.replace(0.0, 1.0), axis=0)
    zero_rows = abs_sum == 0.0
    if zero_rows.any():
        n_assets = weights.shape[1]
        weights.loc[zero_rows] = 1.0 / n_assets

    # Apply caps and redistribute to maintain abs-sum of 1 when possible.
    adjusted = weights.copy()
    for idx, row in weights.iterrows():
        w = row.copy()
        over = w.abs() > max_position
        w[over] = w[over].apply(lambda x: np.sign(x) * max_position)
        remaining = 1.0 - w.abs().sum()
        if remaining > 1e-12:
            capacity = (max_position - w.abs()).clip(lower=0.0)
            total_cap = capacity.sum()
            if total_cap > 0:
                alloc = capacity / total_cap * remaining
                w = w + np.sign(w.replace(0.0, 1.0)) * alloc
        adjusted.loc[idx] = w

    return adjusted


def build_cs_weights(signals: pd.DataFrame, betas: pd.Series, max_position: float) -> pd.DataFrame:
    """Build cross-sectional weights: long top half, short bottom half, beta-neutralise to USD PC1."""
    if not isinstance(signals, pd.DataFrame):
        raise TypeError("signals must be a DataFrame")
    if not isinstance(betas, pd.Series):
        raise TypeError("betas must be a Series")

    weights = pd.DataFrame(index=signals.index, columns=signals.columns, dtype=float)
    for idx, row in signals.iterrows():
        ranked = row.sort_values(ascending=False)
        n = len(ranked)
        half = n // 2
        long_assets = ranked.index[:half]
        short_assets = ranked.index[half:]
        w = pd.Series(0.0, index=signals.columns)
        if len(long_assets) > 0:
            w.loc[long_assets] = 1.0 / len(long_assets)
        if len(short_assets) > 0:
            w.loc[short_assets] = -1.0 / len(short_assets)

        beta_slice = betas.reindex(w.index).fillna(0.0)
        beta_exposure = float((w * beta_slice).sum())
        beta_denom = float((beta_slice**2).sum())
        if beta_denom > 0:
            k = beta_exposure / beta_denom
            w = w - k * beta_slice

        abs_sum = w.abs().sum() if w.abs().sum() != 0 else 1.0
        w = w / abs_sum
        w = w.clip(lower=-max_position, upper=max_position)
        if w.abs().sum() != 0:
            w = w / w.abs().sum()
        weights.loc[idx] = w

    return weights


def apply_tranching(target_weights: pd.DataFrame, n_tranches: int) -> pd.DataFrame:
    """Split target into n_tranches sub-portfolios, each rebalanced on different days."""
    if n_tranches <= 0:
        raise ValueError("n_tranches must be positive")
    if not isinstance(target_weights, pd.DataFrame):
        raise TypeError("target_weights must be a DataFrame")

    tranches = []
    for i in range(n_tranches):
        tranche = target_weights.iloc[i::n_tranches].copy()
        tranche = tranche.reindex(target_weights.index).ffill().fillna(0.0)
        tranches.append(tranche)

    combined = sum(tranches) / n_tranches
    return combined
