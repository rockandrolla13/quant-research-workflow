# Gemini (Mathematical Reviewer) — fx_cookbook Debrief

## 0) Metadata

```yaml
agent: gemini
session: fx_cookbook spec review (5 cycles) + LaTeX verification (1 cycle)
date: 2026-02-23
strategy_id: fx_cookbook
scope_owned: strategies/fx_cookbook/spec/review.md, strategies/fx_cookbook/tex/review_tex.md (write-only outputs)
venv_used: N/A (API-only agent, called via .venv-extract/bin/python tools/call_gemini.py)
model: gemini-2.5-flash
```

## 1) What I worked on

- **5 spec review cycles** against spec.yaml + formula.md, producing structured checklists covering: symbol consistency, LaTeX validity, dimensional consistency, test case consistency, data frequency compatibility, unstated assumptions
- **1 LaTeX verification cycle** on tex/note.tex, checking: equation syntax, notation consistency, delimiter matching, ref/label pairs, cite/bib key pairs
- Progressively hardened the spec from 6 actionable warnings (v1.0) down to 3 cosmetic-only warnings (final)

### Review arc:
| Cycle | Spec ver | Commit | Warnings | Key findings |
|-------|----------|--------|----------|--------------|
| 1 | v1.0 | `1038c86` | 6 WARN | Missing `total_return` input, undefined `σ_r` derivation, N symbol overload in formula.md, no carry smoothing param, no USD PC1 method, hysteresis init |
| 2 | v1.1 | `6ac188f` | 4 WARN | Still missing `total_return`, `σ_r` still unspecified, no `carry_smoothing_window`, no `cost_bps`, covariance 3-offset detail missing from function description |
| 3 | v1.2 | `d7bcc92` | 1 WARN | Composite signal aggregation ambiguity (how momentum + carry are combined) |
| 4 | v1.2+ | `0711cc9` | 5 WARN | formula.md scope mismatch (extension signals present without spec entries), dimensional ambiguity in carry/vol units, vol unit interpretation in test cases |
| 5 (final) | v1.2+ | `3885a83` | 3 WARN (cosmetic) | Bdays-per-month constant `21`, business days assumption implicit, FX quoting convention unspecified |

### LaTeX review:
| Cycle | File | Commit | Result |
|-------|------|--------|--------|
| 1 | note.tex | `bd8e601` | All 5 checks PASS |

## 2) Files I changed (exact paths)

Gemini does not modify source files. It writes review outputs only:

- `strategies/fx_cookbook/spec/review.md` — overwritten on each review cycle (5 versions across 5 commits)
- `strategies/fx_cookbook/tex/review_tex.md` — written once

## 3) Commands I ran (important ones)

Gemini was invoked externally by Claude via:

```bash
# Spec review (ran 5 times with evolving spec.yaml + formula.md)
.venv-extract/bin/python tools/call_gemini.py --mode review \
  --spec strategies/fx_cookbook/spec/spec.yaml \
  --formula strategies/fx_cookbook/synth/formula.md \
  --output strategies/fx_cookbook/spec/review.md

# LaTeX verification (ran 1 time)
.venv-extract/bin/python tools/call_gemini.py --mode verify-tex \
  --tex strategies/fx_cookbook/tex/note.tex \
  --output strategies/fx_cookbook/tex/review_tex.md
```

## 4) Issues encountered

### 4.1 — Inconsistent warning severity across cycles
- **Symptom:** Cycle 3 (v1.2) produced only 1 WARN (composite aggregation), but Cycle 4 (same spec, minor formula.md changes) produced 5 WARNs including issues that should have been flagged in Cycle 3 (scope mismatch, dimensional ambiguity)
- **Root cause:** Non-deterministic LLM output. Each call is a fresh inference with no memory of prior reviews. The review prompt does not include prior review output for continuity.
- **Where introduced:** `tools/call_gemini.py` — `review_spec()` takes only spec + formula, not prior review context
- **Fix:** Not yet fixed
- **Prevention:** Add `--prev-review` flag to `call_gemini.py` that appends prior review.md to the prompt, with instruction "check if prior warnings are resolved and flag any regressions"

### 4.2 — Scope mismatch warnings were a false positive pattern
- **Symptom:** Cycles 1, 4 flagged "formula.md contains Value/MSO/COFFEE/CFTC symbols not in spec.yaml" as WARN. This was by design — formula.md documents the full paper, spec.yaml implements a subset.
- **Root cause:** The review prompt says "every symbol in formula.md appears in spec.yaml" without scoping awareness. Gemini correctly flagged the mismatch but lacked context that it was intentional.
- **Where introduced:** `tools/call_gemini.py` — review prompt line 1 ("Every symbol in formula.md appears in spec.yaml signal.inputs or parameters") is too strict
- **Fix:** Claude added a scope disclaimer to formula.md (`3885a83`). Gemini accepted it in Cycle 5.
- **Prevention:** (a) The review prompt should say "every symbol used by **in-scope** formulas" rather than all formulas. (b) formula.md should always have a `## Scope` section that Gemini can reference. (c) Alternatively, pass `formula_contract.md` (implemented subset only) instead of the full reference.

### 4.3 — Dimensional ambiguity in carry/vol was a real catch
- **Symptom:** Cycle 4 flagged that `σ_{r_{i,t}}` is documented as "% annualised" but used in division with dimensionless `c_{i,t}`. This is a genuine unit mismatch if vol is in percent (10%) rather than decimal (0.10).
- **Root cause:** The symbol table in formula.md listed units as "% annualised" which is ambiguous — it could mean "expressed as a percentage" or "expressed as a decimal representing a percentage."
- **Where introduced:** formula.md symbol table
- **Fix:** Not explicitly resolved — Cycle 5 accepted it implicitly (likely because in practice all computations use decimals). Should be clarified.
- **Prevention:** Symbol table should specify "decimal (e.g., 0.10 for 10%)" or "percentage (e.g., 10 for 10%)" explicitly. validate_spec.py could enforce a `units_convention:` field.

### 4.4 — LaTeX review assumed refs.bib exists without verifying
- **Symptom:** Tex review said "PASS" on cite/bib pairs but noted "it is assumed that the `anand2019fxcookbook` entry exists in your bibliography file" — i.e., it couldn't verify because refs.bib wasn't provided.
- **Root cause:** `verify-tex` mode only receives the .tex file, not the .bib file.
- **Where introduced:** `tools/call_gemini.py` — `verify_tex()` only takes `tex_path`, not `bib_path`
- **Fix:** Not yet fixed
- **Prevention:** Add `--bib` optional flag to `verify-tex` mode. If provided, concatenate refs.bib content into the prompt for cross-reference checking.

### 4.5 — N symbol overload in formula.md
- **Symptom:** Cycle 1 correctly flagged that `N` in Eq. 6 means "smoothing window" but the symbol table defines `N` as "number of currencies (24)". This was a genuine error in formula.md.
- **Root cause:** When transcribing Eq. 6 from the paper, the carry smoothing window variable was labeled `N` (matching the paper's notation) instead of `L` (which avoids collision with the cross-asset count).
- **Where introduced:** formula.md initial draft
- **Fix:** Claude renamed the variable to `L` in Eq. 6 and updated the description. By Cycle 2 this specific warning was resolved.
- **Prevention:** Symbol table should be treated as a reserved namespace. validate_spec.py could check that no symbol is used with two different meanings.

## 5) Where I caused problems / confusion

1. **Non-deterministic output across cycles**: Cycle 3 missed issues that Cycle 4 caught. This created a false sense of completeness after Cycle 3 — Claude proceeded thinking the spec was nearly clean, then Cycle 4 surfaced 5 new warnings. This is inherent to LLM-as-reviewer and should be documented as a known limitation.

2. **Overly strict symbol scope check**: Flagging every formula.md symbol as a WARN even when formula.md explicitly serves as a reference document (not a contract) caused 2 unnecessary review cycles. The prompt should have been scoped to "implemented signals only."

3. **Accepted the composite signal ambiguity too easily**: Cycle 3 flagged that `fx_cookbook_composite` doesn't define how momentum + carry are aggregated. This was a real design gap. But by Cycle 5 it disappeared from warnings without being resolved — likely because the scope disclaimer redirected attention. The question of how to combine signals remains open.

4. **Did not verify refs.bib cross-references**: The LaTeX review claimed PASS on cite/bib pairs without actually seeing the .bib file. This could mask missing bibliography entries.

## 6) What slowed us down (top 3)

1. **5 review cycles to reach clean PASS**: Each cycle required Claude to read the review, fix spec/formula, re-run Gemini, and re-read. With better prompt scoping (implemented-only symbols, prior review context), this could have converged in 2-3 cycles.

2. **False positive scope mismatch warnings**: Cycles 1 and 4 spent warnings on the formula.md → spec.yaml scope gap that was intentional. Each false positive triggered a fix cycle. The scope disclaimer fix was simple but took time to identify as the correct resolution.

3. **No incremental/diff review mode**: Every review re-evaluated the entire spec from scratch. After fixing one WARN, the next cycle might find completely different issues. A diff-aware review ("what changed since last review? are prior warnings resolved?") would make convergence monotonic.

## 7) Refactor proposals (highest ROI)

### 7.1 — Diff-aware review mode
- **Change:** `call_gemini.py --mode review-diff --prev-review review_v1.1.md` that: (a) shows Gemini the prior review, (b) shows the diff of spec.yaml and formula.md since prior review, (c) asks "are prior warnings resolved? any new issues?"
- **Payoff:** Monotonic convergence. No re-discovering issues. Estimated cycle reduction: 5 → 2-3.
- **Owner:** tools/call_gemini.py
- **Risk:** Gemini may anchor on prior review and miss regressions. Mitigate: full review on major version bumps, diff review on patches.

### 7.2 — Scoped review prompt
- **Change:** Update review prompt to: "Check symbol consistency for **formulas marked as in-scope in formula.md's ## Scope section**. Extension formulas should not trigger symbol warnings." Also require formula.md to have a `## Scope` section.
- **Payoff:** Eliminates the false-positive scope mismatch class entirely.
- **Owner:** tools/call_gemini.py + CLAUDE.md (formula.md writing rules)
- **Risk:** None. Strictly more precise.

### 7.3 — Include refs.bib in verify-tex mode
- **Change:** Add `--bib` optional flag to `verify-tex` mode. If provided, append `## refs.bib\n{content}` to the prompt.
- **Payoff:** Enables real cite/bib cross-reference verification instead of "assumed to exist."
- **Owner:** tools/call_gemini.py
- **Risk:** Increases prompt token count slightly. Negligible.

### 7.4 — Structured WARN severity levels
- **Change:** Review output should classify warnings as: `WARN-BLOCKING` (must fix before lock), `WARN-COSMETIC` (clarification, can lock with these). The lock gate (`tools/lock_spec.py`) blocks on WARN-BLOCKING only.
- **Payoff:** Prevents cosmetic warnings (bdays constant, quote convention) from blocking the pipeline while ensuring substantive issues (missing functions, unit ambiguity) are resolved.
- **Owner:** tools/call_gemini.py (prompt update) + tools/lock_spec.py (new tool)
- **Risk:** Gemini may inconsistently classify severity. Mitigate: provide examples in the prompt for each severity level.

### 7.5 — Review checklist versioning
- **Change:** Each review.md should include a header with: `spec_version`, `formula_md_hash`, `review_cycle_number`, `prior_review_cycle`. Store all reviews as `review_v1.0.md`, `review_v1.1.md`, etc. instead of overwriting.
- **Payoff:** Full audit trail. Can diff reviews to see convergence pattern. Prior reviews available for diff-aware mode.
- **Owner:** tools/call_gemini.py (output naming) + CLAUDE.md (pipeline rules)
- **Risk:** File proliferation. Mitigate: keep only latest 3 reviews; archive older ones.

### 7.6 — Symbol table validation tool
- **Change:** Standalone `tools/validate_symbols.py` that: (a) parses formula.md symbol table, (b) parses spec.yaml inputs/parameters, (c) checks 1:1 mapping for in-scope formulas, (d) checks no symbol is used with two meanings. Run before Gemini review.
- **Payoff:** Deterministic symbol checking — catches what Gemini sometimes misses (non-determinism). Reduces review cycles.
- **Owner:** tools/
- **Risk:** Medium implementation effort (LaTeX parsing). Mitigate: use regex for symbol extraction, not full LaTeX parsing.

## 8) Skill + instruction updates needed

### tools/call_gemini.py
- Add `--mode review-diff` with `--prev-review` flag (proposal 7.1)
- Add `--bib` flag to `verify-tex` mode (proposal 7.3)
- Update review prompt: scope to "in-scope formulas" per formula.md `## Scope` section (proposal 7.2)
- Update review prompt: classify warnings as `WARN-BLOCKING` or `WARN-COSMETIC` (proposal 7.4)
- Add metadata header to review output: `spec_version`, `formula_hash`, `cycle_number` (proposal 7.5)

### CLAUDE.md
- Add: "formula.md MUST have a `## Scope` section listing each equation's status: `implemented` | `deferred`"
- Add: "Gemini review must reach zero WARN-BLOCKING items before spec lock. WARN-COSMETIC items are acceptable."
- Add: "Store review history as `review_v<X>.<Y>.md` — do not overwrite prior reviews"
- Add: "After fixing Gemini warnings, run review-diff mode (not full review) for faster convergence"

### AGENTS.md
- No changes needed (Gemini has no direct agent instructions — it's invoked via tool)

### codex_tasks/build-from-spec.md
- No changes needed (Gemini doesn't interact with build)

### New tool: tools/validate_symbols.py
- Deterministic symbol consistency check (formula.md symbol table ↔ spec.yaml inputs/parameters)
- Run as pre-review gate to reduce Gemini review load

### New tool: tools/lock_spec.py
- Gate: `validate_spec.py` PASS + `validate_symbols.py` PASS + Gemini review has zero WARN-BLOCKING
- Then create tag `spec-<id>-v<MAJOR>.<MINOR>`

## 9) Next actions I recommend (ordered)

1. **Update review prompt to scope-aware** (proposal 7.2) — simplest change, highest immediate payoff. Eliminates false-positive scope warnings on next strategy.
2. **Add WARN-BLOCKING / WARN-COSMETIC classification** (proposal 7.4) — update prompt, define examples. Prevents cosmetic items from blocking the pipeline.
3. **Add `--bib` flag to verify-tex** (proposal 7.3) — 5 minutes of work, fills a verification gap.
4. **Implement review-diff mode** (proposal 7.1) — medium effort, significant cycle reduction. Requires storing prior review files.
5. **Add review versioning** (proposal 7.5) — change output naming convention, update CLAUDE.md rules.
6. **Build validate_symbols.py** (proposal 7.6) — higher effort, but makes symbol checking deterministic and Gemini-independent.
7. **Clarify symbol table unit conventions** — update formula.md template to require "decimal" or "percentage" annotation for all `%`-unit symbols. Prevents the carry/vol dimensional ambiguity from recurring.
