# Code Review Report (Post-Refactor)

**Files reviewed:** `backtest.py`, `data.py`, `signals.py`, `portfolio.py`, `risk.py`, `results.py`, `validation.py`, `spec_models.py`, `__init__.py`
**Date:** 2026-03-08
**Overall health:** 🟢 Good

## Executive Summary

The codebase is clean, well-decomposed, and correctly handles the critical numerical edge cases (NaN propagation, div-by-zero, empty inputs). The major bugs from the v1 review (input mutation in `_validate_schema`, div-by-zero in carry signal, config coupling in `signals.py`) have all been fixed. Remaining findings are 🟡 minor style/DRY items — no correctness risks. The dominant pattern is hardcoded magic numbers (`252` in 4 locations) that should be parameterised but don't pose a divergence risk at current scale.

## Findings

### CR-DRY-001: Annualisation factor 252 duplicated across 2 modules

- **Severity:** 🟡 Minor
- **Pillar:** DRY
- **Location:** `backtest.py:78,81,92`, `validation.py:17`

BEFORE:
```python
# backtest.py
sharpe = (np.sqrt(252) * mean / std) if std != 0 else 0.0
years = len(r) / 252.0
sortino = (np.sqrt(252) * mean / downside_std) if downside_std != 0 else 0.0

# validation.py
sharpe = (np.sqrt(252) * mean / std) if std != 0 else 0.0
```

AFTER:
```python
def compute_metrics(bt, bdays_per_year: int = 252) -> dict:
    sharpe = (np.sqrt(bdays_per_year) * mean / std)
```

WHY:
Same business knowledge (trading calendar) expressed as a literal in 4 places. The value exists in `config.yaml` as `bdays_per_year: 252` but isn't threaded through.

---

### CR-DRY-002: Sharpe ratio formula duplicated between backtest.py and validation.py

- **Severity:** 🟡 Minor
- **Pillar:** DRY
- **Location:** `backtest.py:78`, `validation.py:17`

BEFORE:
```python
# backtest.py:78
sharpe = (np.sqrt(252) * mean / std) if std != 0 else 0.0

# validation.py:17
sharpe = (np.sqrt(252) * mean / std) if std != 0 else 0.0
```

AFTER:
```python
# Extract to a shared location or accept duplication
# as these serve different contexts (metrics vs hypothesis test)
```

WHY:
Identical formula, identical guard clause. However, these serve different purposes (metrics reporting vs hypothesis testing). Applying Rule of Three: only 2 instances — extracting now risks premature coupling. Flag but don't act.

---

### CR-STYLE-001: data.py dtype dispatch uses string matching instead of a lookup

- **Severity:** 🔵 Suggestion
- **Pillar:** Style
- **Location:** `data.py:70-84`

BEFORE:
```python
if dtype == "datetime":
    ...
elif dtype == "str":
    ...
elif dtype == "float64":
    ...
elif dtype == "int64":
    ...
```

AFTER:
```python
_DTYPE_VALIDATORS = {
    "datetime": _validate_datetime,
    "str": _validate_string,
    "float64": _validate_float,
    "int64": _validate_int,
}
```

WHY:
If-elif chain over string values is a classic Open/Closed violation. A dict dispatch would make adding new types a one-line change. However, the schema is locked and has exactly 4 types — this is a polish item, not a correctness issue.

---

### CR-STYLE-002: test fixture factory uses string dispatch without type safety

- **Severity:** 🔵 Suggestion
- **Pillar:** Style
- **Location:** `tests/utils.py:10-56`

BEFORE:
```python
def make_returns(kind: str) -> pd.DataFrame:
    if kind == "all_positive_returns_252d":
        ...
    if kind == "alternating_sign_returns":
        ...
```

AFTER:
```python
# Use an enum or Literal type for kind parameter
def make_returns(kind: Literal["all_positive_returns_252d", ...]) -> pd.DataFrame:
```

WHY:
Typos in test fixture names fail silently at the `raise ValueError` at the end — the test would fail with a confusing error. `Literal` types would catch this at type-check time. Low impact since tests are run frequently.

---

### CR-PERF-001: _compute_sign_stack loops over lookbacks instead of vectorising

- **Severity:** 🔵 Suggestion
- **Pillar:** Performance
- **Location:** `signals.py:7-14`

BEFORE:
```python
for h in lookbacks:
    r_h = returns.rolling(window=h, min_periods=h).mean()
    signs.append(np.sign(r_h).values)
return np.stack(signs, axis=0)
```

AFTER:
```python
# Pandas rolling doesn't support vectorised variable-width windows
# This loop is the correct approach — numpy can't vectorise this
```

WHY:
The loop is necessary because pandas `rolling()` doesn't support variable window sizes in a single call. Flagging to document that this was considered and rejected.

## Summary Table

| Finding ID | Severity | Pillar | Location | Finding |
|---|---|---|---|---|
| CR-DRY-001 | 🟡 Minor | DRY | backtest.py:78,81,92; validation.py:17 | 252 annualisation factor hardcoded in 4 locations |
| CR-DRY-002 | 🟡 Minor | DRY | backtest.py:78; validation.py:17 | Sharpe formula duplicated (Rule of Three: only 2 instances) |
| CR-STYLE-001 | 🔵 Suggestion | Style | data.py:70-84 | String-matching dtype dispatch; dict lookup would be cleaner |
| CR-STYLE-002 | 🔵 Suggestion | Style | tests/utils.py:10-56 | String-dispatched fixture factory; Literal types would catch typos |
| CR-PERF-001 | 🔵 Suggestion | Performance | signals.py:7-14 | Lookback loop is necessary (pandas limitation); no action needed |

## Positive Highlights

1. **All v1 critical/major bugs fixed.** Input mutation (CR-BUG-001), div-by-zero in carry (CR-BUG-003), config coupling in signals (CR-BUG-004/005), sys.path hacks (CR-STYLE-001 v1) — all resolved.

2. **Clean decomposition in signals.py.** The 4-helper structure (`_compute_sign_stack` → `_compute_raw_signals` → `_apply_hysteresis` → `_normalize_by_dispersion`) reads like pseudocode. Each helper is independently testable.

3. **Backtest shared primitives.** `_lagged_weights`, `_gross_return`, `_turnover` eliminate the duplication between `run_backtest` and `compute_pnl` while keeping the public API unchanged.

---

## Handoff

| Severity | Pillar | Location | Finding | Finding ID |
|---|---|---|---|---|
| 🟡 Minor | DRY | backtest.py:78,81,92; validation.py:17 | 252 annualisation factor hardcoded in 4 locations across 2 modules | CR-DRY-001 |
| 🟡 Minor | DRY | backtest.py:78; validation.py:17 | Sharpe formula duplicated between metrics and hypothesis test | CR-DRY-002 |
| 🔵 Suggestion | Style | data.py:70-84 | String-matching dtype dispatch could use dict lookup | CR-STYLE-001 |
| 🔵 Suggestion | Style | tests/utils.py:10-56 | String-dispatched fixture factory lacks Literal type safety | CR-STYLE-002 |
| 🔵 Suggestion | Performance | signals.py:7-14 | Lookback loop is necessary; no vectorisation possible | CR-PERF-001 |
