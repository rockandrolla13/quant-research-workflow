Process a PDF through the full extraction → synthesis → spec → review pipeline.

$ARGUMENTS is the strategy_id. The PDF must already be at strategies/$ARGUMENTS/input/source.pdf

## Step 1: Extract

Run:
```bash
.venv-extract/bin/python tools/ingest.py strategies/$ARGUMENTS/input/source.pdf --strategy-id $ARGUMENTS
```

Verify strategies/$ARGUMENTS/extract/raw.md exists and has >500 characters.
If extraction fails, report the error and stop.

## Step 2: Synthesise

Read strategies/$ARGUMENTS/extract/raw.md in full.

Write strategies/$ARGUMENTS/synth/strategy.md with these sections (all required):
- Thesis / Intuition (2-4 sentences, WHY does this work, what inefficiency)
- Data Requirements (asset class, instruments, frequency, vendors, history)
- Signal Definition (plain English, reference formula.md for formal defs)
- Execution Assumptions (how would this trade, RFQ/algo/passive, latency, notional)
- Risk Controls (position limits, drawdown stops, concentration, kill switches)
- Failure Modes (when does this break, be specific)
- Minimal Backtest Plan (simplest confirmatory/rejecting test)

Write strategies/$ARGUMENTS/synth/formula.md with these sections (all required):
- Symbol Table (table: symbol, meaning, type, units — EVERY symbol used)
- Equations (all equations in LaTeX with numbered subsections, each with "where" block)
- Computation Steps (ordered algorithm to compute the signal)
- Edge Cases (missing data, stale quotes, look-ahead bias risks)

## Step 3: Write Spec

Write strategies/$ARGUMENTS/spec/SPEC.md (human-readable implementation spec).
Write strategies/$ARGUMENTS/spec/spec.yaml (machine-readable, Codex builds from this).

spec.yaml must include:
- strategy_id, version: "v1.0", status: "draft"
- hypotheses with h0, h1, test_statistic, alpha, expected_effect_size
- signal with name, formula_latex, inputs (each: name, dtype, frequency, source)
- data with universe, columns, splits (train/validate/holdout), holdout.touched: false
- modules with function signatures (EXACT Python, not pseudocode)
- tests.unit with at least 2 cases per function
- success_criteria.metrics with name, threshold, direction

## Step 4: Validate Gate

Run:
```bash
.venv-extract/bin/python tools/validate_spec.py strategies/$ARGUMENTS/spec/spec.yaml
```

If it fails, read the error list, fix spec.yaml, re-run. Loop until exit 0.
Do NOT present the spec to the user until the gate passes.

## Step 5: Gemini Review

Run:
```bash
.venv-extract/bin/python tools/call_gemini.py --mode review \
  --spec strategies/$ARGUMENTS/spec/spec.yaml \
  --formula strategies/$ARGUMENTS/synth/formula.md \
  --output strategies/$ARGUMENTS/spec/review.md
```

Read strategies/$ARGUMENTS/spec/review.md.
If any FAIL items: fix spec.yaml, re-run validate_spec.py, re-run Gemini review. Loop.
If PASS WITH WARNINGS: fix the warnings if straightforward, or note them for the user.

## Step 6: Present to User

Show the user:
1. A summary of the strategy thesis
2. The key equations
3. Any remaining warnings from Gemini review
4. Ask: "Ready to lock the spec? After lock, Codex builds from this."

Stop here. User must approve and run git tag manually.
