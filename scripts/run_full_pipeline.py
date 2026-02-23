"""
run_full_pipeline.py - End-to-end pipeline demonstration.

Generates synthetic skull-CT DICOM data (if data/raw is empty),
runs every stage of the Medical Data Gateway pipeline, saves
visualisations to reports/, and prints a final summary.

Usage
-----
    python scripts/run_full_pipeline.py

To use your own data (e.g. the 2_skull_ct dataset) instead of
generated samples, copy your DICOM files into data/raw/ first:

    cp -r 2_skull_ct/DICOM/*.dcm data/raw/
    python scripts/run_full_pipeline.py
"""

import logging
import os
import sys

# Ensure repo root is on sys.path regardless of launch directory
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

import matplotlib
matplotlib.use("Agg")  # non-interactive backend — works without a display

import pydicom

from src.config import CONFIG
from src.pipeline import process_folder
from src.clustering import cluster_scan
from src.scanner_qc import run_qc
from src.visualization import (
    plot_raw_scan,
    plot_windowed_comparison,
    plot_clustering,
    plot_fleet_qc,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
INPUT_FOLDER = os.path.join(_REPO_ROOT, CONFIG["paths"]["input_folder"])
OUTPUT_FOLDER = os.path.join(_REPO_ROOT, CONFIG["paths"]["output_folder"])
REPORTS_FOLDER = os.path.join(_REPO_ROOT, CONFIG["paths"]["reports_folder"])


def _ensure_sample_data() -> None:
    """Generate synthetic data if data/raw/ has no .dcm files."""
    dcm_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".dcm")]
    if dcm_files:
        logger.info("Found %d DICOM file(s) in %s — skipping generation.", len(dcm_files), INPUT_FOLDER)
        return

    logger.info("No DICOM files in %s — generating samples…", INPUT_FOLDER)
    from scripts.generate_sample_data import generate  # noqa: E402 — lazy import
    generate(INPUT_FOLDER)


def main() -> None:
    os.makedirs(REPORTS_FOLDER, exist_ok=True)

    # ── Step 1: Ensure sample data exists ──────────────────────────────────
    print("=" * 60)
    print("STEP 1 — Prepare input data")
    print("=" * 60)
    _ensure_sample_data()
    dcm_files = sorted(f for f in os.listdir(INPUT_FOLDER) if f.endswith(".dcm"))
    print(f"  Input folder : {INPUT_FOLDER}")
    print(f"  Files found  : {len(dcm_files)}")
    print()

    # ── Step 2: Run the batch pipeline (anonymise + mock upload) ───────────
    print("=" * 60)
    print("STEP 2 — Batch pipeline (anonymise + simulated upload)")
    print("=" * 60)
    report = process_folder(
        input_folder=INPUT_FOLDER,
        output_folder=OUTPUT_FOLDER,
    )
    print(report.summary())
    print()

    # ── Step 3: Intensity clustering on first scan ─────────────────────────
    print("=" * 60)
    print("STEP 3 — Intensity clustering (K-Means)")
    print("=" * 60)
    first_dcm = os.path.join(INPUT_FOLDER, dcm_files[0])
    ds = pydicom.dcmread(first_dcm)
    windowed, cluster_map, silhouette = cluster_scan(ds, n_clusters=3)
    print(f"  File         : {dcm_files[0]}")
    print(f"  Clusters     : 3")
    print(f"  Silhouette   : {silhouette:.3f}")
    print()

    # ── Step 4: Fleet-level QC ─────────────────────────────────────────────
    print("=" * 60)
    print("STEP 4 — Scanner QC (fleet-level outlier detection)")
    print("=" * 60)
    records, matrix, labels, qc_sil = run_qc(OUTPUT_FOLDER, n_clusters=2)
    print(f"  Scans analysed : {len(records)}")
    print(f"  QC silhouette  : {qc_sil:.3f}")
    for rec, lbl in zip(records, labels):
        flag = " ⚠ outlier?" if lbl != 0 else ""
        print(f"    {rec.filename}: group {lbl}  density={rec.avg_density:.1f}  contrast={rec.contrast:.1f}{flag}")
    print()

    # ── Step 5: Save visualisations ────────────────────────────────────────
    print("=" * 60)
    print("STEP 5 — Saving visualisations to reports/")
    print("=" * 60)

    fig = plot_raw_scan(ds, title=f"Raw scan — {dcm_files[0]}")
    path = os.path.join(REPORTS_FOLDER, "raw_scan.png")
    fig.savefig(path, dpi=100, bbox_inches="tight")
    print(f"  Saved: {path}")

    fig = plot_windowed_comparison(ds)
    path = os.path.join(REPORTS_FOLDER, "windowed_comparison.png")
    fig.savefig(path, dpi=100, bbox_inches="tight")
    print(f"  Saved: {path}")

    fig = plot_clustering(ds, n_clusters=3)
    path = os.path.join(REPORTS_FOLDER, "clustering.png")
    fig.savefig(path, dpi=100, bbox_inches="tight")
    print(f"  Saved: {path}")

    fig = plot_fleet_qc(records, labels, qc_sil)
    path = os.path.join(REPORTS_FOLDER, "fleet_qc.png")
    fig.savefig(path, dpi=100, bbox_inches="tight")
    print(f"  Saved: {path}")

    print()

    # ── Done ───────────────────────────────────────────────────────────────
    print("=" * 60)
    print("ALL PIPELINE STAGES COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print(f"  Processed files → {OUTPUT_FOLDER}")
    print(f"  Visualisations  → {REPORTS_FOLDER}")
    print()


if __name__ == "__main__":
    main()
