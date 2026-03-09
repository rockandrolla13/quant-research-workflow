from __future__ import annotations

from typing import Protocol

import pandas as pd


CANONICAL_COLUMNS = ["date", "asset", "total_return", "bid_ask_spread"]


class ReturnsAdapter(Protocol):
    """Transform raw market data into canonical returns schema.

    The canonical schema has columns: date, asset, total_return, bid_ask_spread.
    All asset-class-specific logic (quote conventions, carry computation,
    return calculation, column mapping) lives in the adapter implementation.
    """

    def adapt(self, raw: pd.DataFrame) -> pd.DataFrame:
        """Transform raw data into canonical (date, asset, total_return, bid_ask_spread).

        Args:
            raw: DataFrame as loaded from CSV/Parquet, with asset-class-specific columns.

        Returns:
            DataFrame with exactly: date (datetime), asset (str),
            total_return (float64), bid_ask_spread (float64).
            Additional columns are permitted but ignored by the domain stack.

        Raises:
            ValueError: If required source columns are missing or data is invalid.
        """
        ...
