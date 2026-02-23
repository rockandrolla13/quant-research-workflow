import numpy as np
import pandas as pd
import sys

sys.path.insert(0, "repo/src")

from fx_cookbook.backtest import run_backtest, compute_pnl, compute_metrics


def test_run_backtest_constant_returns_zero_cost():
    dates = pd.date_range("2020-01-01", periods=5, freq="D")
    weights = pd.DataFrame(0.25, index=dates, columns=["A", "B", "C", "D"])
    returns = pd.DataFrame(0.01, index=dates, columns=["A", "B", "C", "D"])
    costs = pd.DataFrame(0.0, index=dates, columns=["A", "B", "C", "D"])

    result = run_backtest(weights, returns, costs)
    assert np.allclose(result["gross_return"].iloc[1:], 0.01, atol=1e-6)
    assert np.allclose(result["net_return"].iloc[1:], 0.01, atol=1e-6)
    assert np.allclose(result["turnover"].iloc[2:], 0.0, atol=1e-6)


def test_run_backtest_flipping_weights_costs():
    dates = pd.date_range("2020-01-01", periods=5, freq="D")
    weights = pd.DataFrame([1, -1, 1, -1, 1], index=dates, columns=["A"])
    returns = pd.DataFrame(0.01, index=dates, columns=["A"])
    costs = pd.DataFrame(0.001, index=dates, columns=["A"])

    result = run_backtest(weights, returns, costs)
    assert (result["net_return"] < result["gross_return"]).any()


def test_compute_pnl_zero_costs():
    dates = pd.date_range("2020-01-01", periods=3, freq="D")
    weights = pd.DataFrame(1.0, index=dates, columns=["A"])
    returns = pd.DataFrame([0.01, 0.01, 0.01], index=dates, columns=["A"])
    bid_ask = pd.DataFrame(0.0, index=dates, columns=["A"])

    pnl = compute_pnl(weights, returns, cost_bps=0.0, bid_ask=bid_ask)
    assert np.allclose(pnl["gross_pnl"], pnl["net_pnl"], atol=1e-6)


def test_compute_pnl_with_costs():
    dates = pd.date_range("2020-01-01", periods=3, freq="D")
    weights = pd.DataFrame(1.0, index=dates, columns=["A"])
    returns = pd.DataFrame([0.01, 0.01, 0.01], index=dates, columns=["A"])
    bid_ask = pd.DataFrame(0.01, index=dates, columns=["A"])

    pnl = compute_pnl(weights, returns, cost_bps=10.0, bid_ask=bid_ask)
    assert (pnl["net_pnl"] < pnl["gross_pnl"]).any()


def test_compute_metrics_constant_positive():
    dates = pd.date_range("2020-01-01", periods=10, freq="D")
    backtest_results = pd.DataFrame(
        {
            "net_return": [0.01] * 10,
            "turnover": [0.0] * 10,
        },
        index=dates,
    )
    metrics = compute_metrics(backtest_results)
    assert metrics["sharpe"] > 0
    assert metrics["max_drawdown"] == 0
    assert metrics["cagr"] > 0


def test_compute_metrics_drawdown():
    dates = pd.date_range("2020-01-01", periods=3, freq="D")
    backtest_results = pd.DataFrame(
        {
            "net_return": [0.0, -0.5, 1.0],
            "turnover": [0.0, 0.0, 0.0],
        },
        index=dates,
    )
    metrics = compute_metrics(backtest_results)
    assert abs(metrics["max_drawdown"] - 0.5) < 0.05
