# Mathematical Formulas

> All math extracted and cleaned from the source paper.
> Source: `extract/raw.md` → feeds into `spec/spec.yaml` signal section

## Symbol Table

| Symbol | Description | Domain / Units |
|--------|-------------|----------------|
| $P_t$  | Closing price at time $t$ | $\mathbb{R}^+$ / USD |
| $R_t$  | Daily return at time $t$ | $\mathbb{R}$ / dimensionless |
| $N$    | Lookback period          | $\mathbb{Z}^+$ / days |
| $V_t$  | Volume at time $t$ | $\mathbb{Z}^+$ / shares or contracts |
| $RSI_t$| Relative Strength Index at time $t$ | $[0, 100]$ / dimensionless |

## Core Equations

<!-- Number every equation for cross-reference with spec.yaml signal.formula_latex -->

### Eq. 1 — Daily Return

$$
R_t = \frac{P_t - P_{t-1}}{P_{t-1}}
$$

**Where**:
- $P_t$: Closing price at time $t$
- $P_{t-1}$: Closing price at time $t-1$

### Eq. 2 — Relative Strength Index (RSI)

$$
RSI_t = 100 - \frac{100}{1 + RS}
$$
where
$$
RS = \frac{\text{Average Gain}}{\text{Average Loss}}
$$
Average Gain and Average Loss are calculated over a lookback period $N$.

**Where**:
- $RSI_t$: Relative Strength Index at time $t$
- $RS$: Relative Strength
- Average Gain: Average of positive price changes over $N$ periods
- Average Loss: Average of absolute negative price changes over $N$ periods

### Eq. 3 — RSI Crossover Signal

The RSI Crossover Signal ($S_t$) is generated based on the following rules:

$$
S_t = 
\begin{cases} 
  1 & \text{if } RSI_t > \text{overbought\_threshold} \text{ and } RSI_{t-1} \le \text{overbought\_threshold} \\
  -1 & \text{if } RSI_t < \text{oversold\_threshold} \text{ and } RSI_{t-1} \ge \text{oversold\_threshold} \\
  0 & \text{otherwise}
\end{cases}
$$

**Where**:
- $S_t$: Trading signal at time $t$ (1 for buy, -1 for sell, 0 for hold)
- $RSI_t$: Relative Strength Index at time $t$
- $\text{overbought\_threshold}$: The upper threshold for RSI (e.g., 70)
- $\text{oversold\_threshold}$: The lower threshold for RSI (e.g., 30)

## Parameters

| Parameter      | Value | Tunable? | Description                    |
|----------------|-------|----------|--------------------------------|
| `rsi_period`   | 14    | Yes      | Lookback period for RSI        |
| `overbought_threshold` | 70    | No       | Upper bound for RSI signals    |
| `oversold_threshold`   | 30    | No       | Lower bound for RSI signals    |

## Numerical Constants

| Constant | Value | Context                      |
|----------|-------|------------------------------|
| $\pi$    | 3.14159 | Mathematical constant        |
| $e$      | 2.71828 | Base of natural logarithm    |

## Notes

- The formulas for Average Gain and Average Loss in RSI calculation use a **Simple Moving Average (SMA)** over the `rsi_period`.
- All symbols used in equations are defined in the Symbol Table.
- Parameters listed here correspond to those in `spec.yaml`'s signal parameters.
