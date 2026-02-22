"""
scanner_qc.py - Fleet-level Scanner Quality Control.

Extracts simple image statistics from a folder of processed DICOM files
and uses K-Means clustering to surface scans that differ markedly from
the rest of the fleet.  Unusual scans may indicate:

- Scanner calibration drift
- Incorrect reconstruction parameters
- Data corruption during transfer

This is a first-pass anomaly signal, not a diagnostic conclusion.
A radiologist or biomedical engineer should investigate flagged scans.

LIMITATIONS
-----------
- Features are simple global statistics (mean, std, max).  They do not
  capture spatial structure or acquisition protocol differences.
- K-Means cluster labels have no inherent meaning — the algorithm does
  not know which cluster is "normal".  Visual inspection is required.
- Clusters are chosen with k=2 by default; use silhouette scores to
  validate the choice for a given fleet dataset.
"""

import logging
import os
from dataclasses import dataclass

import numpy as np
import pydicom
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


@dataclass
class ScanFeatures:
    """Image-level statistics extracted from one DICOM slice."""
    filename: str
    avg_density: float    # Mean pixel value — proxy for overall tissue density
    contrast: float       # Std dev — proxy for image sharpness / dynamic range
    peak_value: float     # Max pixel value — proxy for peak bone/contrast density


def extract_features(folder: str) -> tuple[list[ScanFeatures], np.ndarray]:
    """
    Walk *folder* and extract three scalar features from each DICOM file.

    Parameters
    ----------
    folder : str
        Directory containing processed DICOM files.

    Returns
    -------
    feature_records : list[ScanFeatures]
        Per-file feature structs (includes filenames for labelling).
    feature_matrix : np.ndarray
        Shape (n_files, 3) float array ready for clustering.
        Columns: [avg_density, contrast, peak_value].
    """
    if not os.path.isdir(folder):
        logger.error("Folder not found: %s", folder)
        return [], np.empty((0, 3))

    files = sorted(f for f in os.listdir(folder) if not f.startswith("."))
    records: list[ScanFeatures] = []

    for fname in files:
        full_path = os.path.join(folder, fname)
        try:
            ds = pydicom.dcmread(full_path, force=True)
            pixels = ds.pixel_array.astype(np.float64)
            rec = ScanFeatures(
                filename=fname,
                avg_density=float(np.mean(pixels)),
                contrast=float(np.std(pixels)),
                peak_value=float(np.max(pixels)),
            )
            records.append(rec)
            logger.debug(
                "Extracted features from %s: density=%.1f, contrast=%.1f, peak=%.1f",
                fname, rec.avg_density, rec.contrast, rec.peak_value,
            )
        except Exception as exc:
            logger.warning("Could not process %s: %s", fname, exc)

    if not records:
        return [], np.empty((0, 3))

    matrix = np.array(
        [[r.avg_density, r.contrast, r.peak_value] for r in records],
        dtype=np.float64,
    )
    return records, matrix


def run_qc(
    folder: str,
    n_clusters: int = 2,
    random_state: int = 42,
) -> tuple[list[ScanFeatures], np.ndarray, np.ndarray, float]:
    """
    Extract features and cluster the fleet to surface potential outliers.

    Clustering is performed on standardised features (zero mean, unit
    variance) so that the three features contribute equally regardless
    of their absolute scale.

    Parameters
    ----------
    folder : str
        Directory containing processed DICOM files.
    n_clusters : int
        Number of groups for K-Means.  k=2 is a sensible starting point
        for outlier detection (one "typical" group, one "unusual" group).
    random_state : int
        Random seed for reproducibility.

    Returns
    -------
    records : list[ScanFeatures]
        Feature records (one per file).
    feature_matrix : np.ndarray
        Raw (un-scaled) feature matrix, shape (n, 3).
    labels : np.ndarray
        Cluster label per scan, shape (n,).
    silhouette : float
        Silhouette score for the solution (NaN if fewer than 2 clusters).
    """
    records, matrix = extract_features(folder)

    if len(records) < 2:
        logger.warning("Not enough files to cluster (need ≥ 2, got %d).", len(records))
        labels = np.zeros(len(records), dtype=int)
        return records, matrix, labels, float("nan")

    # Standardise: important because avg_density and peak_value have very
    # different scales, which would otherwise dominate the distance metric.
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(matrix)

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    score = silhouette_score(X_scaled, labels) if (n_clusters > 1 and len(records) > n_clusters) else float("nan")
    logger.info(
        "QC clustering: %d files, k=%d, silhouette=%.3f",
        len(records), n_clusters, score,
    )
    return records, matrix, labels, score
