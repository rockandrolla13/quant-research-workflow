from __future__ import annotations

import numpy as np
import pandas as pd


def _lagged_weights(weights: pd.DataFrame) -> pd.DataFrame:
    """T+1 execution: use previous day's weights."""
    return weights.shift(1).fillna(0.0)


def _gross_return(weights_lagged: pd.DataFrame, returns: pd.DataFrame) -> pd.Series:
    return (weights_lagged * returns).sum(axis=1)


def _turnover(weights: pd.DataFrame) -> pd.Series:
    return weights.diff().abs().sum(axis=1).fillna(0.0)


def run_backtest(weights: pd.DataFrame, returns: pd.DataFrame, costs: pd.DataFrame) -> pd.DataFrame:
    """Run backtest with T+1 execution."""
    w_lag = _lagged_weights(weights)
    gross = _gross_return(w_lag, returns)
    to = _turnover(weights)
    cost = (costs * weights.diff().abs()).sum(axis=1).fillna(0.0)

    net_return = gross - cost
    cumulative_return = (1 + net_return).cumprod() - 1

    return pd.DataFrame(
        {
            "date": returns.index,
            "gross_return": gross.values,
            "net_return": net_return.values,
            "turnover": to.values,
            "cumulative_return": cumulative_return.values,
        }
    )


def compute_pnl(
    weights: pd.DataFrame, returns: pd.DataFrame, cost_bps: float, bid_ask: pd.DataFrame
) -> pd.DataFrame:
    """Compute daily PnL from weights and returns with transaction costs."""
    w_lag = _lagged_weights(weights)
    gross_pnl = _gross_return(w_lag, returns)

    to = _turnover(weights)
    to.iloc[0] = weights.iloc[0].abs().sum()
    spread = bid_ask.mean(axis=1).fillna(0.0)
    cost = to * (cost_bps / 10000.0) * spread

    net_pnl = gross_pnl - cost
    cumulative_net = net_pnl.cumsum()

    return pd.DataFrame(
        {
            "date": returns.index,
            "gross_pnl": gross_pnl.values,
            "cost": cost.values,
            "net_pnl": net_pnl.values,
            "cumulative_net": cumulative_net.values,
        }
    )


def compute_metrics(backtest_results: pd.DataFrame, bdays_per_year: int = 252) -> dict:
    """Compute Sharpe, CAGR, max drawdown, Calmar, Sortino, avg turnover."""
    if "net_return" in backtest_results:
        r = backtest_results["net_return"].astype(float)
    elif "gross_return" in backtest_results:
        r = backtest_results["gross_return"].astype(float)
    else:
        raise ValueError("backtest_results must include net_return or gross_return")

    mean = r.mean()
    std = r.std(ddof=1)
    sharpe = (np.sqrt(bdays_per_year) * mean / std) if std != 0 else 0.0

    cumulative = (1 + r).cumprod()
    years = len(r) / float(bdays_per_year)
    cagr = (cumulative.iloc[-1] ** (1 / years) - 1) if years > 0 else 0.0

    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    max_drawdown = float(drawdown.min()) if not drawdown.empty else 0.0

    calmar = (cagr / abs(max_drawdown)) if max_drawdown != 0 else float("inf")

    downside = r[r < 0]
    downside_std = downside.std(ddof=1)
    sortino = (np.sqrt(bdays_per_year) * mean / downside_std) if downside_std != 0 else 0.0

    avg_turnover = float(backtest_results.get("turnover", pd.Series([0.0])).mean())

    return {
        "sharpe": sharpe,
        "cagr": cagr,
        "max_drawdown": abs(max_drawdown),
        "calmar": calmar,
        "sortino": sortino,
        "avg_turnover": avg_turnover,
    }
