from __future__ import annotations

import numpy as np
import pandas as pd

from .spec_models import load_config


def _dispersion_floor(values: pd.Series, percentile: float) -> float:
    if values.empty:
        return 0.0
    return float(np.nanpercentile(values.values, percentile * 100))


def compute_momentum_signal(
    returns: pd.DataFrame,
    lookback_min: int,
    lookback_max: int,
    hysteresis_threshold: float,
) -> pd.DataFrame:
    """Compute momentum signal for all currencies.

    Returns DataFrame with columns [date, currency, raw_signal, dispersion, final_signal].
    """
    if lookback_min <= 0 or lookback_max < lookback_min:
        raise ValueError("invalid lookback range")

    cfg = load_config()
    floor_pct = cfg.signal.dispersion_floor_percentile

    lookbacks = list(range(lookback_min, lookback_max + 1))
    dates = returns.index
    currencies = returns.columns

    raw_signals = pd.DataFrame(index=dates, columns=currencies, dtype=float)
    dispersions = pd.DataFrame(index=dates, columns=currencies, dtype=float)

    for h in lookbacks:
        r_h = returns.rolling(window=h, min_periods=h).mean()
        sign_h = np.sign(r_h)
        raw_signals = raw_signals.add(sign_h, fill_value=0.0)

    raw_signals = raw_signals / float(len(lookbacks))

    # dispersion across lookbacks
    sign_stack = []
    for h in lookbacks:
        r_h = returns.rolling(window=h, min_periods=h).mean()
        sign_stack.append(np.sign(r_h))
    sign_stack = np.stack([s.values for s in sign_stack], axis=0)
    dispersion_values = np.nanstd(sign_stack, axis=0)
    dispersions.loc[:, :] = dispersion_values

    # hysteresis
    hysteresis = pd.DataFrame(index=dates, columns=currencies, dtype=float)
    for c in currencies:
        prev = 0.0
        for idx in dates:
            val = raw_signals.at[idx, c]
            if np.isnan(val):
                hysteresis.at[idx, c] = np.nan
                continue
            if abs(val) >= hysteresis_threshold:
                prev = float(np.sign(val))
            hysteresis.at[idx, c] = prev

    final_signal = pd.DataFrame(index=dates, columns=currencies, dtype=float)
    for idx in dates:
        floor_val = _dispersion_floor(dispersions.loc[idx], floor_pct)
        denom = dispersions.loc[idx].copy()
        denom = denom.where(denom >= floor_val, floor_val)
        final_signal.loc[idx] = hysteresis.loc[idx] / denom.replace(0, np.nan)

    out = (
        pd.DataFrame({"date": np.repeat(dates.values, len(currencies)), "currency": np.tile(currencies, len(dates))})
        .assign(
            raw_signal=raw_signals.values.ravel(),
            dispersion=dispersions.values.ravel(),
            final_signal=final_signal.values.ravel(),
        )
    )
    return out


def compute_carry_signal(spot: pd.Series, forward: pd.Series, volatility: pd.Series) -> pd.Series:
    """Compute carry signal: (spot - forward) / forward, smoothed, divided by volatility."""
    cfg = load_config()
    window = int(cfg.signal.carry_smoothing_window)

    raw = (spot - forward) / forward
    smoothed = raw.rolling(window=window, min_periods=1).mean()
    return smoothed / volatility


def compute_mso_signal(ir_spread: pd.Series, windows: list[int]) -> pd.Series:
    """Compute MSO signal from interest rate spread changes, averaged over windows."""
    ratios = []
    for h in windows:
        delta = ir_spread.diff(h)
        vol = ir_spread.diff().rolling(window=h, min_periods=h).std()
        ratio = delta / vol
        ratios.append(ratio)
    avg_ratio = pd.concat(ratios, axis=1).mean(axis=1)
    return avg_ratio.rolling(window=21, min_periods=1).mean()
