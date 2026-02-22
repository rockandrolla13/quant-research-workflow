.PHONY: test lint install

test:
	.venv-stratpipe/bin/python -m pytest -q tests

lint:
	ruff check .

install:
	.venv-stratpipe/bin/pip install -e .
