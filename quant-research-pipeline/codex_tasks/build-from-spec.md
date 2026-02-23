# codex_tasks/build-from-spec.md — Build From Locked Spec

## Task
The spec is locked (tag: `spec-fx_cookbook-v1`).
Build the repository under `repo/` from `spec/spec.yaml`.
Use `/home/ak-old-one/projects/pdf-algo-extractor/quant-research-pipeline/.venv-stratpipe/bin/python` for EVERYTHING.

## Absolute Rules
- `spec/spec.yaml` is the only contract: signatures, parameters, tests.
- Do NOT modify spec/synth/tools/tex.
- Write ONLY inside `repo/`.
- Notebooks must be thin import layers (no core logic).
- If tests fail, fix code not tests.

## 10-Step Build Order (must follow exactly)

### 1) Verify gates
- `git tag --list | grep -F "spec-fx_cookbook-v1"` must succeed
- `test -f spec/spec.yaml` must succeed
- If either fails: STOP and report.

### 2) Create repo skeleton
Create:
- `repo/src/fx_cookbook/`
- `repo/tests/`
- `repo/notebooks/`
- `repo/pyproject.toml`, `repo/README.md`, `repo/Makefile`
- `repo/.github/workflows/test.yml`

### 3) Step 1.5 — Generate `spec_models.py`
Create `repo/src/fx_cookbook/spec_models.py`:
- small Pydantic models for runtime config validation
- `load_config("config.yaml")` returns a validated object
- `extra="forbid"` everywhere

### 4) Generate `config.yaml`
Write `repo/config.yaml` from spec parameters and splits.
Immediately validate:
- `/home/ak-old-one/projects/pdf-algo-extractor/quant-research-pipeline/.venv-stratpipe/bin/python -c "from src.fx_cookbook.spec_models import load_config; load_config('repo/config.yaml')"`

### 5) Implement `data.py`
Implement data loading + schema validation (from spec).
Use `load_config()` and `DataConfig`.

### 6) Implement `signals.py`
Implement formula(s) from spec.
No hardcoded parameters; read from config.

### 7) Implement `backtest.py`
Implement minimal backtest harness per spec.

### 8) Implement `validation.py`
Implement hypothesis tests + success criteria per spec.

### 9) Implement tests
Generate tests strictly from spec test_plan.
Add `test_config_loads.py` (config validation test).

Run:
- `/home/ak-old-one/projects/pdf-algo-extractor/quant-research-pipeline/.venv-stratpipe/bin/python -m pytest -q repo/tests`

### 10) Generate thin notebooks (LAST)
Create:
- `repo/notebooks/00_research.ipynb`
- `repo/notebooks/01_backtest.ipynb`
They must import from `repo/src/fx_cookbook/`.

## Commands you must use (examples)
- `/home/ak-old-one/projects/pdf-algo-extractor/quant-research-pipeline/.venv-stratpipe/bin/python -m pytest -q`
- `/home/ak-old-one/projects/pdf-algo-extractor/quant-research-pipeline/.venv-stratpipe/bin/pip install -e repo`
Never use bare `python` or global pip.
