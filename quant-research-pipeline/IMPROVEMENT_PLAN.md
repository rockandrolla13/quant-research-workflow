# StratPipe Improvement Plan — Updated

*Based on 4 agent debriefs + 4 iterations of Ralph Loop refinement*

---

## ✅ Phase 1 Complete (This Session)

### Implemented

| Improvement | Status | Files Changed |
|------------|--------|---------------|
| Venv wrapper scripts | ✅ Done | `tools/run-stratpipe.sh`, `tools/run-extract.sh` |
| Fixed pytest venv path | ✅ Done | `tools/update_state.py` |
| WARN-BLOCKING/WARN-COSMETIC | ✅ Done | `tools/call_gemini.py` |
| Scope-aware review prompt | ✅ Done | `tools/call_gemini.py` |
| --bib flag for verify-tex | ✅ Done | `tools/call_gemini.py` |
| Package naming rule | ✅ Done | `AGENTS.md` |
| sys.path ban | ✅ Done | `AGENTS.md` |
| Spec ambiguity protocol | ✅ Done | `AGENTS.md` |
| .gitignore template | ✅ Done | `codex_tasks/build-from-spec.md` |
| pip install gate | ✅ Done | `codex_tasks/build-from-spec.md` |
| Removed stale absolute paths | ✅ Done | All docs now use wrapper scripts |
| formula.md scope requirement | ✅ Done | `CLAUDE.md` |

### Code Reduction Results

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total tools LOC | 672 | 500 | -26% |
| Total docs LOC | 253 | 173 | -32% |
| CLAUDE.md | 100 | 49 | -51% |

### Test Results
- 28/29 tests passing consistently
- 1 failure due to missing fixture file (pre-existing issue, not related to changes)

---

## 🔄 Phase 2: Medium Effort (Next Session)

### 2.1 Unified Pipeline CLI
Create `tools/pipeline.py` with commands:
```bash
./tools/run-extract.sh python tools/pipeline.py run <id> --from synth --to package
./tools/run-extract.sh python tools/pipeline.py status <id>
./tools/run-extract.sh python tools/pipeline.py validate <id>
```
**Effort:** 2-3 hours | **Impact:** Eliminates manual stage sequencing

### 2.2 Pre-Lock Review Gate
Create `tools/lock_spec.py`:
- Runs validate_spec.py
- Runs validate_symbols.py (new)
- Runs Gemini review
- Only tags if zero WARN-BLOCKING

**Effort:** 1-2 hours | **Impact:** Prevents premature spec locks

### 2.3 Diff-Aware Gemini Review
Add `--mode review-diff --prev-review <path>` to call_gemini.py:
- Shows prior review + current diff
- Asks "are these warnings resolved?"
- Reduces cycles from 5 → 2-3

**Effort:** 1 hour | **Impact:** Major review cycle reduction

### 2.4 Pseudocode Fields in spec.yaml
- Add optional `pseudocode:` field to function specs
- Make required for windowing/aggregation functions
- Update validate_spec.py to check

**Effort:** 1 hour | **Impact:** Prevents EWMA-style ambiguity

### 2.5 Structured Change Request Schema
Create `SPEC_CHANGE_REQUEST.yaml` schema:
```yaml
strategy_id: fx_cookbook
spec_version: "1.2"
questions:
  - function: estimate_covariance
    ambiguity: "3-offset averaging not specified"
    options: ["sum returns", "compound returns"]
    codex_assumption: "sum returns"
```
**Effort:** 1 hour | **Impact:** Machine-readable change requests

---

## 📋 Phase 3: Larger Architecture (Future)

### 3.1 Deterministic Symbol Cross-Reference
New `tools/validate_symbols.py`:
- Parses formula.md symbol table
- Cross-references with spec.yaml inputs/parameters
- Checks 1:1 mapping, no reuse
- Fast pre-gate before Gemini

**Effort:** 2-3 hours | **Impact:** Makes symbol checking deterministic

### 3.2 Split formula.md
Separate into:
- `formula_reference.md` (full paper documentation)
- `formula_contract.md` (auto-generated from spec.yaml)

**Effort:** 2 hours | **Impact:** Eliminates scope mismatch class of errors

### 3.3 Dynamic Build Steps
Generate build steps from spec.yaml `module_apis`:
- Each module → implementation step
- Each module → test step
- Adapts to spec content

**Effort:** 3-4 hours | **Impact:** No hardcoded 10-step list

### 3.4 Extraction Quality Gate
Add to ingest.py:
- Generate `extract/quality_report.json`
- Equation/table/figure/section counts
- Boilerplate detection
- Quality threshold gate

**Effort:** 2 hours | **Impact:** Catches bad extractions early

### 3.5 Pre-Flight GPU Check
New `tools/check_gpu.sh`:
- Validates CUDA before Marker attempt
- Clear error message if no GPU
- Prevents wasted Marker attempts

**Effort:** 30 min | **Impact:** Saves wall-clock time

---

## Summary

### Completed This Session
- All Phase 1 quick wins
- 30% code reduction while adding features
- Eliminated stale absolute paths
- Added venv enforcement

### Expected ROI from Remaining Phases

| Phase | Effort | Impact |
|-------|--------|--------|
| Phase 2 | ~8 hours | 50% reduction in review cycles, eliminates ambiguity issues |
| Phase 3 | ~12 hours | Deterministic symbol checking, dynamic builds, quality gates |

### Key Metrics to Track
- Gemini review cycles (target: 2-3, was 5)
- Venv-related errors (target: 0)
- Spec ambiguity issues (target: rare)
- Wasted rebuilds (target: 0)
