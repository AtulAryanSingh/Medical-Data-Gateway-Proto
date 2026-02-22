"""Tests for src/scanner_qc.py."""

import math
import os

import numpy as np
import pydicom
import pytest
from pydicom.dataset import FileDataset
from pydicom.uid import ExplicitVRLittleEndian

from src.scanner_qc import ScanFeatures, extract_features, run_qc


def _write_dicom(path: str, mean_value: int = 100) -> None:
    """Write a minimal DICOM file with a uniform pixel array."""
    file_meta = pydicom.Dataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.UID("1.2.840.10008.5.1.4.1.1.2")
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = FileDataset(path, {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.Modality = "CT"
    ds.Rows = 4
    ds.Columns = 4
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelRepresentation = 0
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    pixels = np.full((4, 4), mean_value, dtype=np.uint16)
    ds.PixelData = pixels.tobytes()
    ds.save_as(path)


class TestExtractFeatures:
    def test_missing_folder_returns_empty(self, tmp_path):
        records, matrix = extract_features(str(tmp_path / "nonexistent"))
        assert records == []
        assert matrix.shape == (0, 3)

    def test_extracts_three_features(self, tmp_path):
        _write_dicom(str(tmp_path / "scan.dcm"), mean_value=200)
        records, matrix = extract_features(str(tmp_path))
        assert len(records) == 1
        assert matrix.shape == (1, 3)
        assert records[0].avg_density == pytest.approx(200.0)

    def test_feature_matrix_rows_match_records(self, tmp_path):
        for i in range(3):
            _write_dicom(str(tmp_path / f"scan{i}.dcm"), mean_value=100 * (i + 1))
        records, matrix = extract_features(str(tmp_path))
        assert len(records) == matrix.shape[0]


class TestRunQC:
    def test_single_file_returns_nan_silhouette(self, tmp_path):
        _write_dicom(str(tmp_path / "scan.dcm"))
        records, matrix, labels, score = run_qc(str(tmp_path))
        assert len(records) == 1
        assert math.isnan(score)

    def test_two_files_with_k2_returns_nan_not_crash(self, tmp_path):
        """With n_samples == n_clusters, silhouette_score is undefined and must not crash."""
        _write_dicom(str(tmp_path / "scan1.dcm"), mean_value=100)
        _write_dicom(str(tmp_path / "scan2.dcm"), mean_value=900)
        records, matrix, labels, score = run_qc(str(tmp_path), n_clusters=2)
        # silhouette_score requires n_samples > n_clusters, so score must be NaN
        assert math.isnan(score)

    def test_three_files_with_k2_gives_valid_silhouette(self, tmp_path):
        """With n_samples > n_clusters, silhouette_score must be a real number."""
        for i, v in enumerate([50, 500, 1000]):
            _write_dicom(str(tmp_path / f"scan{i}.dcm"), mean_value=v)
        records, matrix, labels, score = run_qc(str(tmp_path), n_clusters=2)
        assert not math.isnan(score)
        assert -1.0 <= score <= 1.0

    def test_labels_shape_matches_records(self, tmp_path):
        for i in range(4):
            _write_dicom(str(tmp_path / f"scan{i}.dcm"), mean_value=100 * (i + 1))
        records, matrix, labels, score = run_qc(str(tmp_path), n_clusters=2)
        assert len(labels) == len(records)
