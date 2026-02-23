import sys

import pandas as pd

sys.path.insert(0, "strategies/fx_cookbook/repo/src")

from fx_cookbook import backtest, portfolio, risk, signals, validation
from fx_cookbook.data import load_data
from fx_cookbook.spec_models import load_config


def test_data_pipeline_smoke_from_fixture():
    cfg = load_config("config.yaml")
    df = load_data(cfg.data.path)

    required = {
        "date",
        "currency_pair",
        "spot_rate",
        "forward_1m",
        "forward_6m",
        "bid_ask_spread",
        "total_return",
    }
    assert required.issubset(df.columns)
    assert isinstance(df["date"].iloc[0], pd.Timestamp)
    assert df["total_return"].notna().all()

    returns = df.pivot(index="date", columns="currency_pair", values="total_return").sort_index()
    sig = signals.compute_momentum_signal(
        returns, cfg.signal.lookback_min, cfg.signal.lookback_max, cfg.signal.hysteresis_threshold
    )
    sig_pivot = sig.pivot(index="date", columns="currency", values="final_signal").sort_index()

    cov = risk.estimate_covariance(returns, cfg.signal.vol_decay_diagonal, cfg.signal.vol_decay_offdiag)
    vol = risk.compute_asset_volatility(cov)
    vol_df = pd.DataFrame([vol.values] * len(returns), index=returns.index, columns=returns.columns)

    weights = portfolio.build_ts_weights(sig_pivot.fillna(0.0), vol_df, cfg.signal.max_position_pct)
    costs = df.pivot(index="date", columns="currency_pair", values="bid_ask_spread").reindex(returns.index)

    bt = backtest.run_backtest(weights, returns, costs)
    metrics = backtest.compute_metrics(bt)
    hyp = validation.run_hypothesis_test(bt["net_return"], cfg.validation.alpha, cfg.validation.effect_size)
    criteria = validation.evaluate_success_criteria(metrics, cfg.validation.criteria)
    verdict = validation.go_no_go(hyp, criteria)

    assert "decision" in verdict
