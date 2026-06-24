PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python
SCRIPT := create_netplan_cfg.py

.PHONY: help venv install run clean

help:
	@echo "Targets:"
	@echo "  make venv     - create virtual environment"
	@echo "  make install  - install dependencies into virtual environment"
	@echo "  make run      - run $(SCRIPT)"
	@echo "  make clean    - remove virtual environment"

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: install
	$(PY) $(SCRIPT)

clean:
	rm -rf $(VENV)
