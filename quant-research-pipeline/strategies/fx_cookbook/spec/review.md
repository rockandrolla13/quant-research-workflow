## Review: spec.yaml + formula.md
### Symbol Consistency
- [X] PASS: All symbols used in the in-scope (Momentum and Carry) formulas in `formula.md` are either explicitly defined as `signal.inputs`, `signal.parameters`, or clearly derived intermediate values within the `module_apis` definitions in `spec.yaml`. The constant '21' used for daily carry conversion in Eq. 0 is a minor fixed value within the formula, not a missing parameter.

### LaTeX Validity
- [X] PASS: The `formula_latex` field in `spec.yaml` uses valid LaTeX syntax and renders correctly based on standard LaTeX rules.

### Dimensional Consistency
- [X] PASS: All equations for Momentum (Eq 0-4, 17) and Carry (Eq 5-7, 16) are dimensionally consistent. For example, returns are dimensionless, signal values are dimensionless, and the risk-adjusted carry signal/weights appropriately handle the units of volatility (%). No circular references were identified.

### Test Case Consistency
- [X] PASS: All unit tests and property tests specified in `spec.yaml` are consistent with the mathematical formulas described in `formula.md` and the functional descriptions in `module_apis`. The expected outcomes logically follow from the inputs based on the defined equations and operations.

### Data Frequency Compatibility
- [X] PASS: All `signal.inputs` and `data_schema.columns` are specified with a `frequency: 1d`, which is fully compatible with the daily granularity required by the lookback windows, rebalancing frequencies, and other time-series computations (e.g., return calculations, smoothing, volatility estimation) detailed in the formulas and parameters.

### Unstated Assumptions
- [X] WARN: 
    - The constant '21' in Eq. 0 for converting 1-month forward spread to daily implied carry assumes 21 business days in a month. While common, explicitly defining this as a constant or linking it to an average business days parameter would enhance clarity. Suggested addition: "The value '21' in Eq. 0 for daily carry conversion represents the assumed number of business days in a month and is a fixed constant within this formula."
    - The strategy implicitly operates on "business days" for all time-based parameters and calculations (e.g., lookback_min, rebalance_freq_medium). Making this explicit would improve precision. Suggested addition: "All lookback periods and frequencies (e.g., 21, 252, 20 days) refer to business days."
    - The specific quoting convention for the "24 USD/FX pairs" (e.g., EUR/USD vs. USD/EUR) is not explicitly stated. While "USD/FX pairs" often implies the foreign currency is the base, clarifying this would remove potential ambiguity for rate calculations (e.g., for positive carry definition). Suggested addition: "All FX pairs are consistently quoted using the [Foreign Currency]/USD convention."

### Summary
PASS WITH WARNINGS
The specification is highly detailed and consistent, with strong alignment between formulas, data, and test plans. Minor clarifications regarding implicit constants, operating days, and FX quoting conventions would enhance absolute precision.