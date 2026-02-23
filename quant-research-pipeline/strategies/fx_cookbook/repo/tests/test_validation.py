import sys
sys.path.insert(0, "strategies/fx_cookbook/repo/src")

from fx_cookbook.validation import run_hypothesis_test, evaluate_success_criteria, go_no_go
from .utils import make_returns


def test_run_hypothesis_test():
    returns = make_returns("strong_positive_returns_10y")
    result = run_hypothesis_test(returns, alpha=0.05, effect_size=0.4)
    assert result["reject_h0"] is True
    assert result["p_value"] < 0.05
    assert result["sharpe"] > 0.4

    returns = make_returns("zero_mean_noise")
    result = run_hypothesis_test(returns, alpha=0.05, effect_size=0.4)
    assert result["reject_h0"] is False


def test_evaluate_success_criteria():
    criteria = [
        {"name": "sharpe", "threshold": 0.4, "direction": ">"},
        {"name": "max_dd", "threshold": 0.25, "direction": "<"},
    ]
    metrics = {"sharpe": 0.6, "max_dd": 0.15}
    results = evaluate_success_criteria(metrics, criteria)
    assert all(r["pass"] for r in results)

    metrics = {"sharpe": 0.2, "max_dd": 0.3}
    results = evaluate_success_criteria(metrics, criteria)
    assert not any(r["pass"] for r in results)


def test_go_no_go():
    criteria_results = [{"pass": True}, {"pass": True}]
    hypothesis_result = {"reject_h0": True}
    decision = go_no_go(hypothesis_result, criteria_results)
    assert decision["decision"] == "GO"

    hypothesis_result = {"reject_h0": False}
    decision = go_no_go(hypothesis_result, criteria_results)
    assert decision["decision"] == "NO_GO"
    assert any("hypothesis" in r for r in decision["reasons"])
