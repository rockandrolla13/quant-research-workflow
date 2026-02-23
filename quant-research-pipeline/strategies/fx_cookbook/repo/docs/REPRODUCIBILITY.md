# Reproducibility

All commands use the pinned venv:
`/home/ak-old-one/projects/pdf-algo-extractor/quant-research-pipeline/.venv-stratpipe/bin/python`

## Install

```bash
/home/ak-old-one/projects/pdf-algo-extractor/quant-research-pipeline/.venv-stratpipe/bin/pip install -e strategies/fx_cookbook/repo
```

## Tests

```bash
cd strategies/fx_cookbook/repo
/home/ak-old-one/projects/pdf-algo-extractor/quant-research-pipeline/.venv-stratpipe/bin/python -m pytest -q
```

## Results (no notebooks)

```bash
cd strategies/fx_cookbook/repo
/home/ak-old-one/projects/pdf-algo-extractor/quant-research-pipeline/.venv-stratpipe/bin/python -m fx_cookbook.results
```

Artifacts are written to `strategies/fx_cookbook/repo/outputs/`.
