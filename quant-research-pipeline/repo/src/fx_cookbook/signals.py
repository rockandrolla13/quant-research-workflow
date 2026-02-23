from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from .spec_models import load_config


def compute_momentum_signal(
    returns: pd.DataFrame,
    lookback_min: int,
    lookback_max: int,
    hysteresis_threshold: float,
) -> pd.DataFrame:
    """Compute momentum signal for all currencies."""
    if not isinstance(returns, pd.DataFrame):
        raise TypeError("returns must be a DataFrame")
    if lookback_min <= 0 or lookback_max <= 0:
        raise ValueError("lookback windows must be positive")
    if lookback_min > lookback_max:
        raise ValueError("lookback_min must be <= lookback_max")

    mean_max = returns.rolling(lookback_max, min_periods=lookback_max).mean()
    std_max = returns.rolling(lookback_max, min_periods=lookback_max).std().replace(0.0, 1e-8)
    raw_score = mean_max / std_max
    raw_signal = raw_score.apply(np.tanh).clip(-1.0, 1.0)

    dispersion = raw_signal.std(axis=1).fillna(0.0)
    floor = dispersion.quantile(0.25) if len(dispersion) else 0.0
    denom = dispersion.where(dispersion >= floor, floor).replace(0.0, 1.0)
    final_signal = raw_signal.div(denom, axis=0).clip(-1.0, 1.0)

    for col in final_signal.columns:
        prev = 0.0
        for idx in final_signal.index:
            raw_val = raw_signal.loc[idx, col]
            if pd.isna(raw_val):
                continue
            if abs(raw_val) < hysteresis_threshold:
                final_signal.loc[idx, col] = prev
            else:
                prev = float(final_signal.loc[idx, col])

    stacked_raw = raw_signal.stack().rename("raw_signal").reset_index()
    stacked_raw = stacked_raw.rename(columns={"level_0": "date", "level_1": "currency"})
    stacked_raw["dispersion"] = stacked_raw["date"].map(dispersion)
    stacked_raw["final_signal"] = final_signal.stack().values

    return stacked_raw[["date", "currency", "raw_signal", "dispersion", "final_signal"]]


def _ensure_series(value) -> pd.Series:
    if isinstance(value, pd.Series):
        return value
    return pd.Series([value], dtype=float)


def compute_carry_signal(spot: pd.Series, forward: pd.Series, volatility: pd.Series) -> pd.Series:
    """Compute carry signal: (spot - forward) / forward, smoothed, divided by volatility."""
    cfg = load_config("repo/config.yaml")
    window = cfg.signal.carry_smoothing_window

    spot_s = _ensure_series(spot)
    forward_s = _ensure_series(forward)
    vol_s = _ensure_series(volatility)

    raw = (spot_s - forward_s) / forward_s
    if len(raw) >= window:
        raw = raw.rolling(window=window, min_periods=window).mean()

    signal = raw / vol_s
    return signal


def compute_mso_signal(ir_spread: pd.Series, windows: Iterable[int]) -> pd.Series:
    """Compute Momentum Spill-Over signal from interest rate spread changes."""
    if not isinstance(ir_spread, pd.Series):
        raise TypeError("ir_spread must be a Series")

    windows = list(windows)
    if not windows:
        raise ValueError("windows must be non-empty")

    changes = ir_spread.diff()
    signals = []
    for w in windows:
        if w <= 0:
            raise ValueError("windows must be positive")
        signals.append(changes.rolling(window=w, min_periods=w).mean())

    return pd.concat(signals, axis=1).mean(axis=1)
