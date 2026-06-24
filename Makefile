# Convenience wrapper around the workshop CLI and pip.
# Run `make` (or `make help`) to see the available commands.
#
# Everything installs into and runs from a local .venv, so the interpreter that
# has the dependencies is always the one that runs the demo. This avoids the
# trap where `pip` installs into one `python3` (e.g. a mise/pyenv version) but
# `./workshop`'s `#!/usr/bin/env python3` shebang resolves to a different one --
# which surfaces as "ModuleNotFoundError: No module named 'claude_agent_sdk'".

PYTHON ?= python3
VENV := .venv
VENV_PY := $(VENV)/bin/python

.DEFAULT_GOAL := help

.PHONY: help install test replay demo clean

help: ## Show this help
	@echo "Agent SDK Workshop -- common tasks:"
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "First time? Run 'make install' then 'make replay' (offline, no key)."

$(VENV_PY):
	$(PYTHON) -m venv $(VENV)

install: $(VENV_PY) ## Create .venv and install dependencies into it
	$(VENV_PY) -m pip install -r requirements.txt

test: $(VENV_PY) ## Run the replay tests (no API key needed)
	$(VENV_PY) -m pip install -q pytest
	$(VENV_PY) -m pytest 01-guided-demo/test_replay.py

replay: ## Re-render the captured transcript offline (no API key needed)
	$(VENV_PY) workshop replay

demo: ## Run the live guided demo (needs ANTHROPIC_API_KEY + credits)
	$(VENV_PY) workshop demo

clean: ## Remove Python caches (keeps .venv; use 'rm -rf .venv' to reset)
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache
