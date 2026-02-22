# SPEC.md — FX Cookbook Strategy Specification

> Derived from `spec.yaml`. If they conflict, `spec.yaml` wins.

## Meta

| Field       | Value |
|-------------|-------|
| Strategy ID | fx_cookbook |
| Version     | v1.0 |
| Status      | draft |

## Hypotheses

| Field       | Value |
|-------------|-------|
| H0 | FX momentum and carry signals have zero predictive power for future currency returns after transaction costs |
| H1 | Multi-horizon momentum and carry signals generate positive risk-adjusted returns (Sharpe > 0.4) net of costs |
| Test | Two-sided t-test on annualised Sharpe ratio vs 0 |
| Alpha | 0.05 |
| Effect size | 0.4 |

## Signal

**Name**: fx_cookbook_composite (momentum + carry)

**Momentum formula**:
$$S_{i,t}^{\text{final}} = \frac{\hat{S}_t}{\max(\tilde{\sigma}_t,\; \tilde{\sigma}^{\text{floor}}_t)}$$

**Carry formula**:
$$S_{i,t}^{\text{Carry}} = \frac{c_{i,t}}{\sigma_{r_{i,t}}}$$

### Inputs

| Name | Dtype | Frequency | Source |
|------|-------|-----------|--------|
| spot_rate | float64 | 1d | Bloomberg |
| forward_1m | float64 | 1d | Bloomberg |
| forward_6m | float64 | 1d | Bloomberg |
| bid_ask_spread | float64 | 1d | Historical avg x 1.5 |

### Parameters

| Name | Value | Tunable |
|------|-------|---------|
| lookback_min | 21 | No |
| lookback_max | 252 | No |
| hysteresis_threshold | 0.333 | Yes |
| vol_decay_diagonal | 252 (1Y) | Yes |
| vol_decay_offdiag | 756 (3Y) | Yes |
| rebalance_freq_medium | 20 (monthly) | No |
| rebalance_freq_short | 5 (weekly) | No |
| max_position_pct | 0.15 | Yes |
| dispersion_floor_percentile | 0.25 | Yes |
| n_currencies | 24 | No |

## Data Schema

**Universe**: 24 USD/FX pairs (G10 + select EM)

### Columns

| Name | Dtype | Nullable |
|------|-------|----------|
| date | datetime | No |
| currency_pair | str | No |
| spot_rate | float64 | No |
| forward_1m | float64 | No |
| forward_6m | float64 | Yes |
| bid_ask_spread | float64 | No |
| total_return | float64 | No |

### Splits

| Split | Start | End |
|-------|-------|-----|
| Train | 2000-01-01 | 2014-12-31 |
| Validate | 2015-01-01 | 2018-12-31 |
| Holdout | 2019-01-01 | 2024-12-31 |

**Holdout touched: false**

## Module APIs

### `signals`
| Function | Args | Returns | Description |
|----------|------|---------|-------------|
| compute_momentum_signal | returns: DataFrame, lookback_min: int, lookback_max: int, hysteresis_threshold: float | DataFrame | Momentum signal with dispersion deflation |
| compute_carry_signal | spot: Series, forward: Series, volatility: Series | Series | Carry signal: forward-spot spread / vol |
| compute_mso_signal | ir_spread: Series, windows: list[int] | Series | Momentum Spill-Over from rate changes |

### `portfolio`
| Function | Args | Returns | Description |
|----------|------|---------|-------------|
| build_ts_weights | signals: DataFrame, volatilities: DataFrame, max_position: float | DataFrame | Time-series IVW weights |
| build_cs_weights | signals: DataFrame, betas: Series, max_position: float | DataFrame | Cross-sectional beta-neutral weights |
| apply_tranching | target_weights: DataFrame, n_tranches: int | DataFrame | Daily tranching of rebalanced portfolio |

### `risk`
| Function | Args | Returns | Description |
|----------|------|---------|-------------|
| estimate_covariance | returns: DataFrame, decay_diag: int, decay_offdiag: int | ndarray | Exp-weighted cov from 3-day non-overlapping returns |
| compute_usd_beta | returns: DataFrame, lookback: int | Series | Rolling beta to USD PC1 |

### `backtest`
| Function | Args | Returns | Description |
|----------|------|---------|-------------|
| run_backtest | weights: DataFrame, returns: DataFrame, costs: DataFrame | DataFrame | T+1 execution backtest |
| compute_metrics | backtest_results: DataFrame | dict | Sharpe, CAGR, max DD, Calmar, Sortino, turnover |

## Test Plan

### Unit Tests
- `compute_momentum_signal`: all-positive returns → signal ≈ +1; alternating returns → signal ≈ 0
- `compute_carry_signal`: positive carry → positive signal; negative carry → negative signal
- `build_cs_weights`: beta-neutrality (Σ w·β ≈ 0); absolute sum = 1
- `estimate_covariance`: identity returns → diagonal matrix; perfect correlation → ρ ≈ 1

### Property Tests
- |Σ weights| = 1.0 at every rebalance (time-series)
- Σ w·β ≈ 0 at every rebalance (cross-sectional)
- No position exceeds max_position_pct
- Raw momentum signal bounded in [-1, 1]

## Success Criteria

| Metric | Threshold | Direction |
|--------|-----------|-----------|
| Sharpe (momentum TS) | 0.4 | > |
| Sharpe (carry CS) | 0.5 | > |
| Max drawdown | 25% | < |
| Avg daily turnover | 10% | < |

## Notes

Priority: Carry (CS max-Sharpe, SR 0.79 reported) and Momentum (TS IVW, SR 0.60 reported) first. Value, MSO, COFFEE, CFTC are extensions. COFFEE requires DTCC data. CFTC reversal has discretisation risk.
