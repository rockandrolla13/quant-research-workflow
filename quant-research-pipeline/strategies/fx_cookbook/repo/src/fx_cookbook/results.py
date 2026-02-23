from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from . import backtest, portfolio, risk, signals, validation
from .data import load_data
from .spec_models import load_config


def _pivot_returns(df: pd.DataFrame) -> pd.DataFrame:
    return df.pivot(index="date", columns="currency_pair", values="total_return").sort_index()


def run_results(output_dir: str | Path = "outputs") -> dict:
    cfg = load_config("config.yaml")
    df = load_data(cfg.data.path)

    returns = _pivot_returns(df)

    momentum = signals.compute_momentum_signal(
        returns,
        lookback_min=cfg.signal.lookback_min,
        lookback_max=cfg.signal.lookback_max,
        hysteresis_threshold=cfg.signal.hysteresis_threshold,
    )
    momentum_pivot = momentum.pivot(index="date", columns="currency", values="final_signal").sort_index()

    cov = risk.estimate_covariance(returns, cfg.signal.vol_decay_diagonal, cfg.signal.vol_decay_offdiag)
    vol = risk.compute_asset_volatility(cov)
    vol_df = pd.DataFrame([vol.values] * len(returns), index=returns.index, columns=returns.columns)

    weights = portfolio.build_ts_weights(momentum_pivot.fillna(0.0), vol_df, cfg.signal.max_position_pct)
    costs = df.pivot(index="date", columns="currency_pair", values="bid_ask_spread").reindex(returns.index)

    bt = backtest.run_backtest(weights, returns, costs)
    metrics = backtest.compute_metrics(bt)

    hyp = validation.run_hypothesis_test(bt["net_return"], cfg.validation.alpha, cfg.validation.effect_size)
    criteria = validation.evaluate_success_criteria(metrics, cfg.validation.criteria)
    verdict = validation.go_no_go(hyp, criteria)

    output_dir = Path(output_dir)
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    metrics_payload = {"metrics": metrics, "hypothesis": hyp, "criteria": criteria, "verdict": verdict}
    (output_dir / "metrics.json").write_text(json.dumps(metrics_payload, indent=2))

    # plot cumulative return
    plt.figure(figsize=(8, 4))
    bt.set_index("date")["cumulative_return"].plot(title="Cumulative Net Return")
    plt.tight_layout()
    plt.savefig(figures_dir / "cumulative_return.png", dpi=150)
    plt.close()

    summary = [
        "# Results Summary",
        "",
        f"Decision: **{verdict['decision']}**",
        "",
        "## Metrics",
    ]
    for k, v in metrics.items():
        summary.append(f"- {k}: {v:.6f}" if isinstance(v, (int, float)) else f"- {k}: {v}")
    summary.append("")
    summary.append("## Hypothesis Test")
    summary.append(f"- reject_h0: {hyp['reject_h0']}")
    summary.append(f"- p_value: {hyp['p_value']:.6f}")
    summary.append(f"- sharpe: {hyp['sharpe']:.6f}")

    (output_dir / "RESULTS.md").write_text("\n".join(summary))

    return metrics_payload


def main() -> None:
    run_results("outputs")


if __name__ == "__main__":
    main()
