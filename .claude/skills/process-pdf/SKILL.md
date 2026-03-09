Process a PDF through the full extraction → synthesis → spec → review pipeline.

$ARGUMENTS is the strategy_id. The PDF must already be at strategies/$ARGUMENTS/input/source.pdf

---

## Stage 1: Extract (two-pass)

Run:
```bash
./tools/run-extract.sh python tools/ingest.py strategies/$ARGUMENTS/input/source.pdf --strategy-id $ARGUMENTS
```

This produces:
- `extract/raw.md` — raw OCR/layout extraction (pass 1)
- `artifacts/01-extraction.md` — tagged structured extraction (pass 2)

Verify both files exist. If `artifacts/01-extraction.md` is missing (tagging failed),
read `extract/raw.md` instead and proceed — but warn the user that tags are missing.

Read `artifacts/01-extraction.md` (or `extract/raw.md` as fallback).
Verify it contains tagged elements: grep for `[SIG:`, `[EQ:`, `[PARAM:`.
If fewer than 5 tags total, the extraction quality is low — warn the user.

Update: `.pipeline_state.yaml` → stage: extract, status: complete

---

## Stage 2: Synthesise

Read the templates:
- `templates/synthesis_template.md` — for the required sections and format

Read `artifacts/01-extraction.md` in full.

Write `synth/strategy.md` following the synthesis template. Required sections:
1. Core Claim (1 sentence)
2. Thesis / Intuition (2-4 sentences, be opinionated)
3. Data Requirements (table format)
4. Signal Decomposition (break into independent components, reference [SIG:n] and [EQ:n] tags)
5. Dependency Graph (mermaid diagram)
6. Execution Assumptions
7. Risk Controls (note paper vs added)
8. Implementation Decisions (at least 3 open choices with approaches)
9. What's Missing (numerical stability, edge cases, scaling)
10. Failure Modes (be specific)
11. Stress Test (which component most likely to fail)
12. Minimal Backtest Plan

Write `synth/formula.md` following the synthesis template. Required sections:
1. Scope (IN-SCOPE vs OUT-OF-SCOPE signals)
2. Symbol Table (every symbol, no ambiguity)
3. Equations (all LaTeX with numbered subsections + "Where" blocks)
4. Computation Steps (ordered algorithm per signal)
5. Edge Cases

Cross-reference: every [EQ:n] tag from extraction must appear in formula.md.
Every [SIG:n] tag must map to a component in strategy.md Signal Decomposition.

Also write `artifacts/02-synthesis.md` as a combined artifact:
```markdown
# Synthesis: $ARGUMENTS
## Core Claim
<from strategy.md>
## Method Decomposition
<from strategy.md Signal Decomposition>
## Dependency Graph
<from strategy.md>
## Implementation Decisions
<from strategy.md>
## What's Missing
<from strategy.md>
```

Update: `.pipeline_state.yaml` → stage: synth, status: complete

---

## Stage 3: Write Spec

Read the templates:
- `templates/spec_template.md` — for spec.yaml structure and rules

Read `synth/strategy.md` and `synth/formula.md`.

Write `spec/SPEC.md` (human-readable implementation spec).
Write `spec/spec.yaml` (machine-readable, Codex builds from this).

Key rules:
- Every function must have a `provenance` field: `paper`, `inferred`, or `design_choice`
- `formula_latex` must match an equation in formula.md
- At least 2 unit test cases per function
- At least 1 property test per module
- `holdout_touched: false`

Also write `artifacts/03-spec.md`:
```markdown
# Spec: $ARGUMENTS
## Modules
<module table from spec.yaml>
## Data Flow
<mermaid diagram: input → signals → portfolio → backtest → validation>
## Open Questions
<any design_choice items that need user confirmation>
## Provenance Summary
- From paper: N functions
- Inferred: N functions
- Design choice: N functions
```

Update: `.pipeline_state.yaml` → stage: spec, status: complete

---

## Stage 4: Validate Gate

Run:
```bash
./tools/run-extract.sh python tools/validate_spec.py strategies/$ARGUMENTS/spec/spec.yaml
```

If it fails, read the error list, fix spec.yaml, re-run. Loop until exit 0.
Do NOT present the spec to the user until the gate passes.

---

## Stage 5: Gemini Review

Run:
```bash
./tools/run-extract.sh python tools/call_gemini.py --mode review \
  --spec strategies/$ARGUMENTS/spec/spec.yaml \
  --formula strategies/$ARGUMENTS/synth/formula.md \
  --output strategies/$ARGUMENTS/spec/review.md
```

Read `spec/review.md`.
If any FAIL items: fix spec.yaml, re-run validate_spec.py, re-run Gemini review. Loop.
If PASS WITH WARNINGS: fix straightforward warnings, or note them for the user.

---

## Stage 6: Present to User

Show the user:
1. Tag summary from extraction (how many SIG, EQ, PARAM, etc.)
2. Core claim and thesis (1 paragraph)
3. Signal decomposition (component list)
4. Key equations (the 3-5 most important)
5. Provenance summary (how many functions from paper vs inferred vs design choice)
6. Any remaining warnings from Gemini review
7. Open questions from spec (design_choice items that need confirmation)

Ask: "Ready to lock the spec? After lock, Codex builds from this."

Stop here. User must approve. Then run:
```bash
git tag spec-$ARGUMENTS-v1.0
```
