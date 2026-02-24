# Build From Locked Spec

## Task
Build `repo/` from `spec/spec.yaml`. Spec must be locked (tagged).

## Rules
- `spec.yaml` is the only contract
- Write ONLY inside `repo/`
- Notebooks = thin import layers
- If tests fail, fix code not tests

## 10-Step Build Order

### 1) Verify gates
```bash
git tag -l "spec-<strategy_id>-*"  # must return tag
test -f spec/spec.yaml             # must exist
```
If either fails: STOP.

### 2) Create skeleton
```
repo/
  src/<strategy_id>/
  tests/
  notebooks/
  pyproject.toml, README.md, Makefile
  .github/workflows/test.yml
  .gitignore  # __pycache__/, *.egg-info/, .pytest_cache/, etc.
```

### 3) Generate `spec_models.py`
Pydantic models + `load_config()` with `extra="forbid"`.

### 4) Generate `config.yaml`
From spec parameters/splits. Validate immediately:
```bash
./tools/run-stratpipe.sh python -c "from src.<id>.spec_models import load_config; load_config('repo/config.yaml')"
```

### 5) Implement `data.py`
Data loading + schema validation.

### 6) Implement `signals.py`
Formulas from spec. No hardcoded params.

### 7) Implement `backtest.py`
Minimal backtest harness.

### 8) Implement `validation.py`
Hypothesis tests + success criteria.

### 9) Implement tests
From spec test_plan. Add `test_config_loads.py`.

**MANDATORY:**
```bash
./tools/run-stratpipe.sh pip install -e repo/
```

**FORBIDDEN:** `sys.path.insert()` or `sys.path.append()`

**Run:**
```bash
./tools/run-stratpipe.sh pytest repo/tests -q
```

### 10) Generate notebooks (LAST)
`00_research.ipynb`, `01_backtest.ipynb` — import from package only.
