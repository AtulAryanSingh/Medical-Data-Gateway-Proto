"""Basic smoke tests for src/pipeline.py."""

import os
import tempfile

import numpy as np
import pydicom
import pytest
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian

from src.pipeline import mock_upload, process_folder, PipelineReport


def _write_dicom(path: str, patient_name: str = "Test^Patient") -> None:
    """Write a minimal valid DICOM file to *path*."""
    file_meta = pydicom.Dataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.UID("1.2.840.10008.5.1.4.1.1.2")
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = FileDataset(path, {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.PatientName = patient_name
    ds.PatientID = "99999"
    ds.Modality = "CT"
    ds.Rows = 4
    ds.Columns = 4
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelRepresentation = 0
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelData = np.zeros((4, 4), dtype=np.uint16).tobytes()
    ds.save_as(path)


class TestMockUpload:
    def test_upload_eventually_succeeds(self):
        """With failure_rate=0 the upload always succeeds on the first try."""
        result = mock_upload("test.dcm", failure_rate=0.0)
        assert result is True

    def test_upload_fails_when_always_failing(self):
        """With failure_rate=1 all attempts fail."""
        result = mock_upload(
            "test.dcm",
            failure_rate=1.0,
            max_attempts=3,
            base_delay=0.0,
            max_delay=0.0,
        )
        assert result is False


class TestProcessFolder:
    def test_missing_folder_returns_empty_report(self):
        report = process_folder(input_folder="/nonexistent/path", output_folder="/tmp/out")
        assert isinstance(report, PipelineReport)
        assert report.total_files == 0

    def test_processes_dicom_files(self, tmp_path):
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()

        _write_dicom(str(input_dir / "scan1.dcm"), "Test^Alice")
        _write_dicom(str(input_dir / "scan2.dcm"), "Test^Bob")

        report = process_folder(
            input_folder=str(input_dir),
            output_folder=str(output_dir),
            max_files=None,
        )

        assert report.total_files == 2
        # Output files should exist (prefixed with "Clean_")
        output_files = list(output_dir.iterdir())
        assert len(output_files) == 2

    def test_max_files_limits_processing(self, tmp_path):
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()

        for i in range(5):
            _write_dicom(str(input_dir / f"scan{i}.dcm"))

        report = process_folder(
            input_folder=str(input_dir),
            output_folder=str(output_dir),
            max_files=2,
        )

        assert report.total_files == 2

    def test_output_files_are_anonymized(self, tmp_path):
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()

        _write_dicom(str(input_dir / "patient.dcm"), "Doe^Jane")

        process_folder(
            input_folder=str(input_dir),
            output_folder=str(output_dir),
        )

        output_files = list(output_dir.iterdir())
        assert len(output_files) == 1

        cleaned = pydicom.dcmread(str(output_files[0]))
        assert not hasattr(cleaned, "PatientName") or str(cleaned.PatientName) != "Doe^Jane"
        assert cleaned.PatientIdentityRemoved == "YES"


class TestPipelineCounters:
    def test_upload_failure_increments_failed_not_processed(self, tmp_path):
        """A file saved but not uploaded must count as failed, not processed."""
        from unittest.mock import patch

        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        _write_dicom(str(input_dir / "scan.dcm"))

        # Force all upload attempts to fail
        with patch("src.pipeline.mock_upload", return_value=False):
            report = process_folder(
                input_folder=str(input_dir),
                output_folder=str(output_dir),
            )

        assert report.total_files == 1
        assert report.processed == 0, "Upload-failed file must not count as successfully processed"
        assert report.failed == 1, "Upload-failed file must count in the failed counter"
