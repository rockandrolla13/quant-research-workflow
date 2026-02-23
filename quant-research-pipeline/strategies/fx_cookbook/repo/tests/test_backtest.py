import numpy as np

import sys
sys.path.insert(0, "strategies/fx_cookbook/repo/src")

from fx_cookbook.backtest import run_backtest, compute_pnl, compute_metrics
from .utils import make_returns, make_weights, make_costs, make_bid_ask, make_backtest_results


def test_run_backtest_constant_returns():
    returns = make_returns("constant_1pct_daily")
    weights = make_weights("constant_long_equal_weight")
    costs = make_costs("zero_costs", returns.index, returns.columns)

    result = run_backtest(weights, returns, costs)
    assert np.allclose(result["gross_return"].iloc[1:], 0.01)
    assert np.allclose(result["net_return"].iloc[1:], 0.01)
    assert result["turnover"].iloc[1:].sum() == 0.0


def test_run_backtest_turnover_costs():
    returns = make_returns("constant_1pct_daily")
    weights = make_weights("daily_flipping_weights")
    costs = make_costs("10bps_spread", returns.index, returns.columns)

    result = run_backtest(weights, returns, costs)
    assert (result["net_return"] < result["gross_return"]).any()


def test_compute_pnl_costs():
    returns = make_returns("known_returns")
    weights = make_weights("static_weights")

    bid_ask_zero = make_bid_ask("zero_spreads", returns.index, returns.columns)
    pnl = compute_pnl(weights, returns, cost_bps=0.0, bid_ask=bid_ask_zero)
    assert np.allclose(pnl["gross_pnl"], pnl["net_pnl"])

    bid_ask = make_bid_ask("uniform_spreads", returns.index, returns.columns)
    pnl_cost = compute_pnl(weights, returns, cost_bps=10.0, bid_ask=bid_ask)
    assert (pnl_cost["net_pnl"] < pnl_cost["gross_pnl"]).any()


def test_compute_metrics():
    backtest_results = make_backtest_results("constant_positive_returns")
    metrics = compute_metrics(backtest_results)
    assert metrics["sharpe"] > 0
    assert metrics["max_drawdown"] == 0.0
    assert metrics["cagr"] > 0

    backtest_results = make_backtest_results("50pct_drawdown_then_recovery")
    metrics = compute_metrics(backtest_results)
    assert abs(metrics["max_drawdown"] - 0.5) < 0.05
