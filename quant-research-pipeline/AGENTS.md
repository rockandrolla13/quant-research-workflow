# AGENTS.md — Codex Operating Rules

## You are Codex (Implementer)
Write production code ONLY under `strategies/<id>/repo/`.
Do NOT edit: spec/, synth/, extract/, tools/, tex/, or locked artifacts.

## First Reads (ALWAYS)
1. This file (AGENTS.md)
2. `codex_tasks/build-from-spec.md`
3. Execute task exactly as specified

## Python Environment
Use wrapper scripts (preferred):
```bash
./tools/run-stratpipe.sh python ...
./tools/run-stratpipe.sh pip ...
./tools/run-stratpipe.sh pytest ...
```

If venv missing, create it:
```bash
python3 -m venv .venv-stratpipe
./tools/run-stratpipe.sh pip install -U pip
./tools/run-stratpipe.sh pip install -r requirements-stratpipe.txt
```

Never use bare `python`, `pip`, `pytest`.

## Package Naming (STRICT)
- Package name = `strategy_id` from spec.yaml
- Path = `strategies/<strategy_id>/repo/src/<strategy_id>/`

## Import Policy (STRICT)
- NEVER use `sys.path.insert()` or `sys.path.append()`
- ALWAYS `pip install -e repo/` before tests
- Import via package name only

## Preconditions (hard gates)
- Spec locked: `git tag -l "spec-<id>-*"` returns result
- `spec/spec.yaml` exists
- If missing: STOP and report

## Spec Ambiguity Protocol
If spec unclear:
1. STOP immediately
2. Write `SPEC_CHANGE_REQUEST.md` with questions
3. Do NOT implement with assumptions

## Ownership
Write: `strategies/<id>/repo/**`
Read: spec.yaml, SPEC.md, formula.md

## Execution
Follow 10-step build in `codex_tasks/build-from-spec.md`.
Checkpoint commits after each step.
