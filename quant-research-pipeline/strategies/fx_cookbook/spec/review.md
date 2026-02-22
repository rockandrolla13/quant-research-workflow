## Review: spec.yaml + formula.md
### Symbol Consistency
- [WARN]: The symbol `$\sigma_{r_{i,t}}$` (volatility of asset returns) is used in the `signal.formula_latex` for the carry signal and in other signal formulas (Eq. 7, 10, 17) but is not explicitly listed in `signal.inputs` or `signal.parameters` within `spec.yaml`. It is a derived quantity, likely from `total_return` using methods in the `risk` module.
- [WARN]: The symbol `N` in Eq. 6 (`c_t^{\text{Carry}} = \frac{1}{N} \sum_{h=0}^{N-1} c_{t-h}`) is used as a lookback window for carry smoothing, but the symbol table defines `N` as "Number of currency pairs in pool" (`n_currencies` parameter). This is an internal inconsistency within `formula.md`.
### LaTeX Validity
- [PASS]: The `signal.formula_latex` field in `spec.yaml` is syntactically valid LaTeX.
### Dimensional Consistency
- [PASS]: The signal definitions, formulas, and expected outputs across `formula.md` and `spec.yaml` appear dimensionally consistent. For instance, momentum and carry signals are dimensionless, and portfolio weights sum to 1.
### Test Case Consistency
- [PASS]: Unit test cases are largely consistent with the mathematical formulas. The expected outcomes for `compute_momentum_signal`, `compute_carry_signal`, and `estimate_covariance` align with the defined equations. Property tests are also consistent with portfolio construction rules. A minor ambiguity exists for `build_cs_weights` when all `signals` are `all_equal` and the method is "long top half, short bottom half", but a reasonable interpretation allows for consistency.
### Data Frequency Compatibility
- [PASS]: The daily frequency of `spot_rate`, `forward_1m`, `forward_6m`, `bid_ask_spread`, and `total_return` specified in `spec.yaml` is compatible with the daily signal calculations and various lookback windows (e.g., 21-252 days for momentum) described in `formula.md`. Rebalance frequencies (5-day, 20-day) are also well-supported by daily data.
### Unstated Assumptions
- [WARN]: **Total Return Definition**: The "Computation Steps" mention `total_return` as "spot return + implied carry from 1M forward". This derivation is crucial but not explicitly detailed in `formula.md` or `spec.yaml`'s `data_schema`. — suggested addition: Define how `total_return` is calculated if it's not a direct raw input.
- [WARN]: **Volatility ($\sigma_{r_i}$) Calculation**: While `risk.estimate_covariance` is described, the specific method (e.g., EWMA lookback, non-EWMA lookback) for deriving the *scalar* asset volatility $\sigma_{r_i}$ (used in carry, IVW, and momentum final weights) from the covariance matrix or daily returns is not explicitly stated. — suggested addition: Specify the exact calculation method and lookback for scalar asset volatility $\sigma_{r_i}$.
- [WARN]: **Currency Pair Convention**: The universe is "24 USD/FX pairs" but the convention (e.g., always XXX/USD or explicit base/quote for each) is not stated. This impacts carry and return calculations. — suggested addition: Clarify the consistent pricing convention for all currency pairs (e.g., all quoted as Base/USD).
- [WARN]: **Hysteresis Initialization**: The initial value of `$\hat{S}_{t-1}$` for the hysteresis mechanism in Eq. 3 is not defined. — suggested addition: Specify the initial condition for $\hat{S}_t$ (e.g., zero, or derived from first non-threshold-crossing $S_t$).
- [WARN]: **USD PC1 Derivation**: The method for deriving the "USD PC1" (Principal Component 1 of USD-based returns) for beta-neutralization is not described. — suggested addition: Briefly describe how the USD PC1 factor is constructed.

### Summary
PASS WITH WARNINGS
The strategy specification is generally well-defined and consistent, but minor clarifications are needed regarding symbol usage, definition of derived inputs, and certain computational assumptions.