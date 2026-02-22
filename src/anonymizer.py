"""
anonymizer.py - DICOM de-identification module.

Implements a subset of the DICOM PS3.15 Annex E Basic Application Level
Confidentiality Profile.  This removes or replaces 25+ PHI (Protected Health
Information) tags so that scans can leave the mobile unit without exposing
patient identity.

IMPORTANT LIMITATIONS
---------------------
- Does NOT handle burned-in annotations (text overlaid on pixel data).
- Does NOT remap UIDs (StudyInstanceUID etc.) to unlinkable values.
- Has NOT been audited for formal HIPAA/GDPR compliance.
- Use as a starting point, not a production compliance solution.

References
----------
- DICOM PS3.15 Annex E: https://dicom.nema.org/medical/dicom/current/output/html/part15.html
- pydicom de-identification guide: https://pydicom.github.io/pydicom/dev/guides/deidentification.html
"""

import logging
from typing import Optional

import pydicom
from pydicom.dataset import Dataset

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tag lists — driven by configuration, not scattered through code
# ---------------------------------------------------------------------------

# Tags to remove entirely (set to empty string or delete).
# Based on DICOM PS3.15 Annex E Table E.1-1 (subset).
TAGS_TO_REMOVE: list[str] = [
    "PatientName",
    "PatientID",
    "PatientBirthDate",
    "PatientSex",
    "PatientAge",
    "PatientAddress",
    "PatientTelephoneNumbers",
    "OtherPatientIDs",
    "OtherPatientNames",
    "OtherPatientIDsSequence",
    "ReferringPhysicianName",
    "ReferringPhysicianAddress",
    "ReferringPhysicianTelephoneNumbers",
    "InstitutionName",
    "InstitutionAddress",
    "InstitutionalDepartmentName",
    "PerformingPhysicianName",
    "OperatorsName",
    "NameOfPhysiciansReadingStudy",
    "RequestingPhysician",
    "ScheduledPerformingPhysicianName",
    "AccessionNumber",
    "StudyID",
    "DeviceSerialNumber",
    "RequestedProcedureID",
]

# Tags to replace with a neutral dummy value rather than delete.
# Dates are shifted to 1900-01-01 so the DICOM remains syntactically valid.
TAGS_TO_REPLACE: dict[str, str] = {
    "StudyDate": "19000101",
    "SeriesDate": "19000101",
    "AcquisitionDate": "19000101",
    "ContentDate": "19000101",
    "StudyTime": "000000",
    "SeriesTime": "000000",
    "AcquisitionTime": "000000",
    "ContentTime": "000000",
}


def anonymize_dataset(
    ds: Dataset,
    station_name: str = "REMOTE_MOBILE_01",
) -> Dataset:
    """
    Remove or replace PHI tags in a pydicom Dataset **in place**.

    The function:
    1. Deletes every tag listed in TAGS_TO_REMOVE (silently skips missing ones).
    2. Replaces every tag listed in TAGS_TO_REPLACE with its dummy value.
    3. Removes all private (vendor-specific) tags via pydicom's built-in helper.
    4. Stamps the dataset with DICOM-standard de-identification markers.
    5. Sets StationName so the receiving server knows the scan origin.

    Parameters
    ----------
    ds : Dataset
        The pydicom Dataset to de-identify.  Modified in place.
    station_name : str
        Identifier for the mobile unit / edge device.

    Returns
    -------
    Dataset
        The same Dataset object, now de-identified.
    """
    # Step 1 — Remove PHI tags
    for tag_name in TAGS_TO_REMOVE:
        if hasattr(ds, tag_name):
            delattr(ds, tag_name)
            logger.debug("Removed tag: %s", tag_name)

    # Step 2 — Replace date/time tags with neutral values
    for tag_name, dummy_value in TAGS_TO_REPLACE.items():
        if hasattr(ds, tag_name):
            setattr(ds, tag_name, dummy_value)
            logger.debug("Replaced tag %s → %s", tag_name, dummy_value)

    # Step 3 — Remove all private (odd-group) tags.
    # Private tags are vendor extensions and may contain PHI we cannot
    # enumerate in advance, so blanket removal is the safe approach.
    ds.remove_private_tags()

    # Step 4 — DICOM-standard de-identification markers
    # PatientIdentityRemoved (0012,0062): "YES" signals downstream systems
    # that this dataset has been de-identified.
    ds.PatientIdentityRemoved = "YES"

    # DeidentificationMethod (0012,0063): free-text description (VR=LO, max 64 chars).
    ds.DeidentificationMethod = (
        "DICOM PS3.15 Annex E subset. No UID remap, no pixel scrub."
    )

    # Step 5 — Stamp with the edge device identifier
    ds.StationName = station_name

    return ds


def anonymize_file(
    input_path: str,
    output_path: str,
    station_name: str = "REMOTE_MOBILE_01",
) -> None:
    """
    Load a DICOM file, de-identify it, and save to a new path.

    Parameters
    ----------
    input_path : str
        Path to the source DICOM file.
    output_path : str
        Destination path for the anonymized file.
    station_name : str
        Identifier stamped as StationName.

    Raises
    ------
    FileNotFoundError
        If *input_path* does not exist.
    pydicom.errors.InvalidDicomError
        If the file cannot be read as DICOM.
    """
    ds = pydicom.dcmread(input_path)
    anonymize_dataset(ds, station_name=station_name)
    ds.save_as(output_path)
    logger.info("Anonymized %s → %s", input_path, output_path)
