## Review: spec.yaml + formula.md
### Symbol Consistency
- [ ] WARN: `total_return` (represented as $r_{t-h,t}$ in Eq. 1 and $r_{t+h}$ in Eq. 18) is a primary input for the momentum signal and mentioned in `data_schema.columns`, but not explicitly listed under `signal.inputs`. `$\sigma_{r_{i,t}}$` (asset return volatility, used in Eq. 7, 10, 15, 17) is crucial for both carry and momentum final weights but is neither an explicit input to the signal nor a parameter, and its derivation (e.g., lookback for volatility calculation) is not specified within the `signal` section.
  - Suggested addition: Add `total_return` to `signal.inputs`. Add a parameter for `asset_volatility_lookback` or `asset_volatility_decay` and specify how `$\sigma_{r_{i,t}}$` is derived from `total_return` within the `signal` definition or its `inputs` section.
### LaTeX Validity
- [x] PASS: All LaTeX formulas in `spec.yaml`'s `formula_latex` field and `formula.md` are syntactically valid.
### Dimensional Consistency
- [x] PASS: The formulas for momentum and carry signals, as well as portfolio weighting schemes, are dimensionally consistent. Signals and weights are dimensionless, and intermediate calculations maintain appropriate units (e.g., percentages, dimensionless ratios).
### Test Case Consistency
- [x] PASS: All unit test cases defined in `test_plan.unit_tests` are consistent with the mathematical formulas and descriptions provided in `formula.md` and `module_apis` descriptions. The expected outcomes logically follow from the input conditions as per the equations.
### Data Frequency Compatibility
- [x] PASS: The `1d` frequency specified for `signal.inputs` and implied for `data_schema.columns` (e.g., `total_return`) is compatible with the daily calculations required for momentum, carry, and risk metrics (e.g., lookback windows in days, daily rebalancing frequencies).
### Unstated Assumptions
- [ ] WARN:
    - **Carry smoothing window `L`**: Eq 6 uses `L` for smoothing the carry signal, but `L` is not defined as a parameter in `spec.yaml`.
        - Suggested addition: Add `carry_smoothing_window_days` to `signal.parameters`.
    - **Transaction cost parameter `cost_bps`**: The `backtest.compute_pnl` function takes `cost_bps` as an argument, but this parameter's value is not specified in `spec.yaml` or any global configuration.
        - Suggested addition: Add `transaction_cost_bps` to `signal.parameters` or a dedicated `backtest_parameters` section.
    - **USD PC1 definition**: The concept of "USD PC1" used for beta neutralisation (Eq 11) and `risk.compute_usd_beta` is not fully defined (e.g., which currencies included, calculation frequency, specific PCA methodology).
        - Suggested addition: Clarify the methodology for constructing "USD PC1" in the `risk` module or `notes`.
    - **Covariance matrix detail**: The `notes` specify "All covariance matrices use 3-day non-overlapping returns averaged over 3 starting offsets," which is a crucial detail for `risk.estimate_covariance` but is not explicitly part of the function's description in `module_apis`.
        - Suggested addition: Include this detail in the `description` for `risk.estimate_covariance`.

### Summary
PASS WITH WARNINGS
The specification and formulas are largely consistent and well-defined, particularly for the core momentum and carry signals. However, clarity on crucial input definitions (`total_return`, asset volatility derivation), missing parameters (`carry_smoothing_window`, `transaction_cost_bps`), and specific methodological details (USD PC1 construction) would enhance completeness and remove ambiguity.