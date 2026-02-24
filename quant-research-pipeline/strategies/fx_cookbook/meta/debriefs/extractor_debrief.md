# Extractor (PDF Tooling / Extraction Agent) — fx_cookbook Debrief

## 0) Metadata

```yaml
agent: extractor
session: pipeline tooling build + fx_cookbook PDF extraction
date: 2026-02-23
strategy_id: fx_cookbook
scope_owned: tools/*, strategies/<id>/extract/* (write), requirements-extract.txt
venv_used: /home/ak-old-one/projects/pdf-algo-extractor/quant-research-pipeline/.venv-extract/bin/python
```

## 1) What I worked on

- **Built the extraction and pipeline tooling suite** (5 tools):
  - `tools/ingest.py` — PDF→markdown with Marker (primary) + Gemini (fallback), scanned/text-layer auto-detection, extract report generation
  - `tools/call_gemini.py` — unified 3-mode Gemini wrapper (extract, review, verify-tex)
  - `tools/validate_spec.py` — deterministic spec.yaml schema gate (no LLM, pure structure check)
  - `tools/update_state.py` — filesystem-derived pipeline state tracker
  - `tools/init_strategy.sh` — strategy directory scaffolder
- **Removed stale v0 scripts** that were non-functional:
  - `tools/scan_pdf.py` (PyMuPDF text-only extraction, no equation preservation)
  - `tools/extract_modules.py` (NotImplementedError stub)
  - `tools/pipeline.py` (imported the above two, dead on arrival)
- **Ran fx_cookbook extraction**: 45-page Deutsche Bank PDF → 181KB raw.md (4129 lines), 108 display equations, 46 figure captions, 71 table rows
- **Set up `.venv-extract`** with Marker, google-genai, pypdf, typer, rich
- **Authored `requirements-extract.txt`** with pinned version ranges

## 2) Files I changed (exact paths)

**Created (commit `cf07a9e`):**
- `tools/ingest.py` (207→180 lines, rewrote from 66-line v0)
- `tools/call_gemini.py` (196 lines, rewrote from 37-line v0)
- `tools/validate_spec.py` (166 lines, new)
- `tools/update_state.py` (159 lines, new)
- `tools/init_strategy.sh` (65 lines, new)

**Removed (commit `cf07a9e`):**
- `tools/scan_pdf.py` (55 lines, PyMuPDF-only, no LaTeX preservation)
- `tools/extract_modules.py` (38 lines, NotImplementedError stub)
- `tools/pipeline.py` (49 lines, imported dead code)
- `tools/__pycache__/*.pyc` (should not have been in repo from `8e3c00e`)

**Produced (commit `1038c86`):**
- `strategies/fx_cookbook/extract/raw.md` (181,111 chars, 4129 lines)
- `strategies/fx_cookbook/extract/extract_report.json`
- `strategies/fx_cookbook/extract/.done`
- `strategies/fx_cookbook/input/source.pdf` (copied from user-provided path)

**Pre-existing (commit `8e3c00e`, scaffolded before extractor session):**
- `requirements-extract.txt`

## 3) Commands I ran (important ones)

```bash
# Create extraction venv
python3 -m venv .venv-extract
.venv-extract/bin/pip install -U pip
.venv-extract/bin/pip install -r requirements-extract.txt

# Run extraction (Marker attempted first, fell back to Gemini due to CUDA)
.venv-extract/bin/python tools/ingest.py strategies/fx_cookbook/input/source.pdf --strategy-id fx_cookbook

# Validate spec (used by other agents, I built the tool)
.venv-extract/bin/python tools/validate_spec.py strategies/fx_cookbook/spec/spec.yaml

# Check pipeline state
.venv-extract/bin/python tools/update_state.py strategies/fx_cookbook --status
```

## 4) Issues encountered

### 4.1 — Marker CUDA failure, fell back to Gemini
- **Symptom:** `CUDA error: no kernel image is available for execution on the device` during Marker extraction
- **Root cause:** Marker's underlying PyTorch model requires a CUDA-compatible GPU kernel. The machine has a GPU but the installed CUDA toolkit or PyTorch build doesn't match the GPU architecture (likely compute capability mismatch).
- **Where introduced:** Environment setup — `requirements-extract.txt` doesn't pin PyTorch/CUDA versions. `pip install marker-pdf` pulls whatever torch version it wants.
- **Fix:** Gemini fallback handled it gracefully. The extract_report.json records the warning and method=gemini.
- **Prevention:** (a) Pin `torch` version in requirements-extract.txt matching the machine's CUDA toolkit. (b) Add CPU-only Marker support as a second fallback (slower but deterministic). (c) Pre-flight GPU check: `tools/check_gpu.sh` that validates CUDA before attempting Marker.

### 4.2 — strategy_id in extract_report.json was the PDF filename, not the strategy ID
- **Symptom:** `extract_report.json` has `"strategy_id": "FX Cookbook A Recipe for Systematic Investing in Currency Markets"` instead of `"fx_cookbook"`
- **Root cause:** `ingest.py` line 97: `sid = strategy_id or pdf_path.stem` — when `--strategy-id` was passed correctly as `fx_cookbook`, the report should have `fx_cookbook`. But the report shows the PDF title, suggesting the first run used the PDF path stem as the strategy ID (before `--strategy-id` was added or when it wasn't passed).
- **Where introduced:** Either the first invocation didn't pass `--strategy-id`, or the PDF filename was used as fallback during an early run and the report wasn't regenerated.
- **Fix:** The extraction output (raw.md) went to the correct directory (`strategies/fx_cookbook/extract/`), so the downstream pipeline was unaffected. The report metadata is cosmetically wrong.
- **Prevention:** `ingest.py` should validate that `strategy_id` is a valid Python identifier (no spaces, lowercase). If the PDF stem fallback produces invalid names, reject and require explicit `--strategy-id`.

### 4.3 — __pycache__ committed in initial scaffold
- **Symptom:** `tools/__pycache__/call_gemini.cpython-313.pyc` and `scan_pdf.cpython-313.pyc` were committed in `8e3c00e`
- **Root cause:** `.gitignore` didn't exist yet when the initial scaffold was committed
- **Where introduced:** `8e3c00e` — the scaffold commit
- **Fix:** Removed in `cf07a9e` and `.gitignore` added
- **Prevention:** `.gitignore` must be the first file created in any new repo, before any Python runs. `init_strategy.sh` should create `.gitignore` as Step 0.

### 4.4 — meta.json left as empty template
- **Symptom:** `strategies/fx_cookbook/input/meta.json` has empty fields: `{"title": "", "authors": [], "date": "", "source_url": ""}`
- **Root cause:** `init_strategy.sh` creates a template meta.json but nobody filled it in. No downstream tool reads it.
- **Where introduced:** `init_strategy.sh` template
- **Fix:** Not fixed. meta.json is unused by the pipeline.
- **Prevention:** Either (a) `ingest.py` auto-populates meta.json from PDF metadata (pypdf can extract title, author, date), or (b) remove meta.json from the scaffold if nothing uses it.

### 4.5 — No extraction quality gate
- **Symptom:** raw.md is produced and `.done` is touched regardless of extraction quality. There's no check for: minimum equation count, section structure, or garbled content.
- **Root cause:** `ingest.py` has no post-extraction validation. Any non-empty Gemini response is accepted.
- **Where introduced:** `ingest.py` design
- **Fix:** Not yet implemented.
- **Prevention:** Add post-extraction sanity checks: (a) minimum char count (already exists: `.done` is unconditional), (b) equation count ≥ expected (from meta.json or heuristic), (c) section heading structure (at least one `#` heading), (d) no truncation (last page markers present).

### 4.6 — Gemini extraction includes legal disclaimers and boilerplate
- **Symptom:** The last ~600 lines of raw.md (lines 3500–4129) are regulatory disclaimers, copyright notices, and distribution restrictions — not research content.
- **Root cause:** Gemini extracted EVERYTHING as instructed ("Do NOT summarise or omit content — extract EVERYTHING"). The prompt doesn't distinguish research content from boilerplate.
- **Where introduced:** `ingest.py` Gemini prompt
- **Fix:** Not fixed. Claude (synthesiser) manually ignored the boilerplate when reading raw.md.
- **Prevention:** Add post-processing step or prompt instruction: "Omit pages that are purely regulatory disclaimers, copyright notices, or distribution restrictions. Mark the boundary with `---END OF RESEARCH CONTENT---`."

## 5) Where I caused problems / confusion

1. **No extraction quality metrics**: Produced raw.md with no quality score. Claude had to manually verify that equations were preserved correctly by reading through 4000+ lines. A simple extraction quality report (equation count, table count, section count, suspected garbled passages) would have saved significant downstream time.

2. **Marker/Gemini fallback was silent**: The CUDA failure was logged to extract_report.json but not surfaced to the user or pipeline state. If someone checked `.pipeline_state.yaml` it would show `ingest: done` with no indication that Marker failed and Gemini was used. The quality characteristics of Marker vs Gemini extraction are different (Marker preserves layout better, Gemini preserves equations better) — this should be visible.

3. **Left stale scaffolding artifacts**: The initial scaffold (`8e3c00e`) committed __pycache__, dead stubs (extract_modules.py, pipeline.py), and a half-written scan_pdf.py. These were cleaned up in the next commit but they created confusion about what tools were real vs. stubs.

4. **validate_spec.py doesn't cross-reference with formula.md**: The tool validates spec.yaml structure but doesn't check that formula symbols match spec inputs/parameters. This gap is filled by Gemini review, but a deterministic check would be faster and more reliable.

5. **update_state.py uses `sys.executable` for pytest**: Line 88 (`subprocess.run([sys.executable, "-m", "pytest", ...])`) uses whatever Python is running update_state.py (the extract venv), not the stratpipe venv. If `.venv-extract/bin/python` runs update_state.py, it runs pytest from the wrong venv, which may fail or give wrong results.

## 6) What slowed us down (top 3)

1. **Marker CUDA failure + implicit Gemini fallback**: The Marker failure cost wall-clock time (attempted, failed, retried with Gemini) and produced a different extraction quality profile than expected. Had we known upfront that Marker wouldn't work, we'd have gone straight to Gemini and potentially tuned the prompt for equation-heavy financial PDFs.

2. **No extraction quality gate**: Claude had to manually read raw.md to verify equation fidelity. A simple automated check ("does raw.md contain at least N display equations?") would have caught extraction failures instantly.

3. **Two venvs with unclear boundaries**: `.venv-extract` runs tools/, `.venv-stratpipe` runs repo/. The boundary is documented in CLAUDE.md but not enforced. update_state.py calls pytest with the wrong venv (issue 4.5 above), which could produce false "test: done" states.

## 7) Refactor proposals (highest ROI)

### 7.1 — Extraction quality report
- **Change:** After producing raw.md, `ingest.py` generates `extract/quality_report.json` with: `{equation_count, table_count, figure_count, section_count, total_chars, total_lines, boilerplate_lines, suspected_garbled: []}`. Pipeline state gate checks quality thresholds before marking `ingest: done`.
- **Payoff:** Catches bad extractions immediately. Claude doesn't have to manually verify 4000 lines.
- **Owner:** tools/ingest.py
- **Risk:** Counting equations by regex (`$$`) may miscount. Mitigate: use `$$` pairs for display, single `$` pairs for inline. Good enough for a gate.

### 7.2 — Explicit extraction method in pipeline state
- **Change:** `.pipeline_state.yaml` ingest stage includes `method: gemini|marker` and `warnings: [...]`. Pipeline state display shows the method.
- **Payoff:** Downstream agents know what extraction quality to expect. Marker = better layout, Gemini = better equation fidelity.
- **Owner:** tools/update_state.py + tools/ingest.py
- **Risk:** None.

### 7.3 — Pre-flight GPU check
- **Change:** `tools/check_gpu.sh` that: (a) checks `nvidia-smi`, (b) checks PyTorch CUDA availability, (c) checks Marker model compatibility. Run before `ingest.py` to decide route upfront (not via try/catch).
- **Payoff:** Eliminates wasted Marker attempt + CUDA error time. Faster extraction.
- **Owner:** tools/
- **Risk:** Adds a dependency on nvidia-smi. Mitigate: graceful "no GPU" detection that defaults to Gemini.

### 7.4 — Auto-populate meta.json from PDF metadata
- **Change:** `ingest.py` extracts title, authors, creation date from PDF metadata (pypdf already imported) and populates `meta.json`. Falls back to empty if metadata is absent.
- **Payoff:** meta.json becomes useful. Could feed into LaTeX note generation (author names, dates).
- **Owner:** tools/ingest.py
- **Risk:** PDF metadata is often incomplete or wrong. Mitigate: populate what's available, leave rest empty.

### 7.5 — Boilerplate stripping in post-processing
- **Change:** After Gemini extraction, detect and strip regulatory boilerplate pages. Heuristic: pages that match patterns like "Deutsche Bank AG", "Provided for the exclusive use", "DO NOT REDISTRIBUTE", legal jurisdiction lists. Move stripped content to `extract/boilerplate.md` for audit trail.
- **Payoff:** raw.md is pure research content. Claude doesn't need to skip 600 lines of disclaimers.
- **Owner:** tools/ingest.py
- **Risk:** May accidentally strip relevant content if heuristics are too aggressive. Mitigate: conservative patterns (multi-line legal blocks only), preserve in separate file for review.

### 7.6 — Fix update_state.py venv for pytest
- **Change:** `update_state.py` should read the venv path from config (or AGENTS.md/CLAUDE.md) rather than using `sys.executable`. For the `test` stage check, it should use `.venv-stratpipe/bin/python -m pytest`.
- **Payoff:** Correct test status regardless of which venv runs the state checker.
- **Owner:** tools/update_state.py
- **Risk:** Hardcoding venv path. Mitigate: use a `pipeline_config.yaml` or `.env` variable.

### 7.7 — Deterministic symbol cross-reference tool
- **Change:** `tools/validate_symbols.py` that parses formula.md symbol table and spec.yaml inputs/parameters, checks 1:1 mapping for in-scope equations. Runs before Gemini review as a fast pre-gate.
- **Payoff:** Catches symbol mismatches deterministically (no LLM non-determinism). Reduces Gemini review cycles.
- **Owner:** tools/
- **Risk:** LaTeX symbol parsing is fragile. Mitigate: parse the markdown symbol table (pipe-separated), not raw LaTeX. Good enough for variable names.

## 8) Skill + instruction updates needed

### CLAUDE.md
- Add: "After running ingest, check `extract/extract_report.json` for `method` and `warnings`. If Marker failed, note in pipeline log."
- Add: "If extraction quality is suspect (few equations, garbled sections), re-run with explicit Gemini mode or debug Marker CUDA."
- Update tool command reference: add `tools/check_gpu.sh` (after 7.3)
- Update tool command reference: add `tools/validate_symbols.py` (after 7.7)

### AGENTS.md
- No changes needed (extractor doesn't operate under AGENTS.md; it's a tool provider, not a Codex-like builder)

### codex_tasks/build-from-spec.md
- No changes needed (Codex doesn't interact with extraction tools)

### tools/ingest.py
- Add extraction quality report (proposal 7.1)
- Add meta.json auto-population (proposal 7.4)
- Add boilerplate stripping (proposal 7.5)
- Validate `strategy_id` format (lowercase, no spaces, valid Python identifier)
- Add `--method` flag to force marker|gemini (skip auto-detection)

### tools/validate_spec.py
- Add cross-reference check: spec function descriptions → spec args (Codex's proposal 7.6 from codex_debrief)
- Add `pseudocode:` field detection for windowed/aggregation functions (Claude's proposal from claude_debrief)

### tools/update_state.py
- Include extraction method and warnings in pipeline state (proposal 7.2)
- Fix pytest venv to use `.venv-stratpipe` (proposal 7.6)
- Add configurable venv paths (from `pipeline_config.yaml` or env)

### tools/call_gemini.py
- Add `--bib` flag to `verify-tex` mode (Gemini's proposal from gemini_debrief)
- Add `--mode review-diff` with `--prev-review` (Gemini's proposal)
- Update review prompt for scope-aware symbol checking (Gemini's proposal)

### New tools
- `tools/check_gpu.sh` — pre-flight CUDA/Marker compatibility check (proposal 7.3)
- `tools/validate_symbols.py` — deterministic formula↔spec symbol cross-reference (proposal 7.7)

## 9) Next actions I recommend (ordered)

1. **Fix `update_state.py` pytest venv** (proposal 7.6) — 5-minute fix, prevents false `test: done` states. Zero risk.
2. **Add extraction quality report** (proposal 7.1) — straightforward regex-based counters. Immediate payoff for next strategy extraction.
3. **Add `--method` flag to `ingest.py`** — skip auto-detection when GPU status is known. 10 minutes.
4. **Auto-populate meta.json** (proposal 7.4) — pypdf already imported. 15 minutes.
5. **Add pre-flight GPU check** (proposal 7.3) — prevents wasted Marker attempt. 20 minutes.
6. **Validate strategy_id format in `ingest.py`** — reject spaces, uppercase, non-identifier chars. 5 minutes.
7. **Build `tools/validate_symbols.py`** (proposal 7.7) — medium effort but high payoff across all strategies.
8. **Add boilerplate stripping** (proposal 7.5) — lower priority, cosmetic improvement. Claude can work around it.
