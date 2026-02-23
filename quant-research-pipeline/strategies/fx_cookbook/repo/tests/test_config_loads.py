import sys
sys.path.insert(0, "strategies/fx_cookbook/repo/src")

from fx_cookbook.spec_models import load_config


def test_config_loads():
    cfg = load_config("config.yaml")
    assert cfg.signal.lookback_min == 21
