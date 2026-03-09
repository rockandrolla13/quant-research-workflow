from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


_FX_REQUIRED = ["date", "currency_pair", "spot_rate", "forward_1m", "bid_ask_spread"]


def _compute_total_return(df: pd.DataFrame, bdays_per_month: int) -> pd.DataFrame:
    """Compute total return = spot return + carry for FX pairs."""
    df = df.sort_values(["currency_pair", "date"]).copy()
    spot_ret = df.groupby("currency_pair")["spot_rate"].pct_change()
    carry = (df["spot_rate"] - df["forward_1m"]) / df["forward_1m"] / float(bdays_per_month)
    df["total_return"] = spot_ret + carry
    return df


def _apply_quote_convention(df: pd.DataFrame, quote_convention: str, bdays_per_month: int) -> pd.DataFrame:
    """Invert rates if needed, then recompute total return."""
    if quote_convention == "USD_per_FX":
        return df
    if quote_convention != "FX_per_USD":
        raise ValueError(f"unknown quote_convention: {quote_convention}")

    df = df.copy()
    df["spot_rate"] = 1.0 / df["spot_rate"]
    df["forward_1m"] = 1.0 / df["forward_1m"]
    if "forward_6m" in df.columns:
        df["forward_6m"] = 1.0 / df["forward_6m"]
    df = _compute_total_return(df, bdays_per_month)
    return df


@dataclass
class FxAdapter:
    """Transform FX market data into canonical returns schema.

    Handles quote convention inversion, carry computation, and column mapping
    from FX-specific names (currency_pair) to canonical names (asset).
    """

    quote_convention: str = "USD_per_FX"
    bdays_per_month: int = 21

    def adapt(self, raw: pd.DataFrame) -> pd.DataFrame:
        """Transform FX data into canonical (date, asset, total_return, bid_ask_spread)."""
        missing = [c for c in _FX_REQUIRED if c not in raw.columns]
        if missing:
            raise ValueError(f"FX adapter requires columns: {missing}")

        df = raw.copy()
        df = _apply_quote_convention(df, self.quote_convention, self.bdays_per_month)

        if "total_return" not in df.columns or df["total_return"].isna().all():
            df = _compute_total_return(df, self.bdays_per_month)

        df = df.rename(columns={"currency_pair": "asset"})
        return df
