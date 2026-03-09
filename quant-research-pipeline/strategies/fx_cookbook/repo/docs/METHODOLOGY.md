# Methodology

This implementation follows `strategies/fx_cookbook/spec/spec.yaml` (v1.2) and provides a minimal but complete
pipeline for momentum replication, generalised across asset classes via an adapter layer.

## Data and Returns
- Raw inputs are asset-class-specific (FX: spot/forward rates; credit: spreads/duration).
- An adapter transforms raw data into a canonical schema: `(date, asset, total_return, bid_ask_spread)`.
- The domain stack (signals through validation) operates on this canonical schema only.
- See `docs/DATA_CONTRACT.md` for adapter-specific return computations.

## Signals
### Momentum (Eq. 1–4)
- For each currency, compute 3-day non-overlapping total returns and average the sign over lookbacks 21–252.
- Apply hysteresis: retain prior signal when |raw| < threshold.
- Deflate by dispersion (std of sign readings), with a floor at the configured percentile.

### Carry (Eq. 5–7)
- Carry = (spot - forward) / forward, smoothed over the configured window, then divided by volatility.

## Risk and Volatility
- EWMA covariance is computed using 3-day non-overlapping returns and averaged across 3 offsets.
- Volatility is derived from the diagonal of the covariance matrix.
- USD PC1 is computed from the correlation matrix of rolling returns.

## Portfolio Construction
- Time-series weights use inverse-volatility weighting and are normalized to abs-sum = 1.
- Cross-sectional weights are beta-neutralized to USD PC1, then normalized.
- Optional tranching produces staggered sub-portfolios.

## Backtest
- T+1 execution; turnover-based transaction costs applied via bid/ask spreads.
- Metrics: Sharpe, CAGR, max drawdown, Calmar, Sortino, avg turnover.

## Validation
- Two-sided t-test on annualized Sharpe against 0.
- Success criteria applied to metrics with explicit thresholds.
- GO/NO_GO based on hypothesis and criteria.
