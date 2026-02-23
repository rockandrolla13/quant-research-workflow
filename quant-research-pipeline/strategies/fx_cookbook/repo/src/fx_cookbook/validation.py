from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats


def run_hypothesis_test(returns: pd.Series, alpha: float, effect_size: float) -> dict:
    """Two-sided t-test on annualised Sharpe ratio vs 0."""
    r = returns.dropna().astype(float)
    n_obs = int(r.shape[0])
    if n_obs < 2:
        return {"t_stat": 0.0, "p_value": 1.0, "sharpe": 0.0, "reject_h0": False, "n_obs": n_obs}

    mean = r.mean()
    std = r.std(ddof=1)
    sharpe = (np.sqrt(252) * mean / std) if std != 0 else 0.0
    t_stat = sharpe * np.sqrt(n_obs)
    p_value = float(stats.t.sf(np.abs(t_stat), df=n_obs - 1) * 2)
    reject = bool((p_value < alpha) and (sharpe > effect_size))

    return {"t_stat": float(t_stat), "p_value": p_value, "sharpe": float(sharpe), "reject_h0": reject, "n_obs": n_obs}


def evaluate_success_criteria(metrics: dict, criteria: list[dict]) -> list[dict]:
    """Check each metric against its threshold and direction."""
    results: list[dict[str, Any]] = []
    for c in criteria:
        name = c["name"]
        threshold = c["threshold"]
        direction = c["direction"]
        value = metrics.get(name)
        if value is None:
            passed = False
        elif direction == ">":
            passed = value > threshold
        elif direction == "<":
            passed = value < threshold
        else:
            raise ValueError(f"unknown direction: {direction}")
        results.append(
            {
                "name": name,
                "value": value,
                "threshold": threshold,
                "direction": direction,
                "pass": passed,
            }
        )
    return results


def go_no_go(hypothesis_result: dict, criteria_results: list[dict]) -> dict:
    """Combine hypothesis test and criteria evaluation into a single verdict."""
    hypothesis_pass = bool(hypothesis_result.get("reject_h0"))
    criteria_all_pass = all(r.get("pass") for r in criteria_results)

    reasons = []
    if not hypothesis_pass:
        reasons.append("hypothesis_failed")
    for r in criteria_results:
        if not r.get("pass"):
            reasons.append(f"criteria_failed:{r.get('name')}")

    decision = "GO" if (hypothesis_pass and criteria_all_pass) else "NO_GO"
    return {
        "decision": decision,
        "reasons": reasons,
        "hypothesis_pass": hypothesis_pass,
        "criteria_all_pass": criteria_all_pass,
    }
