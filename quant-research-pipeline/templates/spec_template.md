# Spec Template

Used by Claude (Stage 3) to produce `spec/SPEC.md` and `spec/spec.yaml`
from `synth/strategy.md` and `synth/formula.md`.

---

## spec.yaml structure (machine-readable, Codex builds from this)

```yaml
strategy_id: "<id>"
version: "v1.0"
status: "draft"  # draft → review → locked

hypotheses:
  h0: "<null hypothesis — signal has zero predictive power after costs>"
  h1: "<alternative — signal generates positive risk-adjusted returns>"
  test: "<test statistic, e.g. two-sided t-test on annualised Sharpe>"
  alpha: 0.05
  effect_size: 0.4  # minimum Sharpe to be economically meaningful

signal:
  name: "<signal_name>"
  formula_latex: "<primary signal formula in LaTeX>"
  inputs:
    - {name: "<col>", dtype: "<float64|datetime|str>", frequency: "1d", source: "<vendor>"}

data_schema:
  universe: "<description of asset universe>"
  columns:
    - {name: "<col>", dtype: "<type>", nullable: <bool>}
  splits:
    train: {start: "YYYY-MM-DD", end: "YYYY-MM-DD"}
    validate: {start: "YYYY-MM-DD", end: "YYYY-MM-DD"}
    holdout: {start: "YYYY-MM-DD", end: "YYYY-MM-DD"}
  holdout_touched: false

module_apis:
  - module: signals
    functions:
      - name: "<fn_name>"
        args: "<exact Python signature>"
        returns: "<return type>"
        description: "<one-line docstring>"
        provenance: "paper|inferred|design_choice"  # WHERE did this come from?
  - module: portfolio
    functions: [...]
  - module: risk
    functions: [...]
  - module: backtest
    functions: [...]
  - module: validation
    functions: [...]

test_plan:
  unit_tests:
    - function: "<fn_name>"
      cases:
        - {input: "<description>", expected: "<description>"}
  property_tests:
    - {invariant: "<property that must always hold>"}

success_criteria:
  metrics:
    - {name: "sharpe", threshold: 0.4, direction: ">"}
    - {name: "max_drawdown", threshold: 0.25, direction: "<"}
```

## Key rules

1. Every function signature must include exact Python types
2. Every function must have a `provenance` field:
   - `paper` — directly from the paper's description
   - `inferred` — reasonable interpretation of the paper
   - `design_choice` — our decision, paper doesn't specify
3. `formula_latex` must match an equation in formula.md
4. `data_schema.columns` must cover all `signal.inputs`
5. `holdout_touched: false` until explicitly approved
6. At least 2 unit test cases per function
7. At least 1 property test per module

## SPEC.md structure (human-readable)

Same content as spec.yaml but formatted for reading:
- Meta table (strategy_id, version, status)
- Hypotheses table
- Signal section with LaTeX equations
- Inputs table
- Parameters table (with tunable yes/no)
- Data schema section
- Module APIs section (function signature tables per module)
- Test plan section
- Success criteria table
- Notes (priority order, extensions, caveats)
