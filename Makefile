PYTHON ?= python3
GUARDRAILS_DIR := scripts/guardrails

.PHONY: lint typecheck test build verify guardrails

guardrails:
	@$(PYTHON) $(GUARDRAILS_DIR)/check_no_placeholders.py
	@$(PYTHON) $(GUARDRAILS_DIR)/check_no_secrets.py

lint: guardrails
typecheck: guardrails
test: guardrails
build: guardrails
verify: lint typecheck test build
