from __future__ import annotations

from typing import Dict

import pandas as pd


def allocate_weights(signals: pd.DataFrame, risk_params: dict) -> pd.DataFrame:
    """Allocates portfolio weights based on signals and risk parameters."""
    if not isinstance(signals, pd.DataFrame):
        raise TypeError("signals must be a pandas DataFrame")
    if not isinstance(risk_params, Dict):
        raise TypeError("risk_params must be a dict")

    normalize = risk_params.get("normalize", True)
    max_weight = risk_params.get("max_weight")
    min_weight = risk_params.get("min_weight")

    weights = signals.astype(float).copy()

    if normalize:
        denom = weights.abs().sum(axis=1)
        denom = denom.replace(0, 1.0)
        weights = weights.div(denom, axis=0)

    if max_weight is not None:
        weights = weights.clip(upper=float(max_weight))
    if min_weight is not None:
        weights = weights.clip(lower=float(min_weight))

    return weights
