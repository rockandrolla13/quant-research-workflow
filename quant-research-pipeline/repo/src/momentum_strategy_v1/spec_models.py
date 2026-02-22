from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, ConfigDict


class DataConfig(BaseModel):
    source: Optional[str] = None
    frequency: Optional[str] = None
    universe: Optional[str] = None
    train_start: Optional[str] = None
    train_end: Optional[str] = None
    validate_start: Optional[str] = None
    validate_end: Optional[str] = None
    holdout_start: Optional[str] = None
    holdout_end: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class SignalConfig(BaseModel):
    rsi_period: int
    oversold_threshold: int
    overbought_threshold: int

    model_config = ConfigDict(extra="forbid")


class ValidationConfig(BaseModel):
    sharpe_ratio_threshold: Optional[float] = None
    max_drawdown_threshold: Optional[float] = None
    cagr_threshold: Optional[float] = None

    model_config = ConfigDict(extra="forbid")


class RepoConfig(BaseModel):
    data: DataConfig
    signal: SignalConfig
    validation: Optional[ValidationConfig] = None

    model_config = ConfigDict(extra="forbid")


def load_config(path: str | Path = "config.yaml") -> RepoConfig:
    p = Path(path)
    raw = yaml.safe_load(p.read_text())
    return RepoConfig(**raw)
