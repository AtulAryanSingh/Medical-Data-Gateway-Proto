"""
windowing.py - Hounsfield Unit conversion and window/level display.

WHY THIS MATTERS
----------------
Raw CT pixel values are stored as integers that encode tissue density on the
Hounsfield Unit (HU) scale.  The conversion formula is:

    HU = pixel_value * RescaleSlope + RescaleIntercept

Different tissues have characteristic HU ranges:
    Air          ≈ -1000 HU
    Fat          ≈ -100  HU
    Water        ≈    0  HU
    Soft tissue  ≈   40  HU
    Bone         ≈  400+ HU

Radiologists view CT scans through *windows* — a centre and width that
maps a clinically relevant HU range to the full 0-255 display range.
Showing the wrong window makes anatomy invisible.

References
----------
- DICOM PS3.3, attribute (0028,1050)/(0028,1051): WindowCenter/WindowWidth
- Radiopaedia HU reference: https://radiopaedia.org/articles/hounsfield-unit
"""

import logging
from typing import Optional

import numpy as np
from pydicom.dataset import Dataset

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Window presets (centre, width) commonly used in radiology
# ---------------------------------------------------------------------------
WINDOW_PRESETS: dict[str, tuple[float, float]] = {
    "brain": (40.0, 80.0),
    "bone": (400.0, 1800.0),
    "lung": (-600.0, 1500.0),
    "soft_tissue": (50.0, 400.0),
}


def to_hounsfield(
    pixel_array: np.ndarray,
    slope: float = 1.0,
    intercept: float = 0.0,
) -> np.ndarray:
    """
    Convert raw stored pixel values to Hounsfield Units.

    Parameters
    ----------
    pixel_array : np.ndarray
        Raw pixel data as returned by ``ds.pixel_array``.
    slope : float
        RescaleSlope from the DICOM header (default 1.0).
    intercept : float
        RescaleIntercept from the DICOM header (default 0.0).

    Returns
    -------
    np.ndarray
        Float array of HU values, same shape as *pixel_array*.
    """
    return pixel_array.astype(np.float64) * slope + intercept


def apply_window(
    hu_array: np.ndarray,
    center: float,
    width: float,
) -> np.ndarray:
    """
    Apply window/level to a HU array and return values normalised to [0, 1].

    Pixels below (center - width/2) map to 0.
    Pixels above (center + width/2) map to 1.
    Everything in between is linearly scaled.

    Parameters
    ----------
    hu_array : np.ndarray
        Array of Hounsfield Unit values.
    center : float
        Window centre (level) in HU.
    width : float
        Window width in HU.

    Returns
    -------
    np.ndarray
        Float array in [0, 1], same shape as *hu_array*.
    """
    lower = center - width / 2.0
    upper = center + width / 2.0
    if width <= 0:
        raise ValueError(
            f"Window width must be > 0, got width={width}."
        )
    windowed = np.clip(hu_array, lower, upper)
    # Normalise to [0, 1]
    return (windowed - lower) / (upper - lower)


def window_from_dataset(
    ds: Dataset,
    preset: Optional[str] = None,
    center: Optional[float] = None,
    width: Optional[float] = None,
) -> np.ndarray:
    """
    Extract pixel data from a DICOM Dataset, convert to HU, and window it.

    Priority for window parameters:
    1. Explicit *center* / *width* arguments.
    2. Named *preset* from WINDOW_PRESETS.
    3. Values embedded in the DICOM header (WindowCenter / WindowWidth).
    4. Fall back to soft-tissue preset if nothing else is available.

    Parameters
    ----------
    ds : Dataset
        Loaded pydicom Dataset.
    preset : str, optional
        One of "brain", "bone", "lung", "soft_tissue".
    center : float, optional
        Manual window centre override.
    width : float, optional
        Manual window width override.

    Returns
    -------
    np.ndarray
        Windowed image normalised to [0, 1].
    """
    # Read rescale parameters with safe defaults
    slope = float(getattr(ds, "RescaleSlope", 1.0))
    intercept = float(getattr(ds, "RescaleIntercept", 0.0))

    hu = to_hounsfield(ds.pixel_array, slope=slope, intercept=intercept)

    # Determine window centre/width
    if center is not None and width is not None:
        wc, ww = center, width
    elif preset is not None:
        if preset not in WINDOW_PRESETS:
            raise ValueError(
                f"Unknown preset '{preset}'. "
                f"Choose from: {list(WINDOW_PRESETS.keys())}"
            )
        wc, ww = WINDOW_PRESETS[preset]
    else:
        # Try to read from DICOM header
        dicom_wc = getattr(ds, "WindowCenter", None)
        dicom_ww = getattr(ds, "WindowWidth", None)
        if dicom_wc is not None and dicom_ww is not None:
            # WindowCenter/Width can be a MultiValue list; take the first element
            wc = float(dicom_wc) if not hasattr(dicom_wc, "__iter__") else float(list(dicom_wc)[0])
            ww = float(dicom_ww) if not hasattr(dicom_ww, "__iter__") else float(list(dicom_ww)[0])
        else:
            logger.warning("No window parameters found; defaulting to soft_tissue preset.")
            wc, ww = WINDOW_PRESETS["soft_tissue"]

    logger.debug("Applying window: centre=%.1f, width=%.1f", wc, ww)
    return apply_window(hu, center=wc, width=ww)
