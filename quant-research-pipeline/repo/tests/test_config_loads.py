import sys

sys.path.insert(0, "repo/src")

from fx_cookbook.spec_models import load_config


def test_config_loads():
    cfg = load_config("repo/config.yaml")
    assert cfg.signal.lookback_min == 21
    assert cfg.backtest.cost_model == "spread"
