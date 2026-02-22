"""
visualization.py - Consolidated matplotlib plotting helpers.

All plot functions follow a consistent style and return the Figure so
callers can save or display it as needed.
"""

import logging
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from pydicom.dataset import Dataset

from src.windowing import WINDOW_PRESETS, window_from_dataset
from src.clustering import cluster_scan
from src.scanner_qc import ScanFeatures

logger = logging.getLogger(__name__)

# Consistent figure style across all plots
plt.rcParams.update({"figure.dpi": 100, "axes.titlesize": 11})


def plot_raw_scan(ds: Dataset, title: str = "CT Slice") -> plt.Figure:
    """
    Display raw pixel data from a DICOM dataset.

    Parameters
    ----------
    ds : Dataset
        Loaded pydicom Dataset.
    title : str
        Plot title.

    Returns
    -------
    plt.Figure
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(ds.pixel_array, cmap="gray")
    ax.set_title(title)
    ax.axis("off")
    return fig


def plot_windowed_comparison(ds: Dataset) -> plt.Figure:
    """
    Show the same CT slice through each standard window preset side by side.

    Parameters
    ----------
    ds : Dataset
        Loaded pydicom Dataset.

    Returns
    -------
    plt.Figure
    """
    presets = list(WINDOW_PRESETS.keys())
    fig, axes = plt.subplots(1, len(presets), figsize=(4 * len(presets), 4))

    for ax, preset in zip(axes, presets):
        windowed = window_from_dataset(ds, preset=preset)
        center, width = WINDOW_PRESETS[preset]
        ax.imshow(windowed, cmap="gray")
        ax.set_title(f"{preset.replace('_', ' ').title()}\n(C={center}, W={width})")
        ax.axis("off")

    fig.suptitle("Windowed Views (same slice)", y=1.02)
    fig.tight_layout()
    return fig


def plot_clustering(ds: Dataset, n_clusters: int = 3) -> plt.Figure:
    """
    Display original windowed scan alongside K-Means cluster map.

    Parameters
    ----------
    ds : Dataset
        Loaded pydicom Dataset.
    n_clusters : int
        Number of intensity clusters.

    Returns
    -------
    plt.Figure
    """
    windowed, cluster_map, silhouette = cluster_scan(ds, n_clusters=n_clusters)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.imshow(windowed, cmap="gray")
    station = getattr(ds, "StationName", "Unknown")
    ax1.set_title(f"Windowed Scan\n(Source: {station})")
    ax1.axis("off")

    ax2.imshow(cluster_map, cmap="plasma")
    ax2.set_title(
        f"Intensity Clustering (K-Means, k={n_clusters})\n"
        f"Silhouette score: {silhouette:.3f}"
    )
    ax2.axis("off")

    fig.tight_layout()
    return fig


def plot_fleet_qc(
    records: list[ScanFeatures],
    labels: np.ndarray,
    silhouette: float,
) -> plt.Figure:
    """
    Scatter plot of fleet scans coloured by QC cluster assignment.

    X-axis: average tissue density (mean pixel value)
    Y-axis: image contrast (pixel std dev)

    Parameters
    ----------
    records : list[ScanFeatures]
        Per-file feature records (filenames used for point labels).
    labels : np.ndarray
        Cluster label per scan.
    silhouette : float
        Silhouette score to display in the title.

    Returns
    -------
    plt.Figure
    """
    X = np.array([[r.avg_density, r.contrast] for r in records])
    unique_labels = np.unique(labels)
    colors = plt.cm.tab10(np.linspace(0, 0.5, len(unique_labels)))

    fig, ax = plt.subplots(figsize=(10, 6))

    for label, color in zip(unique_labels, colors):
        mask = labels == label
        ax.scatter(
            X[mask, 0], X[mask, 1],
            s=100, color=color, label=f"Group {label}",
        )

    for i, rec in enumerate(records):
        ax.annotate(
            rec.filename,
            (X[i, 0], X[i, 1]),
            fontsize=8,
            alpha=0.7,
            xytext=(5, 5),
            textcoords="offset points",
        )

    ax.set_title(
        f"Scanner QC — Fleet Overview\n"
        f"Silhouette score: {silhouette:.3f} "
        f"(closer to 1 = well-separated groups)"
    )
    ax.set_xlabel("Average Tissue Density (mean pixel value)")
    ax.set_ylabel("Image Contrast (pixel std dev)")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)
    fig.tight_layout()
    return fig
