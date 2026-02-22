"""Tests for src/windowing.py."""

import numpy as np
import pytest
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian

from src.windowing import to_hounsfield, apply_window, window_from_dataset, WINDOW_PRESETS


def _make_ds_with_pixels(pixels: np.ndarray, slope: float = 1.0, intercept: float = 0.0) -> Dataset:
    """Create a minimal pydicom Dataset with pixel_array support."""
    file_meta = pydicom.Dataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.UID("1.2.840.10008.5.1.4.1.1.2")
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = FileDataset(filename_or_obj=None, dataset={}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.Rows, ds.Columns = pixels.shape
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelRepresentation = 0
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelData = pixels.astype(np.uint16).tobytes()
    ds.RescaleSlope = slope
    ds.RescaleIntercept = intercept
    return ds


class TestHounsfield:
    def test_known_conversion(self):
        pixels = np.array([[0, 100], [200, 1000]], dtype=np.float64)
        hu = to_hounsfield(pixels, slope=1.0, intercept=-1024.0)
        expected = pixels - 1024.0
        np.testing.assert_array_almost_equal(hu, expected)

    def test_default_slope_intercept(self):
        pixels = np.array([[5, 10]], dtype=np.float64)
        hu = to_hounsfield(pixels)
        np.testing.assert_array_equal(hu, pixels)


class TestWindowing:
    def test_output_in_zero_one_range(self):
        hu = np.linspace(-1000, 2000, 100)
        windowed = apply_window(hu, center=40, width=80)
        assert windowed.min() >= 0.0
        assert windowed.max() <= 1.0

    def test_clip_below_lower_is_zero(self):
        hu = np.array([-2000.0])
        windowed = apply_window(hu, center=40, width=80)
        assert windowed[0] == 0.0

    def test_clip_above_upper_is_one(self):
        hu = np.array([5000.0])
        windowed = apply_window(hu, center=40, width=80)
        assert windowed[0] == 1.0

    def test_center_maps_to_half(self):
        hu = np.array([40.0])
        windowed = apply_window(hu, center=40, width=80)
        assert abs(windowed[0] - 0.5) < 1e-9


class TestWindowFromDataset:
    def test_preset_applied(self):
        pixels = np.zeros((4, 4), dtype=np.uint16)
        ds = _make_ds_with_pixels(pixels, slope=1.0, intercept=-1024.0)
        result = window_from_dataset(ds, preset="brain")
        assert result.shape == (4, 4)
        assert result.min() >= 0.0
        assert result.max() <= 1.0

    def test_missing_rescale_uses_defaults(self):
        pixels = np.zeros((4, 4), dtype=np.uint16)
        ds = _make_ds_with_pixels(pixels)
        # Remove rescale tags to test defaults
        if hasattr(ds, "RescaleSlope"):
            delattr(ds, "RescaleSlope")
        if hasattr(ds, "RescaleIntercept"):
            delattr(ds, "RescaleIntercept")
        result = window_from_dataset(ds, preset="soft_tissue")
        assert result.shape == (4, 4)

    def test_unknown_preset_raises(self):
        pixels = np.zeros((4, 4), dtype=np.uint16)
        ds = _make_ds_with_pixels(pixels)
        with pytest.raises(ValueError, match="Unknown preset"):
            window_from_dataset(ds, preset="invalid_preset")

    def test_all_presets_work(self):
        pixels = np.arange(16, dtype=np.uint16).reshape(4, 4)
        ds = _make_ds_with_pixels(pixels, slope=1.0, intercept=-1024.0)
        for preset in WINDOW_PRESETS:
            result = window_from_dataset(ds, preset=preset)
            assert result.min() >= 0.0
            assert result.max() <= 1.0
