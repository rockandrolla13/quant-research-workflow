# Codex (Implementer) — fx_cookbook Debrief

## 0) Metadata

```yaml
agent: codex
session: fx_cookbook build (v1.0 → v1.2 → v1.3 EWMA patch → results phase)
date: 2026-02-23
strategy_id: fx_cookbook
scope_owned: strategies/fx_cookbook/repo/**
venv_used: /home/ak-old-one/projects/pdf-algo-extractor/quant-research-pipeline/.venv-stratpipe/bin/python
```

## 1) What I worked on

- Built the `fx_cookbook` implementation repo from locked spec.yaml, following the 10-step build order in `codex_tasks/build-from-spec.md`
- **v1.0 build** (spec v1.0): Scaffolded repo, implemented signals + portfolio modules, tests, notebooks — but used wrong package name (`momentum_strategy_v1`) and wrong repo path (`quant-research-pipeline/repo/` instead of `strategies/fx_cookbook/repo/`)
- **v1.2 rebuild** (spec v1.2): Complete rewrite at correct path with correct package name `fx_cookbook`. All 6 modules implemented: signals, portfolio, risk, backtest, validation, spec_models. Full test suite: unit tests + Hypothesis property tests.
- **v1.3 EWMA patch**: Implemented `estimate_covariance` with 3-day non-overlapping returns averaged over 3 starting offsets. Filed `SPEC_CHANGE_REQUEST_v1.3.md` documenting 3 implementation assumptions.
- **Results phase**: Added `results.py` orchestrator, `data.py` with provider abstraction, extended `spec_models.py` with `DataConfig`/`CalendarConfig`, 3 new notebooks, docs (CHANGELOG, DATA_CONTRACT, METHODOLOGY, REPRODUCIBILITY), and Makefile targets.

## 2) Files I changed (exact paths)

**v1.0 build (discarded):**
- `quant-research-pipeline/repo/src/momentum_strategy_v1/` — wrong package name, wrong path
- Commits: `988032c`..`00d1582` (Steps 2-6, 9-10)

**v1.2 rebuild (23 files, 1148 insertions):**
- `strategies/fx_cookbook/repo/src/fx_cookbook/__init__.py`
- `strategies/fx_cookbook/repo/src/fx_cookbook/signals.py`
- `strategies/fx_cookbook/repo/src/fx_cookbook/portfolio.py`
- `strategies/fx_cookbook/repo/src/fx_cookbook/risk.py`
- `strategies/fx_cookbook/repo/src/fx_cookbook/backtest.py`
- `strategies/fx_cookbook/repo/src/fx_cookbook/validation.py`
- `strategies/fx_cookbook/repo/src/fx_cookbook/spec_models.py`
- `strategies/fx_cookbook/repo/config.yaml`
- `strategies/fx_cookbook/repo/pyproject.toml`
- `strategies/fx_cookbook/repo/Makefile`
- `strategies/fx_cookbook/repo/README.md`
- `strategies/fx_cookbook/repo/.github/workflows/test.yml`
- `strategies/fx_cookbook/repo/tests/` (all test files + utils.py)
- `strategies/fx_cookbook/repo/notebooks/00_research.ipynb`
- `strategies/fx_cookbook/repo/notebooks/01_backtest.ipynb`
- Commit: `2be7e87`

**v1.3 EWMA patch (9 files, 191 insertions):**
- `strategies/fx_cookbook/repo/src/fx_cookbook/risk.py` — rewrote `estimate_covariance` with 3-offset averaging
- `strategies/fx_cookbook/repo/tests/test_risk.py` — added 4 EWMA-specific tests
- `strategies/fx_cookbook/repo/SPEC_CHANGE_REQUEST_v1.3.md` — documented assumptions
- `strategies/fx_cookbook/repo/pyproject.toml` — version bump to 1.3.0
- `strategies/fx_cookbook/repo/src/strategy_fx_cookbook.egg-info/` — build artifact (should not have been committed)
- Commit: `c6ffcdd`

**Results phase (19 files, 673 insertions):**
- `strategies/fx_cookbook/repo/src/fx_cookbook/data.py` — data loading + schema validation
- `strategies/fx_cookbook/repo/src/fx_cookbook/results.py` — end-to-end orchestrator
- `strategies/fx_cookbook/repo/src/fx_cookbook/spec_models.py` — added DataConfig, CalendarConfig, ValidationConfig
- `strategies/fx_cookbook/repo/config.yaml` — added data + validation sections
- `strategies/fx_cookbook/repo/tests/test_data.py`
- `strategies/fx_cookbook/repo/tests/fixtures/fx_sample.csv`
- `strategies/fx_cookbook/repo/notebooks/00_data_sanity.ipynb`
- `strategies/fx_cookbook/repo/notebooks/01_signal_diagnostics.ipynb`
- `strategies/fx_cookbook/repo/notebooks/02_backtest_results.ipynb`
- `strategies/fx_cookbook/repo/docs/` (CHANGELOG, DATA_CONTRACT, METHODOLOGY, REPRODUCIBILITY)
- `strategies/fx_cookbook/repo/Makefile` — added data-sanity, backtest, notebooks, results targets
- Commit: `d104688`

**Tags:**
- `fx_cookbook-impl-v1.3`

## 3) Commands I ran (important ones)

```bash
# Install package in dev mode
/home/ak-old-one/projects/pdf-algo-extractor/quant-research-pipeline/.venv-stratpipe/bin/pip install -e "strategies/fx_cookbook/repo[dev]"

# Run tests
/home/ak-old-one/projects/pdf-algo-extractor/quant-research-pipeline/.venv-stratpipe/bin/python -m pytest -q strategies/fx_cookbook/repo/tests

# Verify config loads
/home/ak-old-one/projects/pdf-algo-extractor/quant-research-pipeline/.venv-stratpipe/bin/python -c "from fx_cookbook.spec_models import load_config; load_config('strategies/fx_cookbook/repo/config.yaml')"

# Verify gate: spec lock tag exists
git tag --list | grep -F "spec-fx_cookbook-v1"
```

## 4) Issues encountered

### 4.1 — v1.0 repo at wrong path with wrong package name
- **Symptom:** First build created `quant-research-pipeline/repo/src/momentum_strategy_v1/` instead of `strategies/fx_cookbook/repo/src/fx_cookbook/`
- **Root cause:** The v1.0 build instructions and spec didn't specify the repo path convention clearly. Package name `momentum_strategy_v1` was a carryover from an earlier design that only implemented momentum.
- **Where introduced:** `codex_tasks/build-from-spec.md` v1.0 + my interpretation of directory structure
- **Fix:** Complete rebuild at correct path with correct package name in v1.2 (`2be7e87`)
- **Prevention:** `codex_tasks/build-from-spec.md` must include exact path: `strategies/<strategy_id>/repo/src/<strategy_id>/`. A pre-build validation step should check `strategy_id` matches directory name and package name.

### 4.2 — EWMA covariance spec was ambiguous
- **Symptom:** `estimate_covariance` spec said "3-day non-overlapping returns, averaged over 3 starting offsets" but left 3 details undefined: (a) how `decay` maps to EWMA alpha, (b) whether 3-day returns use sum or compounding, (c) what "offsets 0, 1, 2" means precisely.
- **Root cause:** spec.yaml described the algorithm in prose, not pseudocode. The description was sufficient for a human quant but not for deterministic implementation.
- **Where introduced:** `spec/spec.yaml` v1.2 — `estimate_covariance` function description
- **Fix:** Implemented with reasonable assumptions (`alpha = 1 - exp(-1/decay)`, sum of daily returns, offsets = starting indices 0/1/2 for 3-day blocks). Filed `SPEC_CHANGE_REQUEST_v1.3.md` documenting all 3 assumptions.
- **Prevention:** Any function involving iterative/windowed computation must have a `pseudocode:` field in spec.yaml. The build task should STOP and file a change request if a function with windowing/aggregation lacks pseudocode.

### 4.3 — Build artifacts committed to repo
- **Symptom:** `strategy_fx_cookbook.egg-info/` directory (6 files) committed in `c6ffcdd`
- **Root cause:** `pip install -e .` generates egg-info, and `.gitignore` didn't exclude it
- **Where introduced:** v1.3 EWMA patch session — ran `pip install -e .` then `git add .`
- **Fix:** Removed in `6a2c415`
- **Prevention:** Add `*.egg-info/` to `strategies/fx_cookbook/repo/.gitignore` (done in `39256c8`). The build task should specify: "never use `git add .` — always add specific files."

### 4.4 — `sys.path.insert` hack in test files
- **Symptom:** Every test file has `sys.path.insert(0, "strategies/fx_cookbook/repo/src")` at the top
- **Root cause:** Tests were run from the project root but the package wasn't always installed in the venv. The `sys.path` hack was needed to make imports work without `pip install -e`.
- **Where introduced:** v1.2 rebuild — test files
- **Fix:** Not yet fixed. Should be resolved by ensuring `pip install -e .` is always run before tests, and removing the sys.path hacks.
- **Prevention:** Build task Step 9 should mandate: "Before running tests, ensure package is installed: `pip install -e .`. Tests must NOT contain sys.path manipulation."

### 4.5 — v1.0 build skipped Steps 7 (backtest) and 8 (validation)
- **Symptom:** Git log shows commits for Steps 2, 3, 4, 5, 6, 9, 10 — no commits for Steps 7 or 8
- **Root cause:** spec v1.0 did not define `backtest` or `validation` modules (those were added in v1.1). Codex correctly skipped what wasn't in the spec, but the build order required them.
- **Where introduced:** Mismatch between spec v1.0 (missing modules) and build task (required all 10 steps)
- **Fix:** v1.2 rebuild included all modules
- **Prevention:** `build-from-spec.md` should generate the step list dynamically from `module_apis` in spec.yaml, not use a hardcoded 10-step sequence.

### 4.6 — `compute_momentum_signal` reads config internally
- **Symptom:** `signals.py:compute_momentum_signal` calls `load_config()` internally to get `dispersion_floor_percentile`, even though the function signature already accepts parameters. This couples the function to config.yaml at the file system level.
- **Root cause:** `dispersion_floor_percentile` was not in the function signature in spec.yaml, but was needed by the implementation. Rather than violating the spec signature, the function reached for config directly.
- **Where introduced:** spec.yaml — `compute_momentum_signal` signature omits `dispersion_floor_percentile`
- **Fix:** Not yet fixed. The parameter should be added to the spec function signature.
- **Prevention:** `validate_spec.py` should check that every parameter referenced in a function's description is either in its `args` list or derivable from another function's return.

### 4.7 — Bare `python` / wrong venv in v1.0 session
- **Symptom:** Initial build attempts used system Python or `.venv-extract` instead of `.venv-stratpipe`
- **Root cause:** AGENTS.md and `codex_tasks/build-from-spec.md` originally used relative paths (`.venv-stratpipe/bin/python`) that were ambiguous depending on CWD
- **Where introduced:** AGENTS.md before `d945e41` fix
- **Fix:** Claude updated all paths to absolute in `d945e41` and `39256c8`
- **Prevention:** Use wrapper scripts (`tools/run-stratpipe.sh`) that activate the correct venv. Never expose raw venv paths in agent instructions.

## 5) Where I caused problems / confusion

1. **Named the v1.0 package `momentum_strategy_v1`**: Invented a name instead of using `strategy_id` from spec.yaml. This meant the entire v1.0 build was thrown away. Should have derived the package name from `strategy_id` mechanically.

2. **Committed build artifacts**: Used `git add .` instead of adding specific files. The egg-info directory slipped in and required a cleanup commit. Should always use explicit file lists.

3. **Added `sys.path.insert` hacks instead of fixing the import setup**: The correct fix was ensuring `pip install -e .` was run before tests. Instead I added path manipulation to every test file, creating tech debt.

4. **Reached into config from inside `compute_momentum_signal`**: When the spec signature didn't include `dispersion_floor_percentile`, I should have filed a change request rather than silently coupling the function to the filesystem.

5. **Did not validate test coverage against spec test_plan**: Some spec test cases (e.g., `compute_pnl` with `cost_bps` multiplied by turnover and spread) are tested loosely (asserting `net < gross`) rather than checking exact computed values. The spec says "net_pnl < gross_pnl by cost_bps * turnover * spread amount" — this should be an exact assertion.

## 6) What slowed us down (top 3)

1. **Full v1.0 → v1.2 rebuild (wasted ~50% of build effort)**: The v1.0 build was entirely discarded because: (a) wrong path, (b) wrong package name, (c) spec bumped to v1.2 with 2 new modules not in v1.0. Had the spec been locked after all review cycles, and had the package name been derived from `strategy_id`, the v1.0 build would have been incrementally patchable instead of thrown away.

2. **EWMA covariance ambiguity (3 assumptions needed)**: This single function required more implementation guesswork than all other functions combined. The prose description was correct but insufficient for deterministic coding. The change request + review loop added a full iteration cycle.

3. **Venv confusion**: Silent import failures when using wrong Python. Debugging these was slow because the errors (ModuleNotFoundError deep in test execution) didn't clearly indicate "wrong venv" as the root cause. The fix was simple but discovering the problem was not.

## 7) Refactor proposals (highest ROI)

### 7.1 — Derive package name and repo path from spec.yaml
- **Change:** Build task generates package name as `strategy_id` (with hyphens→underscores) and repo path as `strategies/<strategy_id>/repo/`. No manual naming.
- **Payoff:** Eliminates the v1.0 wrong-name/wrong-path class of errors entirely.
- **Owner:** codex_tasks/build-from-spec.md + codex_skills/strategy_repo_builder/SKILL.md
- **Risk:** None. Purely mechanical derivation.

### 7.2 — Dynamic build steps from spec.yaml modules
- **Change:** Instead of hardcoded "10-step build order," generate steps from `module_apis` in spec.yaml. Step template: for each module M, (a) implement `src/<pkg>/M.py`, (b) implement `tests/test_M.py`, (c) run tests for M.
- **Payoff:** Eliminates skipped-step confusion when spec doesn't include all modules. Build order adapts to spec content.
- **Owner:** codex_tasks/build-from-spec.md
- **Risk:** Loses explicit ordering control. Mitigate: allow optional `build_order` field in spec.yaml for dependency ordering between modules.

### 7.3 — Mandatory `pip install -e .` before tests + ban `sys.path` hacks
- **Change:** Build task adds hard gate: `pip install -e .` before any `pytest` run. Add pre-commit hook or ruff rule that rejects `sys.path.insert` in test files.
- **Payoff:** Clean imports, no path hacks, tests match production import behavior.
- **Owner:** codex_tasks/build-from-spec.md + repo `.pre-commit-config.yaml`
- **Risk:** Negligible.

### 7.4 — Explicit `.gitignore` template for strategy repos
- **Change:** Build task Step 2 (scaffold) generates `.gitignore` with: `*.egg-info/`, `__pycache__/`, `.hypothesis/`, `.pytest_cache/`, `*.pyc`, `outputs/` (except `.gitkeep`).
- **Payoff:** Prevents build artifacts from ever being committed.
- **Owner:** codex_skills/strategy_repo_builder/SKILL.md
- **Risk:** None.

### 7.5 — Test assertion strictness: exact vs. directional
- **Change:** For each spec test case, classify the expected outcome as "exact" (includes a numeric value) or "directional" (says "> 0" or "< gross"). Exact expectations must produce exact assertions (with tolerance). Directional expectations can use inequality assertions.
- **Payoff:** Catches implementation bugs that directional assertions miss. The `compute_pnl` cost deduction test currently passes even if the cost formula is wrong, as long as net < gross.
- **Owner:** codex_tasks/build-from-spec.md (Step 9 instructions)
- **Risk:** Exact assertions are more brittle. Mitigate: use `rel_tol=1e-3` for floating point comparisons.

### 7.6 — Spec signature completeness check
- **Change:** If a function's description references a parameter name that is in `signal.parameters` but NOT in the function's `args` list, `validate_spec.py` should emit a WARNING. This would have caught `dispersion_floor_percentile` missing from `compute_momentum_signal`.
- **Payoff:** Prevents functions from silently coupling to config when they should receive parameters explicitly.
- **Owner:** tools/validate_spec.py
- **Risk:** May produce false positives for parameters that are legitimately read from config at a higher level and passed down. Mitigate: allow `config_provided: true` annotation on parameters.

### 7.7 — Structured change request with STOP gate
- **Change:** When Codex encounters a spec ambiguity: (a) write `SPEC_CHANGE_REQUEST.yaml` (not freeform .md), (b) STOP and report, (c) do not implement with assumptions. Claude reviews the request, updates spec, and re-triggers the build.
- **Payoff:** Eliminates the "implement with assumptions then discover they were wrong" failure mode. Change requests become machine-readable.
- **Owner:** codex_tasks/build-from-spec.md + AGENTS.md
- **Risk:** May over-trigger STOPs for minor ambiguities. Mitigate: define an "ambiguity threshold" — file request for algorithmic ambiguity, but proceed with reasonable defaults for cosmetic/formatting ambiguity.

## 8) Skill + instruction updates needed

### AGENTS.md
- Add: "Package name MUST equal `strategy_id` from spec.yaml (hyphens replaced with underscores)"
- Add: "Repo path MUST be `strategies/<strategy_id>/repo/`"
- Add: "NEVER use `git add .` or `git add -A`. Always add specific files by name."
- Add: "If a spec function's description references a parameter not in its args, file a SPEC_CHANGE_REQUEST and STOP."
- Add: "NEVER include `sys.path.insert` in test files. Ensure `pip install -e .` is run before tests."

### codex_tasks/build-from-spec.md
- Step 2: Add "Generate `.gitignore` from template (egg-info, pycache, hypothesis, pytest_cache)"
- Step 2: Add "Package name = `strategy_id` with hyphens→underscores. Repo at `strategies/<strategy_id>/repo/`."
- Step 9: Add "Run `pip install -e .` BEFORE running pytest. Tests must not contain `sys.path` hacks."
- Step 9: Add "For spec test cases with exact numeric expectations, write exact assertions with `rel_tol`. For directional expectations, inequality assertions are acceptable."
- New Step 11: Add "If any spec ambiguity was encountered during build, write `SPEC_CHANGE_REQUEST.yaml` and STOP."
- Consider: Generate steps dynamically from `module_apis` instead of hardcoded 10-step list.

### codex_skills/strategy_repo_builder/SKILL.md
- Add `.gitignore` template to "Repo Layout" section
- Add "Package naming convention" section
- Add "Test import policy: `pip install -e .` not sys.path"
- Add "Change request protocol" section

### codex_skills/notebook_builder/ (if used)
- Add: "Notebooks must not define functions — import from `src/<pkg>/`"
- Add: "Notebooks must declare expected data path relative to repo root"

### CLAUDE.md
- Add to spec writing rules: "Every parameter referenced in a function's description MUST appear in its `args` list, OR be documented as config-provided with `config_provided: true`"

### tools/validate_spec.py
- Add: check that function description parameters match `args` list
- Add: check that `strategy_id` is a valid Python package name (no hyphens, etc.)

## 9) Next actions I recommend (ordered)

1. **Fix `sys.path.insert` hacks in all test files** — remove the hacks, ensure `pip install -e .` in Makefile test target (already done) is the canonical way to run tests. Low effort, immediate cleanup.
2. **Add `.gitignore` to `strategies/fx_cookbook/repo/`** — prevent future build artifact commits. 2 minutes.
3. **Add `dispersion_floor_percentile` to `compute_momentum_signal` args in spec.yaml** — remove the internal `load_config()` call from `signals.py`. Requires spec bump (v1.4) but is backward-compatible.
4. **Strengthen test assertions for `compute_pnl`** — add exact cost calculation check, not just `net < gross`.
5. **Update `codex_tasks/build-from-spec.md`** with lessons learned (package naming, `.gitignore` template, pip install before tests, change request protocol).
6. **Implement dynamic build step generation from spec.yaml** — replaces hardcoded 10-step list. Medium effort but prevents step-skipping confusion.
7. **Create `SPEC_CHANGE_REQUEST.yaml` schema** — structured format for spec ambiguity reporting. Coordinate with Claude's matching proposal.
