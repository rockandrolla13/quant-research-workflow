from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import pandas as pd
from pandas.api import types as ptypes
import yaml

from .spec_models import load_config


class DataProvider(Protocol):
    def load(self) -> pd.DataFrame:
        ...


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


def _required_columns() -> list[dict]:
    spec_path = Path(__file__).resolve().parents[3] / "spec" / "spec.yaml"
    spec = yaml.safe_load(spec_path.read_text())
    return spec["data_schema"]["columns"]


def _validate_schema(df: pd.DataFrame) -> None:
    columns = _required_columns()
    for col in columns:
        name = col["name"]
        dtype = col["dtype"]
        nullable = bool(col["nullable"])
        if name not in df.columns:
            raise ValueError(f"missing column: {name}")

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
        elif dtype == "int64":
            if not ptypes.is_integer_dtype(series):
                df[name] = pd.to_numeric(series, errors="raise").astype("int64")


def _compute_total_return(df: pd.DataFrame, bdays_per_month: int) -> pd.DataFrame:
    df = df.sort_values(["currency_pair", "date"]).copy()
    spot_ret = df.groupby("currency_pair")["spot_rate"].pct_change()
    carry = (df["spot_rate"] - df["forward_1m"]) / df["forward_1m"] / float(bdays_per_month)
    df["total_return"] = spot_ret + carry
    return df


def _apply_quote_convention(df: pd.DataFrame, quote_convention: str, bdays_per_month: int) -> pd.DataFrame:
    if quote_convention == "USD_per_FX":
        return df
    if quote_convention != "FX_per_USD":
        raise ValueError(f"unknown quote_convention: {quote_convention}")

    df = df.copy()
    df["spot_rate"] = 1.0 / df["spot_rate"]
    df["forward_1m"] = 1.0 / df["forward_1m"]
    if "forward_6m" in df.columns:
        df["forward_6m"] = 1.0 / df["forward_6m"]
    df = _compute_total_return(df, bdays_per_month)
    return df


def load_data(path: str | None = None) -> pd.DataFrame:
    cfg = load_config("config.yaml")
    provider = cfg.data.provider
    data_path = path or cfg.data.path

    if provider == "local_csv":
        source = LocalCSVProvider(data_path)
    elif provider == "local_parquet":
        source = LocalParquetProvider(data_path)
    else:
        raise ValueError(f"unknown data provider: {provider}")

    df = source.load()
    _validate_schema(df)

    calendar = cfg.data.calendar
    df = _apply_quote_convention(df, cfg.data.quote_convention, calendar.bdays_per_month)

    if "total_return" not in df.columns or df["total_return"].isna().any():
        df = _compute_total_return(df, calendar.bdays_per_month)

    _validate_schema(df)
    return df
