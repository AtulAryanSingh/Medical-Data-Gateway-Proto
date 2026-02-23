# Medical Data Gateway — Developer Makefile
#
# Common targets:
#   make setup       Install Python dependencies
#   make data        Generate synthetic DICOM files for demo
#   make test        Run the test suite
#   make demo        Generate data + run the pipeline + open the notebook
#   make clean       Remove generated data and processed files

PYTHON ?= python
PYTEST ?= python -m pytest

.PHONY: setup data test pipeline run notebook demo clean

# ── Install dependencies ───────────────────────────────────────────────────
setup:
	pip install -r requirements.txt

# ── Generate synthetic sample data ────────────────────────────────────────
data:
	$(PYTHON) scripts/generate_sample_data.py

# ── Run the test suite ────────────────────────────────────────────────────
test:
	$(PYTEST) tests/ -v

# ── Audit DICOM files for Protected Health Information ────────────────────
audit:
	$(PYTHON) scripts/audit_phi.py

# ── Run the batch pipeline against sample data ────────────────────────────
pipeline:
	$(PYTHON) -c "\
import logging; logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s'); \
from src.pipeline import process_folder; \
r = process_folder(); \
print(r.summary())"

# ── Full end-to-end run: data → pipeline → clustering → QC → reports ─────
run:
	$(PYTHON) scripts/run_full_pipeline.py

# ── Open the demo notebook ────────────────────────────────────────────────
notebook:
	jupyter notebook notebooks/demo_walkthrough.ipynb

# ── Full demo: generate → process → open notebook ─────────────────────────
demo: data pipeline notebook

# ── Remove generated artefacts ────────────────────────────────────────────
clean:
	find data/raw     -name "*.dcm" -delete 2>/dev/null || true
	find data/processed -name "*.dcm" -delete 2>/dev/null || true
	find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
