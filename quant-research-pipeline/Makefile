.PHONY: extract review validate status test clean

VENV := .venv-extract/bin/python
STRATPIPE := .venv-stratpipe/bin/python

extract:
	$(VENV) tools/ingest.py $(STRATEGY_DIR)/input/source.pdf -s $(STRATEGY_ID)

review:
	$(VENV) tools/call_gemini.py --mode review \
		--spec $(STRATEGY_DIR)/spec/spec.yaml \
		--formula $(STRATEGY_DIR)/synth/formula.md \
		-o $(STRATEGY_DIR)/spec/review.md

validate:
	$(VENV) tools/validate_spec.py $(STRATEGY_DIR)/spec/spec.yaml

status:
	$(VENV) tools/update_state.py $(STRATEGY_DIR) --status

test:
	$(STRATPIPE) -m pytest $(STRATEGY_DIR)/repo/tests -q

clean:
	@echo "Nothing to clean yet"
