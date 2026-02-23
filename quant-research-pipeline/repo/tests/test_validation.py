import numpy as np
import pandas as pd
import sys
from hypothesis import given, strategies as st

sys.path.insert(0, "repo/src")

from fx_cookbook.validation import run_hypothesis_test, evaluate_success_criteria, go_no_go


def test_run_hypothesis_test_strong_positive():
    rng = np.random.default_rng(0)
    returns = rng.normal(0.01, 0.02, size=252 * 10)
    result = run_hypothesis_test(returns, alpha=0.05, effect_size=0.4)
    assert result["reject_h0"] is True
    assert result["sharpe"] > 0.4
    assert result["p_value"] < 0.05


def test_run_hypothesis_test_zero_mean():
    rng = np.random.default_rng(1)
    returns = rng.normal(0.0, 0.02, size=252 * 5)
    result = run_hypothesis_test(returns, alpha=0.05, effect_size=0.4)
    assert result["reject_h0"] is False


def test_evaluate_success_criteria_all_pass():
    metrics = {"sharpe": 0.6, "max_dd": 0.15}
    criteria = [
        {"name": "sharpe", "threshold": 0.4, "direction": ">"},
        {"name": "max_dd", "threshold": 0.25, "direction": "<"},
    ]
    results = evaluate_success_criteria(metrics, criteria)
    assert all(r["pass"] for r in results)


def test_evaluate_success_criteria_fail():
    metrics = {"sharpe": 0.2, "max_dd": 0.30}
    criteria = [
        {"name": "sharpe", "threshold": 0.4, "direction": ">"},
        {"name": "max_dd", "threshold": 0.25, "direction": "<"},
    ]
    results = evaluate_success_criteria(metrics, criteria)
    assert not any(r["pass"] for r in results)


def test_go_no_go():
    decision = go_no_go({"reject_h0": True}, [{"pass": True}, {"pass": True}])
    assert decision["decision"] == "GO"

    decision = go_no_go({"reject_h0": False}, [{"pass": True}, {"pass": True}])
    assert decision["decision"] == "NO_GO"
    assert "hypothesis_failed" in decision["reasons"]


@given(
    reject=st.booleans(),
    passes=st.lists(st.booleans(), min_size=1, max_size=5),
)
def test_go_no_go_property(reject, passes):
    criteria_results = [{"pass": p} for p in passes]
    result = go_no_go({"reject_h0": reject}, criteria_results)
    expected = "GO" if reject and all(passes) else "NO_GO"
    assert result["decision"] == expected
