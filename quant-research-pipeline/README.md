# Quant Research Pipeline

A structured pipeline for converting research PDFs into implementable trading strategies.

## Directory Structure

| Directory | Purpose |
|-----------|---------|
| `extract/` | Raw extraction output (OCR/marker/gemini) |
| `synth/` | Cleaned synthesis (human-readable) |
| `spec/` | Spec contract (SPEC.md + spec.yaml) |
| `tools/` | Scripts (call_gemini.py, validate_spec.py) |
| `repo/` | Actual Python package + tests |
| `notebooks/` | Thin demos that import from repo/ |
| `tex/` | LaTeX note output |
| `templates/` | Reusable templates |

## Usage

```bash
# Scan all PDFs in inbox
make scan

# Extract modules from notebooks
make extract

# Run full pipeline
make all
```
