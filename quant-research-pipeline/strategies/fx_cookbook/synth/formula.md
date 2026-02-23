# Mathematical Formulas: FX Cookbook

> Source: `extract/raw.md`
> All equations numbered for cross-reference with spec.yaml

**Scope**: This document covers the full FX Cookbook signal family. Only **Momentum** (Eq 0–4, 17) and **Carry** (Eq 5–7, 16) are implemented in `spec.yaml` v1.2 (`fx_cookbook_composite`). Value (Eq 8–9), MSO (Eq 12), COFFEE (Eq 13), and CFTC (Eq 14–15) are future extensions — their inputs and parameters are intentionally absent from `spec.yaml` until scheduled for implementation.

## Symbol Table

| Symbol | Meaning | Type | Units |
|--------|---------|------|-------|
| $r_{t-h,t}$ | Total return (spot + carry) from $t-h$ to $t$ | scalar | % |
| $S_t$ | Raw signal value at time $t$ | scalar | dimensionless |
| $\hat{S}_t$ | Preliminary signal (after hysteresis) | scalar | dimensionless |
| $\tilde{\sigma}_t$ | Momentum signal dispersion (std of sign readings across lookbacks) | scalar | dimensionless |
| $\sigma_{r_i}$ | Volatility of asset $i$ returns (used for IVW and carry risk-adjustment) | scalar | % annualised |
| $w_i$ | Portfolio weight for asset $i$ | scalar | fraction (sums to 1) |
| $\beta_i$ | Beta of currency $i$ to USD PC1 | scalar | dimensionless |
| $c_i$ | Carry (forward-spot spread) for asset $i$ | scalar | % |
| $F_i$ | Forward exchange rate for asset $i$ | scalar | USD/FX |
| $S_i$ | Spot exchange rate for asset $i$ | scalar | USD/FX |
| $N$ | Number of currency pairs in pool | int | count (24) |
| $h$ | Lookback window | int | business days |
| $\rho$ | Correlation matrix | matrix | dimensionless |
| $\text{REER}_{i,t}$ | Real effective exchange rate | scalar | index |
| $\text{PROD}_{i,t}$ | Productivity differential | scalar | log ratio |
| $\text{TOT}_{i,t}$ | Terms of trade index | scalar | index |
| $\varepsilon_{i,t}$ | REER misalignment (regression residual) | scalar | log units |
| $I^{NC}_{i,t}$ | CFTC non-commercial long positions | scalar | contracts |
| $S^{SNC}_{i,t}$ | CFTC non-commercial short positions | scalar | contracts |
| $\text{MIC}$ | Modified Information Coefficient | scalar | covariance units |
| $Q$ | Number of factor signals | int | count |

## Equations

### Eq. 0 — Total Return

$$
r_{i,t-h,t} = \frac{S_{i,t}}{S_{i,t-h}} - 1 + \sum_{\tau=t-h}^{t-1} \frac{S_{i,\tau} - F_{i,\tau}^{1M}}{F_{i,\tau}^{1M}} \cdot \frac{1}{21}
$$

**Where**: $S_{i,\tau}$ = spot rate, $F_{i,\tau}^{1M}$ = 1-month forward rate. First term is spot return over $h$ days. Second term accumulates daily implied carry (forward-spot spread annualised to daily by dividing by 21 business days). This is the `total_return` column in `data_schema`, computed from `spot_rate` and `forward_1m` inputs.

### Eq. 1 — Momentum Raw Signal

$$
S_t = \frac{1}{232} \sum_{h=21}^{252} \text{sign}(r_{t-h,t})
$$

**Where**: $r_{t-h,t}$ is the total return (spot + carry) over lookback $h$ business days. The signal averages the sign of returns across 232 lookback windows (21 to 252 days). Bounded: $S_t \in [-1, 1]$.

### Eq. 2 — Momentum Signal Dispersion

$$
\tilde{\sigma}_t = \sqrt{\frac{1}{232} \sum_{h=21}^{252} (\text{sign}(r_{t-h,t}) - S_t)^2}
$$

**Where**: Measures cross-lookback variability of the sign readings. Floor at 25th percentile of cross-asset distribution to prevent hyper-inflation.

### Eq. 3 — Momentum Hysteresis Noise Control

$$
\hat{S}_t = \begin{cases} \text{sign}(S_t), & |S_t| \ge \theta \\ \hat{S}_{t-1}, & |S_t| < \theta \end{cases}
$$

**Where**: $\theta = 1/3$. If raw signal is weak, retain prior position.

### Eq. 4 — Momentum Final Signal

$$
S_t^{\text{final}} = \frac{\hat{S}_t}{\max(\tilde{\sigma}_t,\; \tilde{\sigma}^{\text{floor}}_t)}
$$

**Where**: Deflation by signal dispersion. Higher dispersion → lower conviction → smaller position. $\tilde{\sigma}^{\text{floor}}_t$ = 25th percentile of the cross-asset $\tilde{\sigma}$ distribution on day $t$ (parameter `dispersion_floor_percentile`).

### Eq. 5 — Carry Signal (raw)

$$
c_i = \frac{S_i - F_i}{F_i}
$$

**Where**: $S_i$ = spot, $F_i$ = 1-month forward. Positive carry = long position earns positive roll.

### Eq. 6 — Carry Signal (smoothed)

$$
c_t^{\text{Carry}} = \frac{1}{L} \sum_{h=0}^{L-1} c_{t-h}
$$

**Where**: $L$-day moving average for noise reduction ($L$ = smoothing window, distinct from $N$ = number of currencies).

### Eq. 7 — Carry Signal (risk-adjusted)

$$
S_{i,t}^{\text{Carry}} = \frac{c_{i,t}^{\text{Carry}}}{\sigma_{r_{i,t}}}
$$

**Where**: Carry divided by asset return volatility $\sigma_{r_{i,t}}$ (not momentum signal dispersion $\tilde{\sigma}$). Resembles ex-ante Sharpe ratio.

### Eq. 8 — Value: DOLS Panel Regression

$$
\log(\text{REER}_{i,t}) = \alpha_i + \beta^1 \text{PROD}_{i,t} + \beta^2 \text{TOT}_{i,t} + \theta_0 + \varepsilon_{i,t}
$$

$$
\theta_0 = \sum_{s=-1}^{1} (\psi_s^1 \Delta\text{PROD}_{i,t+s} + \psi_s^2 \Delta\text{TOT}_{i,t+s})
$$

**Where**: Dynamic OLS with leads/lags. $\alpha_i$ = country fixed effects. Estimated per panel (5 panels: EM commodity exporters/importers, East Asian tigers, G10 commodity exporters/importers).

### Eq. 9 — Value Signal

$$
S_{i,t}^V = \varepsilon_{i,t}
$$

**Where**: The residual from Eq. 8, converted from REER to USD/FX space via matrix inversion / least squares.

### Eq. 10 — Inverse Volatility Weights (IVW)

$$
w_i^{\text{IVW}} = \frac{1/\sigma_{r_i}}{\sum_j 1/\sigma_{r_j}}
$$

**Where**: Used for time-series momentum and short-term signal portfolios.

### Eq. 11 — Beta Neutralisation (cross-sectional portfolios)

$$
\arg\min_w \sum_{i=1}^N (w_i - \tilde{w}_i)^2 \quad \text{s.t.} \quad \sum_i w_i \beta_i = 0
$$

**Where**: $\tilde{w}_i$ = initial weights (equal or rank-based), $\beta_i$ = rolling 1-year beta to USD PC1.

### Eq. 12 — Momentum Spill-Over (MSO) Signal

Steps:
1. $\Delta IR_{i,h} = \text{annualised change in 6M interest rate spread over } h \in \{21, 42, 63\} \text{ days}$
2. $\sigma_{IR,h} = \text{annualised vol of daily changes in 6M IR diff over same windows}$
3. $\text{ratio}_h = \Delta IR_{i,h} / \sigma_{IR,h}$
4. $S_t^{\text{MSO}} = \frac{1}{3} \sum_{h} \text{ratio}_h$, then 1-month moving average

**Filter**: Remove asset if 1-year correlation between past 1-day IR spread moves and future 1-day FX returns is negative.

### Eq. 13 — COFFEE Signal

$$
S_t^{\text{COFFEE}} = \frac{\text{NotionalCalls}_{4w} - \text{NotionalPuts}_{4w}}{\sigma_{1y}(\text{NotionalCalls}_{4w} - \text{NotionalPuts}_{4w})}
$$

**Where**: European options with |delta| ∈ [0.25, 0.75], expiry < 1 year. 4-week aggregate volume. Standardised by 1-year rolling vol.

### Eq. 14 — CFTC Continuation Signal

$$
S_{i,t}^{\text{CFTC,C}} = \frac{\sum_{h=0}^{3} I_{i,t-h}^{NC} - \sum_{h=0}^{3} S_{i,t-h}^{SNC}}{\sum_{h=0}^{3} I_{i,t-h}^{NC} + \sum_{h=0}^{3} S_{i,t-h}^{SNC}}
$$

**Where**: 4-week summed net positioning ratio from non-commercial traders.

### Eq. 15 — CFTC Reversal Signal

1. $z_h = \text{z-score of net position over lookback } h \in \{1M, 2M, 3M\}$
2. $\bar{z} = \frac{1}{3}(z_{1M} + z_{2M} + z_{3M})$
3. $S_i^{\text{CFTC,R}} = -\bar{z} / \sigma_{r_i,6M}$

**Where**: Sign-flipped to represent reversal. Volatility-normalised. Cross-sectional only (time-series MIC ≈ 0).

### Eq. 16 — Max Sharpe Carry Weights

$$
\arg\max_w \frac{\sum_i w_i c_i}{\sqrt{\sum_i \sum_j w_i w_j \sigma_{i,j}}} \quad \text{s.t.} \quad \sum_i w_i \beta_i = 0
$$

**Where**: Maximise ex-ante Sharpe of carry portfolio subject to USD-beta neutrality and boundary constraints.

### Eq. 17 — Time-Series Momentum Final Weights

$$
W_{i,t}^{\text{Trend}} = \frac{S_{i,t}^{\text{final}} / \sigma_{r_{i,t}}}{\sum_j |S_{j,t}^{\text{final}} / \sigma_{r_{j,t}}|}
$$

**Where**: Combines the momentum signal (already deflated by signal dispersion via Eq. 4) with inverse volatility weighting (Eq. 10). The denominator $\sigma_{r_{i,t}}$ is asset return volatility, NOT signal dispersion $\tilde{\sigma}$ — using signal dispersion here would double-deflate.

### Eq. 18 — Modified Information Coefficient (MIC)

$$
\text{MIC}_{t,h}^{TS} = \mathbb{E}\left[\frac{r_{t+h} S_t}{\sum_{i=1}^N S_i^2}\right]
$$

$$
\text{MIC}_{t,h}^{CS} = \mathbb{E}\left[\frac{r_{t+h} (S_t - \text{median}(S_t))}{\sum_{i=1}^N (S_i - \text{median}(S_i))^2}\right]
$$

## Computation Steps

### Momentum Signal (per currency, per day):
1. Compute total return $r_{t-h,t}$ for each $h \in \{21, 22, ..., 252\}$ (from `data_schema.total_return` column = spot return + implied carry from 1M forward)
2. Take sign of each return → 232 binary values
3. Average signs → raw signal $S_t \in [-1, 1]$
4. Compute signal dispersion $\tilde{\sigma}_t$ (std of signs)
5. Apply hysteresis: if $|S_t| < 1/3$, keep $\hat{S}_{t-1}$; else $\hat{S}_t = \text{sign}(S_t)$
6. Deflate: $S_t^{\text{final}} = \hat{S}_t / \tilde{\sigma}_t$

### Carry Signal (per currency, per day):
1. Compute carry: $c_i = (S_i - F_i) / F_i$
2. Smooth: $N$-day moving average
3. Risk-adjust: divide by asset return volatility $\sigma_{r_i}$

### Value Signal (per currency, monthly):
1. Run DOLS panel regression of log(REER) on PROD + TOT with leads/lags
2. Extract residual $\varepsilon_{i,t}$
3. Convert from REER to USD/FX space

### Portfolio Construction (at each rebalance):
1. Compute signal for each currency
2. **TS**: Weight by signal / volatility, normalise absolute sum to 100%
3. **CS**: Rank by signal, long top half / short bottom half, beta-neutralise to USD PC1

## Edge Cases

- **Missing data**: Emerging market data starts later (1994+). Value signal requires GDP/ToT which have publication lags (2-month lag applied).
- **Stale quotes**: NDF markets (e.g., KRW, INR, TWD) may have wider spreads and less reliable forward rates.
- **Look-ahead bias**: DOLS regression uses leads/lags ($s = -1, 0, +1$). Must re-estimate panel at each rebalance using only data available at $t$.
- **Transaction cost estimation**: Fixed 1.5x historical average spread is a simplification. Real-world costs are time-varying and liquidity-dependent.
- **Carry definition in NDF markets**: Onshore rates ≠ NDF-implied rates. Must use NDF-implied yields.
- **CFTC reporting lag**: 4-business-day delay. Signal executed Monday for prior Tuesday data.
- **Signal dispersion floor**: 25th percentile floor prevents division by near-zero. Must be computed cross-sectionally each day.
