from __future__ import annotations

import numpy as np
import pandas as pd


def _turnover_and_delta(weights: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    delta = weights.diff().abs()
    if not weights.empty:
        delta.iloc[0] = weights.iloc[0].abs()
    delta = delta.fillna(0.0)
    turnover = delta.sum(axis=1)
    return turnover, delta


def run_backtest(weights: pd.DataFrame, returns: pd.DataFrame, costs: pd.DataFrame) -> pd.DataFrame:
    """Run backtest with T+1 execution."""
    w = weights.shift(1).fillna(0.0)
    gross_return = (w * returns).sum(axis=1)
    turnover, delta = _turnover_and_delta(weights)
    cost = (delta * costs).sum(axis=1)
    net_return = gross_return - cost
    cumulative_return = (1.0 + net_return).cumprod() - 1.0

    out = pd.DataFrame(
        {
            "date": returns.index,
            "gross_return": gross_return.values,
            "net_return": net_return.values,
            "turnover": turnover.values,
            "cumulative_return": cumulative_return.values,
        }
    )
    return out


def compute_pnl(weights: pd.DataFrame, returns: pd.DataFrame, cost_bps: float, bid_ask: pd.DataFrame) -> pd.DataFrame:
    """Compute daily PnL from weights and returns with transaction costs."""
    w = weights.shift(1).fillna(0.0)
    gross_pnl = (w * returns).sum(axis=1)
    turnover, delta = _turnover_and_delta(weights)
    cost = (delta * bid_ask).sum(axis=1) * (cost_bps / 10000.0)
    net_pnl = gross_pnl - cost
    cumulative_net = net_pnl.cumsum()

    out = pd.DataFrame(
        {
            "date": returns.index,
            "gross_pnl": gross_pnl.values,
            "cost": cost.values,
            "net_pnl": net_pnl.values,
            "cumulative_net": cumulative_net.values,
        }
    )
    return out


def compute_metrics(backtest_results: pd.DataFrame) -> dict:
    """Compute Sharpe, CAGR, max drawdown, Calmar, Sortino, avg turnover."""
    net = backtest_results["net_return"] if "net_return" in backtest_results else backtest_results["net_pnl"]
    mean = net.mean()
    std = net.std(ddof=1)
    sharpe = (mean / std) * np.sqrt(252) if std > 0 else 0.0

    cumulative = (1.0 + net).cumprod()
    drawdown = cumulative / cumulative.cummax() - 1.0
    max_dd = abs(drawdown.min()) if len(drawdown) else 0.0

    n = len(net)
    cagr = cumulative.iloc[-1] ** (252 / n) - 1.0 if n > 0 else 0.0

    downside = net[net < 0]
    downside_std = downside.std(ddof=1)
    sortino = (mean / downside_std) * np.sqrt(252) if downside_std and downside_std > 0 else 0.0

    calmar = cagr / max_dd if max_dd > 0 else 0.0
    avg_turnover = backtest_results.get("turnover", pd.Series([0.0])).mean()

    return {
        "sharpe": float(sharpe),
        "cagr": float(cagr),
        "max_drawdown": float(max_dd),
        "calmar": float(calmar),
        "sortino": float(sortino),
        "avg_turnover": float(avg_turnover),
    }
