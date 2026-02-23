from __future__ import annotations

import numpy as np
import pandas as pd


CURRENCIES = [f"C{i:02d}" for i in range(24)]


def make_returns(kind: str) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    if kind == "all_positive_returns_252d":
        dates = pd.date_range("2000-01-01", periods=300, freq="B")
        data = np.full((len(dates), len(CURRENCIES)), 0.01)
        return pd.DataFrame(data, index=dates, columns=CURRENCIES)
    if kind == "alternating_sign_returns":
        dates = pd.date_range("2000-01-01", periods=300, freq="B")
        pos = 0.01
        neg = -pos / (1 + pos)
        base = np.where(np.arange(len(dates)) % 2 == 0, pos, neg)
        data = np.tile(base.reshape(-1, 1), (1, len(CURRENCIES)))
        return pd.DataFrame(data, index=dates, columns=CURRENCIES)
    if kind == "perfectly_correlated_24_pairs":
        dates = pd.date_range("2000-01-01", periods=300, freq="B")
        series = rng.normal(0, 0.01, size=len(dates))
        data = np.tile(series.reshape(-1, 1), (1, len(CURRENCIES)))
        return pd.DataFrame(data, index=dates, columns=CURRENCIES)
    if kind == "independent_noise_24_pairs":
        dates = pd.date_range("2000-01-01", periods=300, freq="B")
        data = rng.normal(0, 0.01, size=(len(dates), len(CURRENCIES)))
        return pd.DataFrame(data, index=dates, columns=CURRENCIES)
    if kind == "identity_corr_returns":
        dates = pd.date_range("2000-01-01", periods=500, freq="B")
        data = rng.normal(0, 0.01, size=(len(dates), 5))
        return pd.DataFrame(data, index=dates, columns=[f"A{i}" for i in range(5)])
    if kind == "perfectly_correlated_pair":
        dates = pd.date_range("2000-01-01", periods=300, freq="B")
        series = rng.normal(0, 0.01, size=len(dates))
        data = np.column_stack([series, series])
        return pd.DataFrame(data, index=dates, columns=["A", "B"])
    if kind == "constant_1pct_daily":
        dates = pd.date_range("2000-01-01", periods=10, freq="B")
        data = np.full((len(dates), 2), 0.01)
        return pd.DataFrame(data, index=dates, columns=["A", "B"])
    if kind == "known_returns":
        dates = pd.date_range("2000-01-01", periods=5, freq="B")
        data = np.array([[0.01, 0.02], [0.00, -0.01], [0.01, 0.00], [0.02, 0.01], [-0.01, 0.00]])
        return pd.DataFrame(data, index=dates, columns=["A", "B"])
    if kind == "strong_positive_returns_10y":
        n = 252 * 10
        return pd.Series(rng.normal(0.001, 0.005, size=n))
    if kind == "zero_mean_noise":
        n = 252 * 5
        return pd.Series(rng.normal(0.0, 0.01, size=n))

    raise ValueError(f"unknown returns kind: {kind}")


def make_weights(kind: str) -> pd.DataFrame:
    if kind == "constant_long_equal_weight":
        dates = pd.date_range("2000-01-01", periods=10, freq="B")
        data = np.full((len(dates), 2), 0.5)
        return pd.DataFrame(data, index=dates, columns=["A", "B"])
    if kind == "daily_flipping_weights":
        dates = pd.date_range("2000-01-01", periods=10, freq="B")
        w = np.where(np.arange(len(dates)) % 2 == 0, 0.5, -0.5)
        data = np.column_stack([w, -w])
        return pd.DataFrame(data, index=dates, columns=["A", "B"])
    if kind == "static_weights":
        dates = pd.date_range("2000-01-01", periods=5, freq="B")
        data = np.full((len(dates), 2), 0.5)
        return pd.DataFrame(data, index=dates, columns=["A", "B"])

    raise ValueError(f"unknown weights kind: {kind}")


def make_costs(kind: str, index: pd.DatetimeIndex, columns: list[str]) -> pd.DataFrame:
    if kind == "zero_costs":
        return pd.DataFrame(0.0, index=index, columns=columns)
    if kind == "10bps_spread":
        return pd.DataFrame(0.001, index=index, columns=columns)

    raise ValueError(f"unknown costs kind: {kind}")


def make_bid_ask(kind: str, index: pd.DatetimeIndex, columns: list[str]) -> pd.DataFrame:
    if kind == "zero_spreads":
        return pd.DataFrame(0.0, index=index, columns=columns)
    if kind == "uniform_spreads":
        return pd.DataFrame(0.002, index=index, columns=columns)

    raise ValueError(f"unknown bid_ask kind: {kind}")


def make_backtest_results(kind: str) -> pd.DataFrame:
    if kind == "constant_positive_returns":
        dates = pd.date_range("2000-01-01", periods=10, freq="B")
        net = pd.Series(0.01, index=dates)
        return pd.DataFrame({"net_return": net, "turnover": 0.0})
    if kind == "50pct_drawdown_then_recovery":
        dates = pd.date_range("2000-01-01", periods=3, freq="B")
        net = pd.Series([0.0, -0.5, 1.0], index=dates)
        return pd.DataFrame({"net_return": net, "turnover": 0.0})

    raise ValueError(f"unknown backtest_results kind: {kind}")


def make_covariance(kind: str) -> np.ndarray:
    if kind == "identity_matrix_scaled_0.04":
        return np.eye(3) * 0.04
    if kind == "diagonal_matrix_varied":
        return np.diag([0.01, 0.04, 0.09])

    raise ValueError(f"unknown covariance kind: {kind}")


def make_signals(kind: str) -> pd.DataFrame:
    if kind == "monotonic_ranking":
        return pd.DataFrame([[1, 2, 3, 4, 5, 6]], index=[pd.Timestamp("2000-01-03")], columns=[f"C{i}" for i in range(6)])
    if kind == "all_equal":
        return pd.DataFrame([[1, 1, 1, 1, 1, 1]], index=[pd.Timestamp("2000-01-03")], columns=[f"C{i}" for i in range(6)])

    raise ValueError(f"unknown signals kind: {kind}")


def make_betas(kind: str) -> pd.Series:
    if kind == "uniform_betas":
        return pd.Series(1.0, index=[f"C{i}" for i in range(6)])
    if kind == "varied_betas":
        return pd.Series([0.5, 0.8, 1.2, 1.5, 1.1, 0.7], index=[f"C{i}" for i in range(6)])

    raise ValueError(f"unknown betas kind: {kind}")
