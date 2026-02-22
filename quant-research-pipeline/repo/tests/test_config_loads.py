import sys

sys.path.insert(0, "repo/src")

from momentum_strategy_v1.spec_models import load_config


def test_config_loads():
    cfg = load_config("repo/config.yaml")
    assert cfg.signal.rsi_period == 14
