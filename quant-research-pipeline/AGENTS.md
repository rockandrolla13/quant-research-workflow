# AGENTS.md — Codex Operating Rules (Project Root)

## You are Codex (Implementer)
You ONLY write production code under `strategies/<id>/repo/`.
You do NOT edit:
- `strategies/<id>/spec/`, `strategies/<id>/synth/`, `strategies/<id>/extract/`, `tools/`, `strategies/<id>/tex/`
- any locked spec artifacts

## Mandatory First Reads (ALWAYS do this before any work)
1) Read this file (AGENTS.md).
2) Then read: `codex_tasks/build-from-spec.md`.
3) Then execute the task exactly as specified.

## Environment (non-negotiable)
Use ONLY:
- `.venv-stratpipe/bin/python`
- `.venv-stratpipe/bin/pip`
- `.venv-stratpipe/bin/pytest`

Never use bare `python`, `pip`, or global interpreters.

If `.venv-stratpipe` does not exist:
- `python3 -m venv .venv-stratpipe`
- `.venv-stratpipe/bin/pip install -U pip`
- `.venv-stratpipe/bin/pip install -r requirements-stratpipe.txt`

## Preconditions (hard gates)
Before coding:
- Confirm spec is locked: git tag exists `spec-<strategy_id>-v*`
- Confirm `strategies/<id>/spec/spec.yaml` exists and is the only source of truth
- If lock/tag missing: STOP and report

## Repo ownership
You write ONLY in:
- `strategies/<id>/repo/**`

You may READ:
- `strategies/<id>/spec/spec.yaml`, `strategies/<id>/spec/SPEC.md`, `strategies/<id>/synth/formula.md`

## Execution policy
Follow the 10-step build order in `codex_tasks/build-from-spec.md` exactly.
Checkpoint commits after each major step.
