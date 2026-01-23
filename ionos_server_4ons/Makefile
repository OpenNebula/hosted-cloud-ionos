.PHONY: help install run clean test
SHELL := /bin/bash

PYTHON := python3
VENV := .venv
SCRIPT := create_server_4ons.py

help:
	@echo "Available targets:"
	@echo "  venv       - Create virtual environment"
	@echo "  install    - Install venv and dependencies"
	@echo "  test       - Test the environment"
	@echo "  run        - Run the script (use snr=1 or snr=2 to specify server number)"
	@echo "  clean      - Remove virtual environment and cache files"
	@echo ""
	@echo "Usage examples:"
	@echo "  make install"
	@echo "  make run snr=1"
	@echo "  make run snr=2"

venv:
	@if [ -n "$(VIRTUAL_ENV)" ]; then \
		echo " Variable VIRTUAL_ENV: $(VIRTUAL_ENV) is not empty"; \
	else \
		echo " Variable VIRTUAL_ENV: $(VIRTUAL_ENV) is empty"; \
		source $(VENV)/bin/activate; \
		echo " Please activate python-venv with:  source .venv/bin/activate"; \
		echo " Terminate early with error!"; \
    	exit 1; \
	fi

install: venv
	echo "Installing dependencies..." && \
	pip install --upgrade pip && \
	pip install -r requirements.txt && \
	echo "Dependencies installed successfully." && \
	echo "" && \
	echo "Virtual environment is now active."

run:
	@if [ -z "$(snr)" ]; then \
		echo "Error: snr variable not set. Use: make run snr=1 or make run snr=2"; \
		exit 1; \
	fi
	@$(VENV)/bin/python $(SCRIPT) -snr $(snr)

clean:
	@echo "Cleaning up..."
	@rm -rf $(VENV)
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete."

test:
	@echo "Testing Python environment..."
	@$(VENV)/bin/python --version
	@echo "Testing installed packages..."
	@$(VENV)/bin/pip list
