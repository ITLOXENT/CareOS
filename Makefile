PYTHON ?= python3
UV ?= uv
GUARDRAILS_DIR := scripts/guardrails
API_DIR := apps/api

.PHONY: lint typecheck test build verify guardrails format-check audit secret-scan iac

guardrails:
	@$(PYTHON) $(GUARDRAILS_DIR)/check_no_placeholders.py
	@$(PYTHON) $(GUARDRAILS_DIR)/check_no_secrets.py
	@$(PYTHON) $(GUARDRAILS_DIR)/check_iac.py

lint: guardrails
	@pnpm -r lint
	@cd $(API_DIR) && $(UV) run ruff check .

format-check: guardrails
	@pnpm exec prettier --check .
	@cd $(API_DIR) && $(UV) run ruff format --check .

typecheck: guardrails
	@pnpm -r typecheck
	@cd $(API_DIR) && $(UV) run mypy .

test: guardrails
	@pnpm -r --if-present test
	@cd $(API_DIR) && $(UV) run pytest -q

build: guardrails
	@pnpm -r --if-present build

audit: guardrails
	@cd $(API_DIR) && $(UV) run pip-audit -r requirements.txt -r requirements-dev.txt
	@pnpm audit

secret-scan: guardrails
	@$(PYTHON) $(GUARDRAILS_DIR)/check_no_secrets.py

iac: guardrails
	@$(PYTHON) $(GUARDRAILS_DIR)/check_iac.py

verify: lint format-check typecheck test audit secret-scan iac build