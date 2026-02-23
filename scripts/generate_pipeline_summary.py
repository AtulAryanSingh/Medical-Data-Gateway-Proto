"""
generate_pipeline_summary.py - Write a Markdown summary to GitHub Actions.

When ``GITHUB_STEP_SUMMARY`` is set (i.e. inside a GitHub Actions workflow),
this script writes pipeline results, metrics and inline visualisation
thumbnails so that everything is visible directly in the Actions run page.

When run locally (no ``GITHUB_STEP_SUMMARY``), the summary is printed to
stdout instead.

Usage
-----
    python scripts/generate_pipeline_summary.py
"""

import base64
import glob
import logging
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

import pydicom

from src.config import CONFIG
from src.clustering import cluster_scan
from src.scanner_qc import run_qc

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
logger = logging.getLogger(__name__)

INPUT_FOLDER = os.path.join(_REPO_ROOT, CONFIG["paths"]["input_folder"])
OUTPUT_FOLDER = os.path.join(_REPO_ROOT, CONFIG["paths"]["output_folder"])
REPORTS_FOLDER = os.path.join(_REPO_ROOT, CONFIG["paths"]["reports_folder"])


def _image_to_base64(path: str) -> str:
    """Return a base64-encoded data URI for an image file."""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{data}"


def _build_summary() -> str:
    """Build a Markdown summary of the pipeline run."""
    lines: list[str] = []
    lines.append("# 🏥 Medical Data Gateway — Pipeline Results\n")

    # ── Input / Output counts ──────────────────────────────────────────────
    input_files = sorted(f for f in os.listdir(INPUT_FOLDER) if not f.startswith("."))
    output_files = sorted(f for f in os.listdir(OUTPUT_FOLDER) if not f.startswith("."))

    lines.append("## 📂 Data Summary\n")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Input files (data/raw) | {len(input_files)} |")
    lines.append(f"| Output files (data/processed) | {len(output_files)} |")
    lines.append("")

    # ── Clustering metrics ─────────────────────────────────────────────────
    lines.append("## 🔬 Intensity Clustering (K-Means, k=3)\n")
    if not input_files:
        lines.append("_No input files found — skipping clustering._\n")
        silhouette = float("nan")
    else:
        first_file = os.path.join(INPUT_FOLDER, input_files[0])
        ds = pydicom.dcmread(first_file)
        _, _, silhouette = cluster_scan(ds, n_clusters=3)

    if input_files:
        lines.append(f"| Metric | Value | Interpretation |")
        lines.append(f"|--------|-------|----------------|")
        if silhouette > 0.7:
            interp = "✅ Excellent — clusters are well-separated"
        elif silhouette > 0.5:
            interp = "✅ Good — reasonable cluster separation"
        elif silhouette > 0.25:
            interp = "⚠️ Fair — clusters overlap moderately"
        else:
            interp = "❌ Poor — clusters are not well-defined"
        lines.append(f"| Silhouette score | {silhouette:.3f} | {interp} |")
        lines.append("")

    # ── Fleet QC metrics ───────────────────────────────────────────────────
    lines.append("## 🛡️ Fleet-Level Scanner QC (K-Means, k=2)\n")
    records, _, labels, qc_sil = run_qc(OUTPUT_FOLDER, n_clusters=2)

    lines.append(f"| Metric | Value | Interpretation |")
    lines.append(f"|--------|-------|----------------|")
    if qc_sil > 0.7:
        qc_interp = "✅ Excellent — scanners are clearly grouped"
    elif qc_sil > 0.5:
        qc_interp = "✅ Good — scanner groups are distinguishable"
    elif qc_sil > 0.25:
        qc_interp = "⚠️ Fair — some overlap between scanner groups"
    else:
        qc_interp = "❌ Poor — scanners are not clearly grouped"
    lines.append(f"| Silhouette score | {qc_sil:.3f} | {qc_interp} |")
    lines.append(f"| Scans analysed | {len(records)} | |")
    lines.append("")

    lines.append("### Per-Scan Breakdown\n")
    lines.append("| File | Group | Avg Density | Contrast | Status |")
    lines.append("|------|-------|-------------|----------|--------|")
    for rec, lbl in zip(records, labels):
        status = "⚠️ Outlier?" if lbl != 0 else "✅ Normal"
        lines.append(
            f"| {rec.filename} | {lbl} | {rec.avg_density:.1f} "
            f"| {rec.contrast:.1f} | {status} |"
        )
    lines.append("")

    # ── Visualisations ─────────────────────────────────────────────────────
    report_images = sorted(glob.glob(os.path.join(REPORTS_FOLDER, "*.png")))
    if report_images:
        lines.append("## 📊 Visualisations\n")
        lines.append(
            "> Download the **pipeline-reports** artifact for full-resolution images.\n"
        )
        for img_path in report_images:
            name = os.path.basename(img_path).replace("_", " ").replace(".png", "").title()
            data_uri = _image_to_base64(img_path)
            lines.append(f"### {name}\n")
            lines.append(f"![{name}]({data_uri})\n")

    # ── ML Evaluation Notes ────────────────────────────────────────────────
    lines.append("## 🧠 ML Technique Evaluation\n")
    lines.append("| Aspect | Current Approach | Notes |")
    lines.append("|--------|-----------------|-------|")
    lines.append(
        "| Clustering algorithm | K-Means | "
        "Simple, fast, works well for intensity-based grouping |"
    )
    lines.append(
        "| Cluster validation | Silhouette score | "
        "Standard metric; scores above 0.5 indicate good separation |"
    )
    lines.append(
        "| Feature extraction | Mean, Std, Max | "
        "Minimal but effective for fleet-level QC |"
    )
    lines.append(
        "| Spatial awareness | None | "
        "Pixels treated independently — consider DBSCAN or "
        "connected-component analysis for spatial clustering |"
    )
    lines.append("")

    lines.append("### Potential Upgrades\n")
    lines.append(
        "- **DBSCAN / HDBSCAN**: Density-based clustering that can find "
        "arbitrarily shaped regions and does not require choosing k up front.\n"
        "- **Gaussian Mixture Models**: Soft clustering that provides "
        "probability estimates per tissue type.\n"
        "- **U-Net / deep learning segmentation**: For production-quality "
        "tissue segmentation, a trained neural network would outperform "
        "unsupervised methods — but requires labelled training data.\n"
        "- **Isolation Forest for QC**: Better suited for outlier detection "
        "than K-Means when the number of anomalous scans is small.\n"
    )

    return "\n".join(lines)


def main() -> None:
    summary = _build_summary()

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a") as f:
            f.write(summary)
        logger.info("Summary written to GITHUB_STEP_SUMMARY")
    else:
        print(summary)


if __name__ == "__main__":
    main()
