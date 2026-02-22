from __future__ import annotations

import pandas as pd


def calculate_rsi(prices: pd.Series, period: int) -> pd.Series:
    """Calculates the Relative Strength Index (RSI)."""
    if period <= 0:
        raise ValueError("period must be positive")
    if not isinstance(prices, pd.Series):
        raise TypeError("prices must be a pandas Series")

    change = prices.diff()
    gain = change.where(change > 0, 0.0)
    loss = -change.where(change < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.round(2)
