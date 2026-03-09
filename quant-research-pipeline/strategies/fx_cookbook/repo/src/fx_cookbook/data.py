from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from pandas.api import types as ptypes

from .spec_models import load_config


@dataclass
class LocalCSVProvider:
    path: str

    def load(self) -> pd.DataFrame:
        p = Path(self.path)
        if p.is_dir():
            files = sorted(p.glob("*.csv"))
            if not files:
                raise FileNotFoundError(f"no csv files found in {p}")
            frames = [pd.read_csv(f) for f in files]
            df = pd.concat(frames, ignore_index=True)
        else:
            df = pd.read_csv(p)
        return df


@dataclass
class LocalParquetProvider:
    path: str

    def load(self) -> pd.DataFrame:
        p = Path(self.path)
        if p.is_dir():
            files = sorted(p.glob("*.parquet"))
            if not files:
                raise FileNotFoundError(f"no parquet files found in {p}")
            frames = [pd.read_parquet(f) for f in files]
            df = pd.concat(frames, ignore_index=True)
        else:
            df = pd.read_parquet(p)
        return df


_CANONICAL_COLUMNS: list[dict] = [
    {"name": "date", "dtype": "datetime", "nullable": False},
    {"name": "asset", "dtype": "str", "nullable": False},
    {"name": "total_return", "dtype": "float64", "nullable": True},
    {"name": "bid_ask_spread", "dtype": "float64", "nullable": False},
]


def _validate_canonical_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Validate that a DataFrame matches the canonical returns schema."""
    df = df.copy()
    for col in _CANONICAL_COLUMNS:
        name = col["name"]
        dtype = col["dtype"]
        nullable = bool(col["nullable"])
        if name not in df.columns:
            raise ValueError(f"missing canonical column: {name}")

        series = df[name]
        if not nullable and series.isna().any():
            raise ValueError(f"non-nullable column has nulls: {name}")

        if dtype == "datetime":
            if not ptypes.is_datetime64_any_dtype(series):
                try:
                    df[name] = pd.to_datetime(series)
                except Exception as exc:
                    raise ValueError(f"column {name} is not datetime") from exc
        elif dtype == "str":
            if not (ptypes.is_string_dtype(series) or ptypes.is_object_dtype(series)):
                raise ValueError(f"column {name} is not string")
        elif dtype == "float64":
            if not ptypes.is_float_dtype(series):
                df[name] = pd.to_numeric(series, errors="raise")
    return df


def load_data(path: str | None = None) -> pd.DataFrame:
    """Load raw data, apply adapter, validate canonical schema."""
    from .adapters import get_adapter

    cfg = load_config("config.yaml")
    provider = cfg.data.provider
    data_path = path or cfg.data.path

    # Resolve relative paths against repo root (2 levels up from this file)
    dp = Path(data_path)
    if not dp.is_absolute() and not dp.exists():
        repo_root = Path(__file__).resolve().parents[2]
        dp = repo_root / dp
    data_path = str(dp)

    if provider == "local_csv":
        source = LocalCSVProvider(data_path)
    elif provider == "local_parquet":
        source = LocalParquetProvider(data_path)
    else:
        raise ValueError(f"unknown data provider: {provider}")

    raw = source.load()

    adapter = get_adapter(cfg.adapter.name, **cfg.adapter.params)
    df = adapter.adapt(raw)
    df = _validate_canonical_schema(df)

    return df
