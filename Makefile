# ===============================
# MLOps Makefile – Sketch to Image
# ===============================

PYTHON := python
CONFIG_DIR := mlops/config

# -------- BASIC TASKS --------

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make env        - Create virtual environment"
	@echo "  make install    - Install dependencies"
	@echo "  make data       - Run data processing"
	@echo "  make features   - Run feature generation"
	@echo "  make train      - Train model"
	@echo "  make predict    - Run inference"
	@echo "  make docs       - Serve documentation (MkDocs)"
	@echo "  make docs-build - Build documentation static site"
	@echo "  make clean      - Clean cache/build files"
	@echo ""
	@echo "Version Management:"
	@echo "  make version           - Show current version"
	@echo "  make version-sync     - Sync version across all files"
	@echo "  make version-bump     - Bump version (use PART=major|minor|patch)"


# -------- ENV SETUP --------

env:
	python -m venv .venv
	@echo "Virtual environment created."

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt


# -------- DATA PIPELINE --------

data:
	$(PYTHON) mlops/dataset.py --config $(CONFIG_DIR)/dataset.yaml

features:
	$(PYTHON) mlops/features.py --config $(CONFIG_DIR)/features.yaml


# -------- MODELING --------

train:
	$(PYTHON) mlops/modeling/train.py --config $(CONFIG_DIR)/train.yaml

predict:
	$(PYTHON) mlops/modeling/predict.py --config $(CONFIG_DIR)/predict.yaml


# -------- DOCUMENTATION --------

docs:
	@echo "Starting MkDocs server..."
	@echo "Documentation will be available at http://127.0.0.1:8000"
	mkdocs serve

docs-build:
	@echo "Building documentation..."
	mkdocs build
	@echo "Documentation built in 'site/' directory"

docs-install:
	@echo "Installing MkDocs and dependencies..."
	python3 -m pip install -r requirements-dev.txt


# -------- VERSION MANAGEMENT --------

version:
	@python3 scripts/version.py show

version-sync:
	@python3 scripts/version.py sync

version-bump:
	@if [ -z "$(PART)" ]; then \
		echo "Error: Please specify PART=major|minor|patch"; \
		echo "Example: make version-bump PART=patch"; \
		exit 1; \
	fi
	@python3 scripts/version.py bump $(PART)


# -------- CLEAN --------

clean:
	rm -rf __pycache__ */__pycache__
	find . -name "*.pyc" -delete
	rm -rf site/  # Clean MkDocs build directory
