## 0) Metadata (YAML)
- agent: gemini
- session: pdf-algo-gemini
- date: 2026-02-23
- strategy_id: fx_cookbook
- scope_owned:
  - `quant-research-pipeline/`
  - `strategies/fx_cookbook/`
- venv_used: `.venv-extract/bin/python`

## 1) What I worked on (bullet list)
- **Goals:**
  - Fulfill the roles of "Reviewer" for strategy documents and "Extraction runner" for PDF ingestion.
  - Establish a working PDF extraction pipeline using the Gemini API.
  - Review and ensure consistency between `spec.yaml` and `formula.md`.
- **Tasks completed:**
  - Created and configured a virtual environment with heavy dependencies (`.venv-extract`).
  - Implemented `tools/ingest.py` to process PDFs directly with the Gemini API.
  - Implemented `tools/call_gemini.py` (though `ingest.py`'s direct API call is now primary).
  - Created placeholder and then example-filled versions of `spec.yaml` and `formula.md`.
  - Migrated strategy files to the corrected `strategies/fx_cookbook/` directory structure.
  - Performed two detailed reviews of the strategy contract, checking for consistency and completeness.
- **Outputs produced:**
  - `strategies/fx_cookbook/spec/spec.yaml`
  - `strategies/fx_cookbook/synth/formula.md`
  - `strategies/fx_cookbook/spec/review.md`
  - `strategies/fx_cookbook/tex/review_tex.md`
  - `strategies/fx_cookbook/tex/note.tex`
  - `strategies/fx_cookbook/spec/SPEC.md`
  - `strategies/fx_cookbook/spec/review_results_contract.md`
  - `quant-research-pipeline/tools/ingest.py`
  - `quant-research-pipeline/tools/call_gemini.py`
  - `quant-research-pipeline/requirements-extract.txt`
  - `quant-research-pipeline/extract/raw.md` (from PDF ingestion)

## 2) Files I changed (exact paths)
- `quant-research-pipeline/spec/spec.yaml` (created, then moved)
- `quant-research-pipeline/synth/formula.md` (created, then moved)
- `quant-research-pipeline/tools/call_gemini.py` (created, then corrected)
- `quant-research-pipeline/tools/scan_pdf.py` (modified, then made obsolete by `ingest.py` changes)
- `quant-research-pipeline/tools/ingest.py` (created, then corrected multiple times)
- `quant-research-pipeline/requirements.txt` (created, then made obsolete)
- `quant-research-pipeline/requirements-extract.txt` (created, then corrected)
- `strategies/fx_cookbook/spec/spec.yaml` (created via `mv`)
- `strategies/fx_cookbook/synth/formula.md` (created via `mv`)
- `strategies/fx_cookbook/spec/review.md` (created)
- `strategies/fx_cookbook/tex/review_tex.md` (created)
- `strategies/fx_cookbook/tex/note.tex` (created)
- `strategies/fx_cookbook/spec/SPEC.md` (created)
- `strategies/fx_cookbook/spec/review_results_contract.md` (created, then overwritten)

## 3) Commands I ran (important ones)
- `python3 -m venv .venv-extract`
- `.venv-extract/bin/pip install -U pip`
- `.venv-extract/bin/pip install -r quant-research-pipeline/requirements-extract.txt`
- `.venv-extract/bin/python quant-research-pipeline/tools/ingest.py '/home/ak-old-one/Documents/Work_Quant/FX Cookbook A Recipe for Systematic Investing in Currency Markets.pdf'`
- `mkdir -p strategies/fx_cookbook/spec strategies/fx_cookbook/synth strategies/fx_cookbook/tex`
- `mv quant-research-pipeline/spec/spec.yaml strategies/fx_cookbook/spec/spec.yaml`
- `mv quant-research-pipeline/synth/formula.md strategies/fx_cookbook/synth/formula.md`

## 4) Issues encountered
- **Symptom:** `ModuleNotFoundError: No module named 'google'`
  - **Root cause:** Python dependencies listed in `requirements.txt` were not installed in the venv.
  - **Where it was introduced:** My decision to run `ingest.py` before installing dependencies.
  - **How it was fixed:** Ran `pip install -r requirements-extract.txt`.
  - **How to prevent it:** Add a pre-flight check in `ingest.py` to verify that key dependencies are importable, or have a wrapper script that always runs `pip install` before executing.

- **Symptom:** `ingest.py` fails with "Missing key inputs argument!" for Gemini API.
  - **Root cause:** `GOOGLE_API_KEY` was not loaded into the environment where the script was running.
  - **Where it was introduced:** The user's environment setup.
  - **How it was fixed:** I added `python-dotenv` to the requirements and `load_dotenv()` to `ingest.py`. The user then created the `.env` file.
  - **How to prevent it:** The script should provide a more explicit error if `os.getenv("GOOGLE_API_KEY")` is `None` after trying to load the `.env` file. E.g., "GOOGLE_API_KEY not found. Please set it in your environment or a .env file."

- **Symptom:** `ingest.py` fails with `ModuleNotFoundError: No module named 'fitz'`.
  - **Root cause:** I incorrectly removed `PyMuPDF` (`fitz`) from the dependencies while refactoring `ingest.py`, but a legacy import of `scan_pdf` remained.
  - **Where it was introduced:** My incorrect modification of `ingest.py` and `requirements-extract.txt`.
  - **How it was fixed:** I removed the `scan_pdf` import from `ingest.py` entirely, as the new workflow sends the PDF directly to Gemini.
  - **How to prevent it:** A better dependency validation tool or a pre-commit hook could check for unused imports or missing dependencies.

- **Symptom:** `marker-pdf` fails with a CUDA error.
  - **Root cause:** The user's GPU (NVIDIA GeForce GTX 1070 Ti, CUDA capability 6.1) is not compatible with the PyTorch version installed by `marker-pdf` (which requires >= 7.0).
  - **Where it was introduced:** Dependency selection (`marker-pdf` brings in a specific PyTorch version).
  - **How it was fixed:** The `ingest.py` script was designed to fall back to direct Gemini PDF processing, so this was not a blocking issue for the extraction task.
  - **How to prevent it:** The `ingest.py` script could have an optional flag to disable `marker-pdf` explicitly, e.g., `--no-marker`, to avoid the noisy (but non-fatal) error.

## 5) Where I caused problems / confusion (be honest)
- I repeatedly confused file paths and overwrote files with incorrect content (e.g., writing `ingest.py` content into `requirements-extract.txt`). This created significant rework and required multiple corrective steps.
- My initial understanding of the project structure was incorrect, causing me to place `spec.yaml` and `formula.md` in the wrong root-level directories before being corrected.
- I was not fully aware of the correct, modern `google-genai` SDK usage and initially implemented the legacy `google.generativeai` library, which required correction.

## 6) What slowed us down (top 3)
1.  **Manual Error Correction Loops:** The biggest slowdown was the repeated, manual process of me making a mistake (like overwriting a file), the user noticing and correcting me, and me re-doing the work.
2.  **Unclear Initial State:** The initial instructions were to review files that did not exist, which led to a multi-step process of me discovering this, creating placeholders, and then having them filled. A clearer initial state ("create these files from scratch based on this template") would have been faster.
3.  **Implicit Dependency Management:** The dependency and SDK rules were not provided upfront, leading to rework (e.g., `PyMuPDF` vs. `marker-pdf`, legacy vs. modern Gemini SDK).

## 7) Refactor proposals (highest ROI)
1.  **Change:** Create a `Makefile` or a single `run.sh` script that encapsulates the setup and execution logic.
    - **Expected Payoff:** Eliminates ambiguity in how to set up the venv and run the tools. A `make ingest` command would be more reliable than me remembering `.venv-extract/bin/python tools/ingest.py ...`.
    - **Who owns it:** Tools.
    - **Risk/downsides:** Low. Adds a small maintenance burden to the `Makefile`.

2.  **Change:** Implement a `validate_spec.py` tool that programmatically checks for the issues found in the manual review (e.g., missing annualization constants, inconsistent parameter names between `spec.yaml` and `formula.md`).
    - **Expected Payoff:** Automates the review checklist, reducing manual review time and ensuring consistency. Catches errors early.
    - **Who owns it:** Tools / Spec.
    - **Risk/downsides:** Medium. Requires effort to build and maintain the validation logic.

3.  **Change:** Formalize agent instructions and SDK rules into a `CONTRIBUTING.md` or `AGENT_GUIDELINES.md` file in the project root.
    - **Expected Payoff:** Provides a single source of truth for agent behavior, reducing the need for mid-task corrections on topics like file paths, SDK usage, and dependencies.
    - **Who owns it:** Docs.
    - **Risk/downsides:** Low.

## 8) Skill + instruction updates needed
- **AGENTS.md:** Should be updated to reflect the new, corrected file paths under `strategies/<strategy_name>/`. The rule "Never read from or write to spec/ or synth/ at the project root" should be added.
- **tools/ingest.py:** Should be updated to include the explicit `GOOGLE_API_KEY` check to provide a better error message if the key is missing.
- **CLAUDE.md / commands:** The instructions for a review task should explicitly state whether to create files if they don't exist or to halt. This would have clarified the initial ambiguity.

## 9) Next actions I recommend (ordered)
1.  **Implement the `Makefile` or `run.sh` script.** This will provide immediate stability to the execution workflow.
2.  **Add the explicit `GOOGLE_API_KEY` check to `ingest.py`.** This is a small, high-value change to improve user experience.
3.  **Update the agent guideline documents (`AGENTS.md` or similar).** This will prevent future agents from repeating the same pathing and SDK mistakes.
4.  **Begin scaffolding `tools/validate_spec.py`.** This is a larger task but provides the most long-term value in automating the review process.
