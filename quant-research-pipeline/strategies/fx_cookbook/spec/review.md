## Review: spec.yaml + formula.md
### Symbol Consistency
- [PASS] The symbols used within the `signal.formula_latex` field (`hat{S}_t`, `tilde{sigma}_t`, `tilde{sigma}^{\text{floor}}_t`, `c_{i,t}`, `sigma_{r_{i,t}}`) are either explicitly defined as inputs/parameters in `spec.yaml` (e.g., `dispersion_floor_percentile` for `tilde{sigma}^{\text{floor}}_t`) or are clearly intermediate derivations from the specified inputs (e.g., `c_{i,t}` from `spot_rate` and `forward_1m`, `sigma_{r_{i,t}}` from `total_return`). Symbols in `formula.md` pertaining to extension signals (Value, MSO, COFFEE, CFTC) are not expected in the current `spec.yaml` signal definition and are appropriately noted.

### LaTeX Validity
- [PASS] The `signal.formula_latex` field uses valid LaTeX syntax and appropriate commands for mathematical notation, subscripts, superscripts, and text labels.

### Dimensional Consistency
- [PASS] The mathematical formulas maintain dimensional consistency. Returns ($r$), signals ($S, \hat{S}, \tilde{\sigma}, c$), and portfolio weights ($w$) are appropriately dimensionless or defined as percentages. The risk-adjusted carry signal ($S_{i,t}^{\text{Carry}}$) and time-series momentum weights ($W_{i,t}^{\text{Trend}}$) are dimensionless, as they involve ratios of quantities with the same units (e.g., percent returns/volatility).

### Test Case Consistency
- [PASS] All unit tests specified in `test_plan.unit_tests` are consistent with the corresponding mathematical formulas and descriptions in `formula.md` and `module_apis` in `spec.yaml`. Expected outcomes logically follow from the defined functions and inputs. Property tests also align with general expectations for portfolio behavior and signal characteristics.

### Data Frequency Compatibility
- [PASS] All `signal.inputs` are specified with a `1d` frequency, which is compatible with the daily computation steps, lookback periods (e.g., `lookback_min`, `lookback_max`), and rebalancing frequencies specified in the strategy. The use of `total_return` (derived daily) for momentum and spot/forward rates for carry aligns with this daily frequency.

### Unstated Assumptions
- [WARN] The `signal.name` is `fx_cookbook_composite`, and `signal.formula_latex` provides two distinct formulas (one for momentum, one for carry) separated by a semicolon, but does not define how these two components are combined into a *single composite signal*. The `success_criteria` further imply separate evaluations for `sharpe_ratio_momentum_ts` and `sharpe_ratio_carry_cs`. This creates ambiguity regarding whether `fx_cookbook_composite` produces a single aggregated signal or if it represents a meta-strategy comprising two independently managed sub-strategies. — suggested addition: The `signal.formula_latex` should explicitly define the aggregation method (e.g., simple average, inverse volatility weighted average, etc.) if a single composite signal is intended, or the strategy structure should clarify that these are distinct sub-signals/sub-portfolios.

### Summary
PASS WITH WARNINGS
The strategy is well-defined mathematically and programmatically, with consistent symbols, valid LaTeX, and coherent test cases. The primary warning relates to the ambiguity in how the named "composite" signal actually combines its momentum and carry components.