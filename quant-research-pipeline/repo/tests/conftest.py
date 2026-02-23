import numpy as np
import pandas as pd


def make_returns_all_positive(days=252, n_assets=4):
    data = np.full((days, n_assets), 0.01)
    return pd.DataFrame(data, columns=[f"C{i}" for i in range(n_assets)])


def make_returns_alternating(days=252, n_assets=4):
    pattern = np.array([0.01, -0.01])
    data = np.tile(pattern, days // 2 + 1)[:days]
    data = np.tile(data[:, None], (1, n_assets))
    return pd.DataFrame(data, columns=[f"C{i}" for i in range(n_assets)])


def make_perfectly_correlated(n_days=252, n_assets=24, seed=0):
    rng = np.random.default_rng(seed)
    base = rng.normal(0, 0.01, size=n_days)
    data = np.tile(base[:, None], (1, n_assets))
    return pd.DataFrame(data, columns=[f"C{i}" for i in range(n_assets)])


def make_independent_noise(n_days=252, n_assets=24, seed=1):
    rng = np.random.default_rng(seed)
    data = rng.normal(0, 0.01, size=(n_days, n_assets))
    return pd.DataFrame(data, columns=[f"C{i}" for i in range(n_assets)])
