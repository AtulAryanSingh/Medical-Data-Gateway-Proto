"""Tests for src/anonymizer.py."""

import pytest
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian
from pydicom.sequence import Sequence
import pydicom.uid

from src.anonymizer import anonymize_dataset, TAGS_TO_REMOVE, TAGS_TO_REPLACE


def _make_dataset(**kwargs) -> Dataset:
    """Build a minimal in-memory DICOM dataset for testing."""
    file_meta = pydicom.Dataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.UID("1.2.840.10008.5.1.4.1.1.2")
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = FileDataset(filename_or_obj=None, dataset={}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.is_implicit_VR = False
    ds.is_little_endian = True

    # Required PHI tags
    ds.PatientName = "Doe^John"
    ds.PatientID = "12345"
    ds.PatientBirthDate = "19800101"
    ds.PatientSex = "M"
    ds.StudyDate = "20230601"
    ds.ContentDate = "20230601"
    ds.StudyTime = "120000"
    ds.ContentTime = "120000"
    ds.AccessionNumber = "ACC001"
    ds.StudyID = "STUDY001"
    ds.InstitutionName = "General Hospital"
    ds.ReferringPhysicianName = "Smith^Jane"
    ds.Modality = "CT"  # non-PHI tag — should be preserved

    for key, value in kwargs.items():
        setattr(ds, key, value)

    return ds


class TestTagRemoval:
    def test_phi_tags_removed(self):
        ds = _make_dataset()
        anonymize_dataset(ds)
        for tag in ["PatientName", "PatientID", "PatientBirthDate",
                     "InstitutionName", "ReferringPhysicianName", "AccessionNumber"]:
            assert not hasattr(ds, tag), f"{tag} should have been removed"

    def test_non_phi_tags_preserved(self):
        ds = _make_dataset()
        anonymize_dataset(ds)
        assert ds.Modality == "CT", "Non-PHI tag Modality should be preserved"

    def test_patient_identity_removed_flag(self):
        ds = _make_dataset()
        anonymize_dataset(ds)
        assert ds.PatientIdentityRemoved == "YES"

    def test_deidentification_method_set(self):
        ds = _make_dataset()
        anonymize_dataset(ds)
        assert hasattr(ds, "DeidentificationMethod")
        assert len(ds.DeidentificationMethod) > 0

    def test_station_name_stamped(self):
        ds = _make_dataset()
        anonymize_dataset(ds, station_name="TEST_UNIT")
        assert ds.StationName == "TEST_UNIT"

    def test_dates_replaced_not_removed(self):
        ds = _make_dataset()
        anonymize_dataset(ds)
        for tag in TAGS_TO_REPLACE:
            if hasattr(ds, tag):
                assert getattr(ds, tag) == TAGS_TO_REPLACE[tag], \
                    f"{tag} should be replaced with dummy value"

    def test_private_tags_removed(self):
        ds = _make_dataset()
        # Add a private tag (odd group)
        ds.add_new([0x0009, 0x0010], "LO", "PrivateData")
        anonymize_dataset(ds)
        private_tags = [elem for elem in ds if elem.tag.is_private]
        assert len(private_tags) == 0, "All private tags should be removed"

    def test_missing_optional_tags_no_crash(self):
        """Anonymizer must not crash when optional PHI tags are absent."""
        ds = _make_dataset()
        # Remove some tags before calling anonymize
        for attr in ["PatientAge", "PatientAddress", "OtherPatientIDs"]:
            if hasattr(ds, attr):
                delattr(ds, attr)
        # Should not raise
        anonymize_dataset(ds)

    def test_all_tags_to_remove_covered(self):
        """Every tag in TAGS_TO_REMOVE should be absent after anonymization."""
        ds = _make_dataset()
        # Set as many removal-list tags as possible
        for tag in TAGS_TO_REMOVE:
            try:
                setattr(ds, tag, "TEST_VALUE")
            except Exception:
                pass  # Some tags may not accept string values
        anonymize_dataset(ds)
        for tag in TAGS_TO_REMOVE:
            assert not hasattr(ds, tag), f"{tag} still present after anonymization"
