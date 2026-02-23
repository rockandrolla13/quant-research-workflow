## Review: spec.yaml + formula.md
### Symbol Consistency
- [WARN]: The `formula.md` document defines symbols and formulas for "Value" (`REER`, `PROD`, `TOT`, `varepsilon`) and other extension signals (MSO, COFFEE, CFTC: `IR spread`, `NotionalCalls`, `NotionalPuts`, `I^{NC}`, `S^{SNC}`) that do not have corresponding entries in `spec.yaml`'s `signal.inputs` or `parameters`. While `spec.yaml`'s `notes` clarify these are extensions, their presence in `formula.md` (which is presented as defining the `fx_cookbook` strategy) creates a scope mismatch.
- [PASS]: All symbols directly relevant to the "momentum" and "carry" signals, as indicated by `spec.yaml`'s `formula_latex` and `signal.inputs`, are consistently defined or derivable from the `spec.yaml` inputs and parameters.

### LaTeX Validity
- [PASS]: The `formula_latex` field in `spec.yaml` contains syntactically valid LaTeX for the momentum and carry signal definitions.

### Dimensional Consistency
- [WARN]: The Carry Signal `S_{i,t}^{\text{Carry}} = c_{i,t}^{\text{Carry}} / \sigma_{r_{i,t}}` (Eq 7) presents a potential dimensional ambiguity. `c_{i,t}^{\text{Carry}}` (from Eq 5 & 6) is a dimensionless ratio, while `$\sigma_{r_{i,t}}$` is described in the symbol table as `% annualised`. For `S_{i,t}^{\text{Carry}}` to be a true dimensionless Sharpe-like ratio, either `c_{i,t}^{\text{Carry}}` should be implicitly annualised or `$\sigma_{r_{i,t}}$` should be expressed as a daily volatility (or a consistent annualised decimal) to match `c_{i,t}^{\text{Carry}}`'s units. Currently, this implicitly assumes a conversion or interpretation that is not explicitly stated.
- [PASS]: All other formulas for momentum and portfolio weights appear dimensionally consistent (e.g., dimensionless signals, dimensionless weights).

### Test Case Consistency
- [WARN]: The `compute_carry_signal` unit test `input: {"spot": 1.0, "forward": 0.99, "volatility": 0.10}` and `expected: "carry signal = (1.0 - 0.99) / 0.99 / 0.10 ≈ 0.101"` uses `volatility: 0.10`. This implies `0.10` is used as a dimensionless decimal in the division, which is consistent with the formula calculation. However, if `volatility` (i.e., `$\sigma_{r_{i,t}}$`) is `"% annualised"` as per the symbol table (e.g., 10%), then it needs to be made explicit that it's converted to `0.10` (a decimal) for calculation, which relates to the dimensional consistency warning above.
- [PASS]: All other unit and property test cases are logically consistent with the specified formulas and expected outcomes.

### Data Frequency Compatibility
- [PASS]: The primary momentum and carry signals defined in `spec.yaml`'s `formula_latex` and their associated computation steps are compatible with the `1d` frequency specified for `spot_rate`, `forward_1m`, `forward_6m`, `bid_ask_spread`, and `total_return` in `data_schema` and `signal.inputs`.
- [WARN]: The inputs for the extension signals (Value, MSO, COFFEE, CFTC) mentioned in `formula.md` (e.g., REER, PROD, TOT, IR spread, NotionalCalls/Puts, CFTC positions) are not specified in `spec.yaml`'s `signal.inputs` or `data_schema`. This is noted as acceptable in `spec.yaml`'s `notes` as they are extensions, but the formulas exist in the document.

### Unstated Assumptions
- [WARN]: **Consistency of Volatility Units and Annualisation**: The interpretation of `$\sigma_{r_{i,t}}$` (symbol table: `% annualised`) when used in division with dimensionless ratios (`$c_{i,t}^{\text{Carry}}$`) is implicitly assumed.
  - *Suggested addition*: Explicitly state whether `$\sigma_{r_{i,t}}$` is converted to a decimal (e.g., `10%` becomes `0.10`) for calculations, and clarify if `c_i` is implicitly annualised or `sigma_r_i` is implicitly a daily volatility for these specific formulas.
- [WARN]: **Scope of `formula.md`**: `formula.md` contains detailed descriptions and equations for signals (Value, MSO, COFFEE, CFTC) that are explicitly described as "extensions" and lower priority in `spec.yaml`'s `notes`, and for which inputs are not defined in `spec.yaml`.
  - *Suggested addition*: Add a clear disclaimer to `formula.md` distinguishing the core `fx_cookbook_composite` signals (Momentum, Carry) from the discussed extensions, or indicate that `formula.md` describes the *full* `fx_cookbook` family, not just `v1.2`'s `fx_cookbook_composite`.
- [WARN]: **"USD" in Universe**: The `data_schema.universe` includes "USD" in "24 USD/FX pairs: ... + USD". USD is generally a single currency, not a pair.
  - *Suggested addition*: Clarify that this refers to USD as the base or quote currency for all 24 pairs, or if "USD" itself represents a specific instrument or market.

### Summary
PASS WITH WARNINGS
The core momentum and carry signals are well-defined and consistent within the `spec.yaml` and `formula.md`. However, dimensional ambiguity in the carry signal's risk adjustment and scope inconsistencies regarding extension signals in `formula.md` warrant clarification.