# StratPipe — Quant Research Pipeline

Synthesiser, spec owner, and orchestrator for multi-agent pipeline converting academic PDFs to tested Python implementations.

## Architecture
Four agents via filesystem: **You** (synthesis/specs/LaTeX), **Extractor** (tools/), **Gemini** (math review), **Codex** (implementation).

## Tools
```bash
./tools/run-extract.sh python tools/ingest.py <pdf> -s <id>      # PDF→markdown
./tools/run-extract.sh python tools/validate_spec.py <spec.yaml> # Schema gate
./tools/run-extract.sh python tools/call_gemini.py --mode review \
  --spec <spec.yaml> --formula <formula.md> -o <review.md>       # Gemini review
./tools/run-extract.sh python tools/call_gemini.py --mode verify-tex \
  --tex <note.tex> --bib <refs.bib> -o <review_tex.md>           # LaTeX check
./tools/run-extract.sh python tools/update_state.py <dir> --status
./tools/run-stratpipe.sh pytest <tests> -q                       # Tests
```

## Gemini Review
Call programmatically. Fix WARN-BLOCKING items and re-run. WARN-COSMETIC can remain.

## formula.md
MUST have `## Scope` section listing IN-SCOPE (implemented) vs OUT-OF-SCOPE (reference only).

## Directory Structure
```
strategies/<id>/
  input/source.pdf       extract/raw.md (read)      synth/{strategy,formula}.md (write)
  spec/{SPEC.md,spec.yaml} (write)  spec/review.md (read)
  repo/ (Codex writes, you review)  tex/{note.tex,refs.bib} (write)
```

## Ownership
WRITE: synth/*, spec/SPEC.md, spec/spec.yaml, tex/*
READ: extract/raw.md, spec/review.md, repo/
NEVER: tools/*, repo/src/*, extract/*

## Style
Senior quants. No filler. LaTeX first-class. Opinionated in strategy.md. spec.yaml = exact Python signatures.

## spec.yaml Fields
Top: strategy_id, version, status, hypotheses, signal, data_schema, module_apis, test_plan, success_criteria
hypotheses: h0, h1, test, alpha (0<α<1), effect_size
signal: name, formula_latex, inputs[{name,dtype}]
data_schema: universe, columns, splits{train,validate,holdout}
module_apis: [{module, functions[{name,returns,description}]}]
test_plan: unit_tests[{function,cases}], property_tests[{invariant}]
success_criteria: metrics[{name,threshold,direction}]
