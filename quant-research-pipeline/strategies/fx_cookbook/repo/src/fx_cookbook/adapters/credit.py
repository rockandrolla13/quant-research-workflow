from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


_CREDIT_REQUIRED = ["date", "bond_id", "spread", "duration", "bid_ask"]


@dataclass
class CreditAdapter:
    """Transform credit bond data into canonical returns schema.

    Computes daily excess return as:
        total_return = -duration * Δspread + carry

    where carry = spread / bdays_per_year (daily accrual of the spread premium).

    The spread change component captures mark-to-market P&L from credit spread
    movements. Duration scales the spread change into return space.

    Parameters:
        bdays_per_year: Business days per year for carry annualisation.
        spread_unit: Multiplier to convert spread to decimal.
            1.0 if spread is already decimal (e.g. 0.0150 for 150bp).
            0.0001 if spread is in basis points (e.g. 150 for 150bp).
    """

    bdays_per_year: int = 252
    spread_unit: float = 0.0001

    def adapt(self, raw: pd.DataFrame) -> pd.DataFrame:
        """Transform credit data into canonical (date, asset, total_return, bid_ask_spread)."""
        missing = [c for c in _CREDIT_REQUIRED if c not in raw.columns]
        if missing:
            raise ValueError(f"Credit adapter requires columns: {missing}")

        df = raw.copy()
        df = df.sort_values(["bond_id", "date"])

        spread_dec = df["spread"] * self.spread_unit
        duration = df["duration"]

        # Spread change within each bond
        delta_spread = df.groupby("bond_id")["spread"].diff() * self.spread_unit

        # Excess return = -duration * Δspread + carry
        carry = spread_dec / float(self.bdays_per_year)
        df["total_return"] = -duration * delta_spread + carry

        # Bid-ask: convert to decimal if needed
        df["bid_ask_spread"] = df["bid_ask"] * self.spread_unit

        df = df.rename(columns={"bond_id": "asset"})
        return df
