# Claude (Synthesiser / Orchestrator) — fx_cookbook Debrief

## 0) Metadata

```yaml
agent: claude
session: fx_cookbook full pipeline (ingest → results)
date: 2026-02-23
strategy_id: fx_cookbook
scope_owned: strategies/fx_cookbook/synth/*, strategies/fx_cookbook/spec/*, strategies/fx_cookbook/tex/*, CLAUDE.md, AGENTS.md, codex_tasks/, codex_skills/
venv_used: .venv-extract/bin/python (for tools/ingest.py, tools/validate_spec.py, tools/call_gemini.py)
```

## 1) What I worked on

- Synthesised the Deutsche Bank FX Cookbook PDF into strategy.md (thesis, data, signals, risk, failure modes, backtest plan)
- Extracted and formalised 18 equations into formula.md with full symbol table
- Authored spec.yaml v1.0 → v1.1 → v1.2 (locked), defining module APIs, test plans, success criteria
- Authored SPEC.md as the human-readable companion
- Ran Gemini review loops (3 cycles to reach clean PASS)
- Wrote pre-registered LaTeX research note (note.tex + refs.bib), passed Gemini tex verification
- Authored AGENTS.md (Codex operating rules) and codex_tasks/build-from-spec.md (10-step build order)
- Authored codex_skills/strategy_repo_builder/SKILL.md
- Orchestrated Codex for repo build (v1.0 → v1.2 → v1.3 EWMA patch)
- Reviewed Codex implementation output, filed SPEC_CHANGE_REQUEST_v1.3.md feedback
- Updated pipeline state via tools/update_state.py
- Fixed CLAUDE.md and AGENTS.md to use absolute venv paths (resolved bare `python` confusion)

## 2) Files I changed (exact paths)

**Created:**
- `strategies/fx_cookbook/synth/strategy.md`
- `strategies/fx_cookbook/synth/formula.md`
- `strategies/fx_cookbook/spec/spec.yaml` (v1.0 → v1.1 → v1.2)
- `strategies/fx_cookbook/spec/SPEC.md`
- `strategies/fx_cookbook/tex/note.tex`
- `strategies/fx_cookbook/tex/refs.bib`
- `AGENTS.md`
- `codex_tasks/build-from-spec.md`
- `codex_skills/strategy_repo_builder/SKILL.md`
- `codex_skills/notebook_builder/` (not fully used)

**Modified:**
- `CLAUDE.md` (multiple iterations — added architecture, fixed paths to absolute)
- `strategies/fx_cookbook/spec/spec.yaml` (v1.0 → v1.1 → v1.2, three bumps)
- `strategies/fx_cookbook/synth/formula.md` (added Eq 0, scope disclaimer)
- `strategies/fx_cookbook/.pipeline_state.yaml`

**Key commits:**
- `1038c86` — initial synth + spec + first Gemini PASS
- `d2c0cb8` / `4476e23` — spec lock v1.0
- `6ac188f` — spec v1.1 (validation module + backtest tests)
- `4ca118d` — spec v1.2 (resolve all Gemini warnings)
- `d7bcc92` — spec v1.2 fixes (total_return, sigma_r, carry_smoothing)
- `3885a83` — formula.md scope disclaimer → Gemini clean PASS
- `bd8e601` — LaTeX research note
- `d945e41` — fix bare paths in CLAUDE.md/AGENTS.md
- `39256c8` — absolute venv paths, .gitignore, stale file cleanup

## 3) Commands I ran (important ones)

```bash
# PDF extraction
.venv-extract/bin/python tools/ingest.py strategies/fx_cookbook/input/source.pdf --strategy-id fx_cookbook

# Spec validation
.venv-extract/bin/python tools/validate_spec.py strategies/fx_cookbook/spec/spec.yaml

# Gemini review (ran 3x to reach PASS)
.venv-extract/bin/python tools/call_gemini.py --mode review \
  --spec strategies/fx_cookbook/spec/spec.yaml \
  --formula strategies/fx_cookbook/synth/formula.md \
  --output strategies/fx_cookbook/spec/review.md

# Gemini LaTeX verification
.venv-extract/bin/python tools/call_gemini.py --mode verify-tex \
  --tex strategies/fx_cookbook/tex/note.tex \
  --output strategies/fx_cookbook/tex/review_tex.md

# Pipeline state checks
.venv-extract/bin/python tools/update_state.py strategies/fx_cookbook --status

# Spec lock tags
git tag spec-fx_cookbook-v1 <hash>
git tag spec-fx_cookbook-v1.0 <hash>
git tag spec-fx_cookbook-v1.2 <hash>
```

## 4) Issues encountered

### 4.1 — Gemini flagging formula.md ↔ spec.yaml scope mismatch
- **Symptom:** Gemini WARN: formula.md documents 7 signals (Value, MSO, COFFEE, CFTC) but spec.yaml only implements Momentum + Carry
- **Root cause:** formula.md was written as a complete math reference for the paper; spec.yaml deliberately scoped to 2 signals
- **Introduced by:** Me — formula.md lacked explicit scope boundary
- **Fix:** Added scope disclaimer paragraph to top of formula.md (`3885a83`)
- **Prevention:** Template formula.md with mandatory "## Scope" section that maps each equation to implemented/deferred status

### 4.2 — spec v1.0 missing functions that Gemini required
- **Symptom:** Gemini WARN: `compute_asset_volatility` and `compute_usd_pc1` not in spec; `total_return` not listed as signal input
- **Root cause:** v1.0 spec treated risk module as monolithic; didn't expose individual utility functions as spec-level APIs
- **Introduced by:** Me — insufficient decomposition of the risk module in first spec draft
- **Fix:** Bumped to v1.1 and v1.2, added missing functions and inputs (`6ac188f`, `4ca118d`)
- **Prevention:** validate_spec.py should cross-check that every formula symbol maps to either a signal input, a parameter, or a function return

### 4.3 — Bare `python`/`pip`/`pytest` commands in AGENTS.md
- **Symptom:** Codex used system Python instead of .venv-stratpipe, causing import failures and wrong package versions
- **Root cause:** AGENTS.md and codex_tasks/ used relative paths like `.venv-stratpipe/bin/python`
- **Introduced by:** Me — wrote instructions with relative paths assuming CWD was always project root
- **Fix:** Rewrote all paths as absolute (`d945e41`, `39256c8`)
- **Prevention:** Linter/pre-commit hook that rejects bare `python`/`pip`/`pytest` in .md files under codex_tasks/ and AGENTS.md

### 4.4 — Spec version drift between spec.yaml and implementation
- **Symptom:** Codex built v1.2 repo, but EWMA covariance 3-offset averaging was underspecified → Codex had to guess implementation, filed SPEC_CHANGE_REQUEST_v1.3.md
- **Root cause:** spec.yaml v1.2 said "3-day non-overlapping returns, averaged over 3 starting offsets" but didn't define: (a) EWMA alpha formula, (b) sum vs compound 3-day returns, (c) offset definition
- **Introduced by:** Me — spec description was prose-level, not implementation-level
- **Fix:** Codex implemented with assumptions and filed change request; I created v1.3 tag after review
- **Prevention:** For any aggregation/windowing/averaging, spec.yaml must include a `pseudocode:` field with unambiguous steps

### 4.5 — Multiple spec lock tags for same version
- **Symptom:** Both `spec-fx_cookbook-v1` and `spec-fx_cookbook-v1.0` exist as tags
- **Root cause:** Manual tagging without consistent naming convention
- **Introduced by:** Me — tagged twice with slightly different names
- **Fix:** Both point to same commit; not harmful but confusing
- **Prevention:** Automated `lock-spec.sh` tool that enforces `spec-<id>-v<MAJOR>.<MINOR>` naming

## 5) Where I caused problems / confusion

1. **Locked spec too early (v1.0)**: Locked before Gemini review was fully clean. Had to bump to v1.1, then v1.2. The "lock" lost meaning because I kept editing after the lock tag. Should have completed all review cycles before any lock.

2. **Under-specified covariance estimation**: The single biggest source of rework. Codex couldn't implement `estimate_covariance` from the spec description alone and had to make 3 implementation assumptions. This should have been caught by me writing pseudocode in the spec.

3. **Formula.md served dual purpose (reference doc + spec contract)**: formula.md was both a complete paper summary and the formula contract for the spec. This caused Gemini to flag scope mismatches. Should have split into `formula_reference.md` (complete paper) and `formula_spec.md` (implemented subset only).

4. **Inconsistent agent routing**: Sometimes asked the user to "switch to Codex session" instead of providing machine-readable handoff instructions. The pipeline lacks an automated dispatch mechanism.

5. **No structured change request format**: When Codex needed spec clarification, it wrote free-form markdown (SPEC_CHANGE_REQUEST_v1.3.md). There was no schema for change requests, making it harder to process programmatically.

## 6) What slowed us down (top 3)

1. **Spec iteration loop (3 review cycles)**: Each cycle required: edit spec.yaml → run validate_spec.py → run Gemini review → read review.md → fix → repeat. The v1.0→v1.2 journey was 5 commits across 3 versions. A tighter feedback loop (validate + review in one command) would halve this.

2. **Codex venv/path confusion**: Codex attempting bare `python` or wrong venv wasted at least one full implementation cycle. The fix was trivial (absolute paths) but the debugging was not — failures were silent ImportErrors deep in test runs.

3. **Manual agent coordination**: Every handoff between Claude↔Codex↔Gemini required the user to context-switch or me to manually invoke `call_gemini.py`. There's no event-driven orchestration — it's all imperative "run this, then read that".

## 7) Refactor proposals (highest ROI)

### 7.1 — Unified `pipeline run` command
- **Change:** Single CLI: `python tools/pipeline.py run fx_cookbook --from synth --to package`
- **Payoff:** Eliminates manual stage sequencing. Each stage has pre/post gates. Gemini review is automatic.
- **Owner:** tools/
- **Risk:** Over-automation may hide intermediate state. Mitigate with `--dry-run` and verbose logging.

### 7.2 — Pseudocode field in spec.yaml for non-trivial functions
- **Change:** Add optional `pseudocode:` field to each function in `module_apis`. Required for any function involving windowing, aggregation, or iterative computation.
- **Payoff:** Eliminates ambiguity that caused EWMA 3-offset guessing. Codex gets unambiguous contract.
- **Owner:** spec schema (tools/validate_spec.py) + CLAUDE.md spec writing rules
- **Risk:** Adds spec authoring burden. Mitigate by only requiring it for flagged functions.

### 7.3 — Pre-lock review gate (automated)
- **Change:** `tools/lock_spec.py` that: (1) validates schema, (2) runs Gemini review, (3) only creates tag if PASS (no WARN/FAIL), (4) enforces `spec-<id>-v<MAJOR>.<MINOR>` naming
- **Payoff:** Prevents locking before review is clean. Eliminates duplicate/inconsistent tags.
- **Owner:** tools/
- **Risk:** Gemini review may have false positives that block legitimate locks. Add `--force` escape hatch with logged reason.

### 7.4 — Structured change request schema
- **Change:** `SPEC_CHANGE_REQUEST.yaml` schema with fields: `requested_by`, `spec_version`, `changes` (list of `{function, field, current_value, proposed_value, rationale}`)
- **Payoff:** Machine-readable requests. Claude can auto-diff and approve/reject. No more free-form markdown.
- **Owner:** tools/validate_spec.py (add `--validate-change-request` mode)
- **Risk:** Low. Schema is simple. Codex skill needs one update.

### 7.5 — Split formula.md into reference + contract
- **Change:** `synth/formula_reference.md` (complete paper) + `synth/formula_contract.md` (only equations referenced in spec.yaml, auto-generated)
- **Payoff:** Eliminates scope mismatch warnings. Gemini reviews only the contract doc.
- **Owner:** CLAUDE.md spec writing rules + call_gemini.py to use formula_contract.md
- **Risk:** Maintenance burden of two files. Mitigate: formula_contract.md is generated from spec.yaml equation references, not hand-maintained.

### 7.6 — Venv enforcement via wrapper scripts
- **Change:** Replace `AGENTS.md` venv instructions with wrapper scripts: `tools/run-stratpipe.sh <cmd>` and `tools/run-extract.sh <cmd>` that activate the correct venv.
- **Payoff:** Eliminates wrong-venv errors entirely. Codex never sees raw python paths.
- **Owner:** tools/
- **Risk:** Negligible. Wrapper is 3 lines of bash.

### 7.7 — Gemini review diff mode
- **Change:** `call_gemini.py --mode review-diff --prev-review review_v1.1.md` that tells Gemini to only review changes since last review
- **Payoff:** Faster review cycles. Currently Gemini re-reviews everything from scratch on each run.
- **Owner:** tools/call_gemini.py
- **Risk:** Gemini may miss regressions if only reviewing diffs. Mitigate: full review on version bumps, diff review on patches.

## 8) Skill + instruction updates needed

### AGENTS.md
- Add: "If spec functions have a `pseudocode:` field, follow it exactly"
- Add: "Use `tools/run-stratpipe.sh` wrapper instead of direct venv paths" (after 7.6)
- Add: structured change request format (after 7.4)

### codex_tasks/build-from-spec.md
- Step 1 (verify gates): add "validate spec with `tools/validate_spec.py`" as explicit sub-step
- Step 9 (tests): add "if a function has `pseudocode:` in spec, write a test case that verifies the algorithm step-by-step, not just input/output"
- Add Step 11: "if any spec ambiguity encountered, write `SPEC_CHANGE_REQUEST.yaml` and STOP"

### codex_skills/strategy_repo_builder/SKILL.md
- Add pseudocode consumption rule
- Add change request protocol
- Reference wrapper scripts for venv

### CLAUDE.md
- Add: "Before locking a spec, ALL Gemini review items must be PASS (not PASS WITH WARNINGS)"
- Add: "For any function involving windowing, aggregation, or iterative state, include `pseudocode:` in spec.yaml"
- Add: "formula.md must have a ## Scope section at the top mapping each equation to status: implemented | deferred"
- Add: "Spec tags follow strict format: `spec-<strategy_id>-v<MAJOR>.<MINOR>`"

### tools/validate_spec.py
- Add: cross-reference check that every `formula_latex` symbol appears in either signal.inputs, signal.parameters, or a function return
- Add: warning if functions involving windowing/aggregation lack `pseudocode:` field
- Add: `--validate-change-request` mode

### tools/ingest.py
- No changes needed. Worked well.

### tools/call_gemini.py
- Add: `--mode review-diff` for incremental reviews
- Add: `--formula` should accept `formula_contract.md` (after 7.5)

## 9) Next actions I recommend (ordered)

1. **Write codex_debrief.md and gemini_debrief.md** — capture their perspectives before context is lost
2. **Implement `tools/lock_spec.py`** (proposal 7.3) — prevents premature lock, enforces naming. Zero dependencies.
3. **Add `pseudocode:` field to spec schema** (proposal 7.2) — update validate_spec.py, update CLAUDE.md rules. Retroactively add pseudocode for `estimate_covariance`.
4. **Create venv wrapper scripts** (proposal 7.6) — 10 minutes of work, eliminates a recurring error class.
5. **Add structured change request schema** (proposal 7.4) — update validate_spec.py, update codex_tasks/build-from-spec.md.
6. **Split formula.md** (proposal 7.5) — update call_gemini.py and CLAUDE.md. Requires deciding auto-generation approach.
7. **Build `tools/pipeline.py`** (proposal 7.1) — largest effort, highest long-term payoff. Do after simpler items stabilise.
