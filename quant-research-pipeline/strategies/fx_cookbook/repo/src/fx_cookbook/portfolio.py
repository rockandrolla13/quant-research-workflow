from __future__ import annotations

import numpy as np
import pandas as pd


def build_ts_weights(signals: pd.DataFrame, volatilities: pd.DataFrame, max_position: float) -> pd.DataFrame:
    """Build time-series portfolio weights using inverse volatility weighting."""
    if signals.shape != volatilities.shape:
        raise ValueError("signals and volatilities must have same shape")

    raw = signals / volatilities.replace(0, np.nan)
    weights = raw.copy()

    abs_sum = weights.abs().sum(axis=1)
    abs_sum = abs_sum.replace(0, np.nan)
    weights = weights.div(abs_sum, axis=0)

    if max_position is not None:
        weights = weights.clip(lower=-max_position, upper=max_position)

    return weights.fillna(0.0)


def build_cs_weights(signals: pd.DataFrame, betas: pd.Series, max_position: float) -> pd.DataFrame:
    """Build cross-sectional weights with beta-neutralisation to USD PC1."""
    weights = pd.DataFrame(index=signals.index, columns=signals.columns, dtype=float)

    for idx, row in signals.iterrows():
        w = pd.Series(0.0, index=row.index)
        if row.nunique(dropna=True) <= 1:
            w[:] = 1.0 / len(row)
        else:
            ranked = row.rank(method="first")
            n = len(ranked)
            cutoff = n // 2
            longs = ranked > cutoff
            shorts = ranked <= cutoff
            if longs.any():
                w.loc[longs] = 1.0 / longs.sum()
            if shorts.any():
                w.loc[shorts] = -1.0 / shorts.sum()

        beta = betas.reindex(w.index).fillna(0.0)
        for _ in range(2):
            denom = float((beta**2).sum())
            if denom > 0:
                adjustment = (beta * (beta.dot(w) / denom))
                w = w - adjustment

            abs_sum = w.abs().sum()
            if abs_sum > 0:
                w = w / abs_sum

        weights.loc[idx] = w

    return weights.fillna(0.0)


def apply_tranching(target_weights: pd.DataFrame, n_tranches: int) -> pd.DataFrame:
    """Split target into n_tranches sub-portfolios, each rebalanced on different days."""
    if n_tranches <= 0:
        raise ValueError("n_tranches must be positive")

    tranches = []
    for offset in range(n_tranches):
        tranche = target_weights.copy()
        mask = np.arange(len(tranche)) % n_tranches != offset
        tranche.loc[mask] = np.nan
        tranche = tranche.ffill().fillna(0.0)
        tranches.append(tranche)

    return sum(tranches) / float(n_tranches)
