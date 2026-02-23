.PHONY: test lint install data-sanity backtest notebooks results

PYTHON := /home/ak-old-one/projects/pdf-algo-extractor/quant-research-pipeline/.venv-stratpipe/bin/python

test:
	$(PYTHON) -m pytest -q tests

lint:
	ruff check .

install:
	/home/ak-old-one/projects/pdf-algo-extractor/quant-research-pipeline/.venv-stratpipe/bin/pip install -e .

data-sanity:
	$(PYTHON) -c "from fx_cookbook.data import load_data; load_data('config.yaml')"

backtest:
	$(PYTHON) -m fx_cookbook.results

notebooks:
	$(PYTHON) -m jupyter nbconvert --execute --to notebook notebooks/00_data_sanity.ipynb
	$(PYTHON) -m jupyter nbconvert --execute --to notebook notebooks/01_signal_diagnostics.ipynb
	$(PYTHON) -m jupyter nbconvert --execute --to notebook notebooks/02_backtest_results.ipynb

results:
	$(PYTHON) -m fx_cookbook.results
