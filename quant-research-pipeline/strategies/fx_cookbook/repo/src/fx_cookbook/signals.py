from __future__ import annotations

import numpy as np
import pandas as pd


def _compute_sign_stack(returns: pd.DataFrame, lookbacks: list[int]) -> np.ndarray:
    """Compute sign(rolling_mean) for each lookback. Returns (n_lookbacks, n_dates, n_currencies)."""
    signs = []
    for h in lookbacks:
        r_h = returns.rolling(window=h, min_periods=h).mean()
        signs.append(np.sign(r_h).values)
    return np.stack(signs, axis=0)


def _compute_raw_signals(sign_stack: np.ndarray, index: pd.Index, columns: pd.Index) -> pd.DataFrame:
    """Average sign across lookbacks to get raw momentum signal."""
    return pd.DataFrame(np.nanmean(sign_stack, axis=0), index=index, columns=columns)


def _apply_hysteresis(
    raw_signals: pd.DataFrame, threshold: float
) -> pd.DataFrame:
    """Apply hysteresis filter: signal persists until overridden by strong opposite signal."""
    vals = raw_signals.values
    out = np.empty_like(vals)
    n_rows, n_cols = vals.shape
    for j in range(n_cols):
        prev = 0.0
        for i in range(n_rows):
            v = vals[i, j]
            if np.isnan(v):
                out[i, j] = np.nan
                continue
            if abs(v) >= threshold:
                prev = float(np.sign(v))
            out[i, j] = prev
    return pd.DataFrame(out, index=raw_signals.index, columns=raw_signals.columns)


def _normalize_by_dispersion(
    hysteresis: pd.DataFrame, dispersions: pd.DataFrame, floor_pct: float
) -> pd.DataFrame:
    """Divide hysteresis signal by floored dispersion."""
    disp_vals = dispersions.values
    floors = np.nanpercentile(disp_vals, floor_pct * 100, axis=1, keepdims=True)
    denom = np.where(disp_vals >= floors, disp_vals, floors)
    denom = np.where(denom == 0, np.nan, denom)
    result = hysteresis.values / denom
    return pd.DataFrame(result, index=hysteresis.index, columns=hysteresis.columns)


def compute_momentum_signal(
    returns: pd.DataFrame,
    lookback_min: int,
    lookback_max: int,
    hysteresis_threshold: float,
    dispersion_floor_pct: float = 0.25,
) -> pd.DataFrame:
    """Compute momentum signal for all currencies.

    Returns DataFrame with columns [date, currency, raw_signal, dispersion, final_signal].
    """
    if lookback_min <= 0 or lookback_max < lookback_min:
        raise ValueError("invalid lookback range")

    lookbacks = list(range(lookback_min, lookback_max + 1))
    dates = returns.index
    currencies = returns.columns

    sign_stack = _compute_sign_stack(returns, lookbacks)
    raw_signals = _compute_raw_signals(sign_stack, dates, currencies)
    dispersions = pd.DataFrame(np.nanstd(sign_stack, axis=0), index=dates, columns=currencies)
    hysteresis = _apply_hysteresis(raw_signals, hysteresis_threshold)
    final_signal = _normalize_by_dispersion(hysteresis, dispersions, dispersion_floor_pct)

    out = (
        pd.DataFrame({"date": np.repeat(dates.values, len(currencies)), "asset": np.tile(currencies, len(dates))})
        .assign(
            raw_signal=raw_signals.values.ravel(),
            dispersion=dispersions.values.ravel(),
            final_signal=final_signal.values.ravel(),
        )
    )
    return out


def compute_carry_signal(
    spot: pd.Series, forward: pd.Series, volatility: pd.Series, smoothing_window: int = 21
) -> pd.Series:
    """Compute carry signal: (spot - forward) / forward, smoothed, divided by volatility."""
    raw = (spot - forward) / forward
    smoothed = raw.rolling(window=smoothing_window, min_periods=1).mean()
    return smoothed / volatility.replace(0, np.nan)


def compute_mso_signal(
    ir_spread: pd.Series, windows: list[int], smoothing_window: int = 21
) -> pd.Series:
    """Compute MSO signal from interest rate spread changes, averaged over windows."""
    ratios = []
    for h in windows:
        delta = ir_spread.diff(h)
        vol = ir_spread.diff().rolling(window=h, min_periods=h).std()
        ratio = delta / vol
        ratios.append(ratio)
    avg_ratio = pd.concat(ratios, axis=1).mean(axis=1)
    return avg_ratio.rolling(window=smoothing_window, min_periods=1).mean()
