Generate a LaTeX writeup for strategy $ARGUMENTS from the locked spec.

## Prerequisites

Verify spec is locked:
```bash
git tag -l "spec-$ARGUMENTS-*"
```
If no tag exists, STOP and tell the user: "Spec is not locked. Run: git tag -a spec-$ARGUMENTS-v1 -m 'Locked'"

## Step 1: Generate tex/note.tex

Read:
- strategies/$ARGUMENTS/spec/SPEC.md
- strategies/$ARGUMENTS/spec/spec.yaml
- strategies/$ARGUMENTS/synth/formula.md
- strategies/$ARGUMENTS/synth/strategy.md

Write strategies/$ARGUMENTS/tex/note.tex with these sections:

1. **Abstract** (150 words max)
2. **Motivation** (from strategy.md thesis — economic mechanism)
3. **Mathematical Framework** (from formula.md — formal definitions, all equations)
4. **Pre-Registered Methodology**
   - Hypotheses (H0, H1, test, α from spec.yaml)
   - Data (universe, frequency, splits from spec.yaml)
   - Procedure (signal computation steps)
5. **Expected Results** (what H1 predicts — written BEFORE seeing data)
6. **Implementation Notes** (module structure from spec.yaml, link to repo)
7. **Risk Analysis** (from spec risks section)

CRITICAL: Results section must be COMMENTED OUT:
```latex
% \section{Results}
% UNCOMMENT ONLY AFTER HOLDOUT EVALUATION.
% This section must remain empty until the single-touch holdout run.
```

Use standard article class, amsmath, amssymb, booktabs, hyperref.
Write refs.bib if the source PDF had references.

## Step 2: Compile check

```bash
cd strategies/$ARGUMENTS/tex && pdflatex -interaction=nonstopmode note.tex
```

If compilation fails, fix the LaTeX errors and retry.

## Step 3: Gemini verification

```bash
.venv-extract/bin/python tools/call_gemini.py --mode verify-tex \
  --tex strategies/$ARGUMENTS/tex/note.tex \
  --output strategies/$ARGUMENTS/tex/review_tex.md
```

Read review_tex.md. Fix any FAIL items. Re-verify if needed.

## Step 4: Report

Tell the user the LaTeX document is ready and whether it compiled cleanly.
