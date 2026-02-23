from __future__ import annotations

from typing import List

import numpy as np
from scipy import stats


def run_hypothesis_test(returns, alpha: float, effect_size: float) -> dict:
    """Two-sided t-test on annualised Sharpe ratio vs 0."""
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    n = len(r)
    mean = r.mean() if n else 0.0
    std = r.std(ddof=1) if n > 1 else 0.0
    sharpe = (mean / std) * np.sqrt(252) if std > 0 else 0.0
    t_stat = (mean / std) * np.sqrt(n) if std > 0 and n > 1 else 0.0
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=max(n - 1, 1)))
    reject_h0 = bool(p_value < alpha and sharpe > effect_size)

    return {
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "sharpe": float(sharpe),
        "reject_h0": reject_h0,
        "n_obs": int(n),
    }


def evaluate_success_criteria(metrics: dict, criteria: List[dict]) -> List[dict]:
    results = []
    for c in criteria:
        name = c["name"]
        threshold = c["threshold"]
        direction = c["direction"]
        value = metrics.get(name)
        passed = False
        if value is not None:
            if direction == ">":
                passed = value > threshold
            elif direction == "<":
                passed = value < threshold
            else:
                raise ValueError("direction must be '>' or '<'")
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


def go_no_go(hypothesis_result: dict, criteria_results: List[dict]) -> dict:
    hypothesis_pass = bool(hypothesis_result.get("reject_h0"))
    criteria_all_pass = all(r.get("pass") for r in criteria_results)
    reasons = []
    if not hypothesis_pass:
        reasons.append("hypothesis_failed")
    if not criteria_all_pass:
        reasons.append("criteria_failed")

    decision = "GO" if hypothesis_pass and criteria_all_pass else "NO_GO"
    return {
        "decision": decision,
        "reasons": reasons,
        "hypothesis_pass": hypothesis_pass,
        "criteria_all_pass": criteria_all_pass,
    }
