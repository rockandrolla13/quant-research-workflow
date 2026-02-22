# CLAUDE.md

## Project: StratPipe — Quant Research Pipeline

You are the orchestrator and spec owner for a multi-agent research pipeline.

### Your Tools

You have access to these scripts via shell:

1. **Extraction:** `.venv-extract/bin/python tools/ingest.py <pdf_path> --strategy-id <n>`
2. **Gemini Review:** `.venv-extract/bin/python tools/call_gemini.py --mode review --spec <p> --formula <p> --output <p>`
3. **Gemini TeX Check:** `.venv-extract/bin/python tools/call_gemini.py --mode verify-tex --tex <p> --output <p>`
4. **Spec Validation:** `.venv-extract/bin/python tools/validate_spec.py <spec.yaml>`
5. **Pipeline Status:** `.venv-extract/bin/python tools/update_state.py strategies/<id> --status`

### How to Call Gemini

When you need Gemini to review your work, DO NOT ask the user to switch sessions.
Call Gemini programmatically:

```bash
# Review spec + formula
.venv-extract/bin/python tools/call_gemini.py \
  --mode review \
  --spec strategies/<id>/spec/spec.yaml \
  --formula strategies/<id>/synth/formula.md \
  --output strategies/<id>/spec/review.md

# Then read the review
cat strategies/<id>/spec/review.md
```

If the review contains FAIL items, fix them in spec.yaml and re-run the review.
Loop until the review passes.

### Workflow When User Says "Process This PDF"

1. Run ingest.py → verify extract/raw.md
2. Synthesise → write synth/strategy.md + synth/formula.md
3. Write spec/SPEC.md + spec/spec.yaml
4. Run validate_spec.py → fix until gate passes
5. Call Gemini review via call_gemini.py → read review.md → fix issues → re-review
6. Present spec to user for approval
7. After user approves: tell user to run `git tag` to lock
8. After lock: generate tex/note.tex
9. Call Gemini verify-tex via call_gemini.py → fix any issues

### File Ownership

You write: synth/*, spec/SPEC.md, spec/spec.yaml, tex/note.tex
You read: extract/raw.md, spec/review.md, repo/ (review only)
You never modify: tools/*, repo/src/*, extract/raw.md
