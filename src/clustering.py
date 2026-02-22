"""
clustering.py - Intensity-based clustering for DICOM scan visualisation.

This module applies K-Means clustering to the pixel intensity values of
a single CT slice.  The goal is **visualisation**, not diagnosis.

WHY K-MEANS HERE?
-----------------
K-Means groups pixels by HU-like intensity value into k clusters.
Because CT tissue types occupy distinct HU ranges (air ≈ -1000,
soft tissue ≈ 0–80, bone ≈ 400+), k=3 clusters often roughly correspond
to those tissue types — but this is a statistical observation, not a
clinical segmentation.  Do NOT use these labels for diagnosis.

LIMITATIONS
-----------
- Clusters are unlabelled: the algorithm does not know what tissue is what.
- No spatial context: neighbouring pixels are treated independently.
- Sensitive to noise and reconstruction kernel.
- Not validated against radiologist ground truth.

References
----------
- Scikit-learn KMeans: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
- Silhouette score for k selection: https://scikit-learn.org/stable/modules/clustering.html#silhouette-coefficient
"""

import logging
from typing import Optional

import numpy as np
from pydicom.dataset import Dataset
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from src.windowing import window_from_dataset

logger = logging.getLogger(__name__)


def cluster_scan(
    ds: Dataset,
    n_clusters: int = 3,
    window_preset: str = "soft_tissue",
    random_state: int = 42,
) -> tuple[np.ndarray, np.ndarray, float]:
    """
    Apply K-Means intensity clustering to a single CT slice.

    Pixel data is first converted to Hounsfield Units and windowed so that
    the clustering operates on clinically relevant intensity values rather
    than raw stored integers (which can vary by scanner).

    Parameters
    ----------
    ds : Dataset
        Loaded pydicom Dataset for a single slice.
    n_clusters : int
        Number of intensity clusters (default 3).
    window_preset : str
        Windowing preset to apply before clustering.
    random_state : int
        Random seed for reproducible results.

    Returns
    -------
    windowed : np.ndarray
        The windowed image array (values in [0, 1]).
    cluster_map : np.ndarray
        Integer array (same shape as image) with cluster label per pixel.
    silhouette : float
        Silhouette score for the clustering solution.
        Ranges from -1 (poor) to +1 (excellent).  A score > 0.5 suggests
        the clusters are well-separated in intensity space.
    """
    windowed = window_from_dataset(ds, preset=window_preset)

    # Flatten to a column vector for KMeans
    X = windowed.reshape(-1, 1)

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X)

    cluster_map = labels.reshape(windowed.shape)

    # Silhouette score quantifies cluster separation.
    # We subsample for speed — exact score not required for QC use.
    sample_size = min(len(X), 5000)
    rng = np.random.default_rng(random_state)
    idx = rng.choice(len(X), size=sample_size, replace=False)
    score = silhouette_score(X[idx], labels[idx])

    logger.info(
        "Clustering complete: k=%d, silhouette=%.3f", n_clusters, score
    )
    return windowed, cluster_map, score
