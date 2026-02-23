from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel, ConfigDict


class DataConfig(BaseModel):
    universe: Optional[str] = None
    train_start: Optional[str] = None
    train_end: Optional[str] = None
    validate_start: Optional[str] = None
    validate_end: Optional[str] = None
    holdout_start: Optional[str] = None
    holdout_end: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class SignalConfig(BaseModel):
    lookback_min: int
    lookback_max: int
    hysteresis_threshold: float
    vol_decay_diagonal: int
    vol_decay_offdiag: int
    rebalance_freq_medium: int
    rebalance_freq_short: int
    max_position_pct: float
    dispersion_floor_percentile: float
    carry_smoothing_window: int
    pca_window: int
    pca_beta_window: int
    n_currencies: int

    model_config = ConfigDict(extra="forbid")


class BacktestConfig(BaseModel):
    default_cost_bps: float
    cost_model: str

    model_config = ConfigDict(extra="forbid")


class Criterion(BaseModel):
    name: str
    threshold: float
    direction: str

    model_config = ConfigDict(extra="forbid")


class ValidationConfig(BaseModel):
    alpha: float
    effect_size: float
    criteria: List[Criterion]

    model_config = ConfigDict(extra="forbid")


class RepoConfig(BaseModel):
    data: DataConfig
    signal: SignalConfig
    backtest: BacktestConfig
    validation: ValidationConfig

    model_config = ConfigDict(extra="forbid")


def load_config(path: str | Path = "config.yaml") -> RepoConfig:
    p = Path(path)
    raw = yaml.safe_load(p.read_text())
    return RepoConfig(**raw)
