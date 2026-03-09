"""FX Cookbook strategy package — momentum-based FX strategy from the DB FX Cookbook."""

from .adapters import ReturnsAdapter, get_adapter
from .data import load_data
from .results import run_results
from .spec_models import load_config

__all__ = [
    "ReturnsAdapter",
    "adapters",
    "backtest",
    "data",
    "get_adapter",
    "load_config",
    "load_data",
    "portfolio",
    "results",
    "risk",
    "run_results",
    "signals",
    "spec_models",
    "validation",
]
