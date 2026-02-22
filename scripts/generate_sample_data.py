"""
generate_sample_data.py - Create synthetic DICOM files for end-to-end demo.

Writes 10 small DICOM files to data/raw/ so you can run the full pipeline
immediately without real patient data.

Usage
-----
    python scripts/generate_sample_data.py

After running, try:
    python -c "from src.pipeline import process_folder; r = process_folder(); print(r.summary())"

Or open the demo notebook:
    jupyter notebook notebooks/demo_walkthrough.ipynb
"""

import os
import sys

import numpy as np
import pydicom
from pydicom.dataset import FileDataset
from pydicom.uid import ExplicitVRLittleEndian

# Make sure repo root is on the path when run as a script
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

from src.config import CONFIG  # noqa: E402 — import after path fix

OUTPUT_FOLDER = os.path.join(_REPO_ROOT, CONFIG["paths"]["input_folder"])


# ---------------------------------------------------------------------------
# Synthetic scan profiles — varied to make the QC scatter plot interesting
# ---------------------------------------------------------------------------
_SCAN_PROFILES = [
    # (filename_stem, mean_value, std_dev,  note)
    ("scan_01", 1050, 180, "normal head CT"),
    ("scan_02", 1020, 175, "normal head CT"),
    ("scan_03", 1080, 190, "normal head CT"),
    ("scan_04", 1010, 165, "normal head CT"),
    ("scan_05", 1060, 185, "normal head CT"),
    ("scan_06", 1030, 170, "normal head CT"),
    ("scan_07", 1070, 195, "normal head CT"),
    # Two outlier scans — lower mean, much lower contrast, simulating a
    # miscalibrated or low-dose scanner
    ("scan_08", 400,  45, "low-dose / possible miscalibration"),
    ("scan_09", 380,  40, "low-dose / possible miscalibration"),
    # One high-contrast outlier — simulating a bone phantom / QC scan
    ("scan_10", 2200, 600, "high-contrast bone phantom"),
]


def _make_dicom(
    path: str,
    patient_name: str,
    patient_id: str,
    mean_val: float,
    std_val: float,
    size: int = 128,
    seed: int = 42,
) -> None:
    """
    Write a single synthetic DICOM file.

    Pixel values are drawn from a Normal distribution, then a bright square
    is added to simulate a bone / high-density region.  RescaleSlope=1 and
    RescaleIntercept=-1024 bring the stored integers into HU range.
    """
    rng = np.random.default_rng(seed)

    # Generate realistic-looking pixel data
    pixels = rng.normal(mean_val, std_val, size=(size, size))
    pixels = pixels.clip(0, 4095).astype(np.uint16)

    # Add a bright square to simulate bone
    sq = size // 4
    pixels[sq : sq * 2, sq : sq * 2] = min(int(mean_val * 1.8), 4095)

    file_meta = pydicom.Dataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.UID("1.2.840.10008.5.1.4.1.1.2")
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = FileDataset(path, {}, file_meta=file_meta, preamble=b"\0" * 128)

    # --- PHI tags (will be removed by the anonymizer) ---
    ds.PatientName = patient_name
    ds.PatientID = patient_id
    ds.PatientBirthDate = "19800101"
    ds.PatientSex = "M"
    ds.AccessionNumber = f"ACC{patient_id}"
    ds.StudyID = f"ST{patient_id}"
    ds.InstitutionName = "City General Hospital"
    ds.ReferringPhysicianName = "Smith^Jane"

    # --- Acquisition metadata ---
    ds.StudyDate = "20230601"
    ds.ContentDate = "20230601"
    ds.StudyTime = "120000"
    ds.ContentTime = "120000"
    ds.Modality = "CT"

    # --- Rescale parameters for HU conversion ---
    ds.RescaleSlope = 1.0
    ds.RescaleIntercept = -1024.0
    ds.WindowCenter = 40.0
    ds.WindowWidth = 400.0

    # --- Pixel data ---
    ds.Rows = size
    ds.Columns = size
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelRepresentation = 0
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelData = pixels.tobytes()

    ds.save_as(path)


def generate(output_folder: str = OUTPUT_FOLDER) -> None:
    """Generate all synthetic DICOM files into *output_folder*."""
    os.makedirs(output_folder, exist_ok=True)

    print(f"Writing {len(_SCAN_PROFILES)} synthetic DICOM files to: {output_folder}")
    print("-" * 60)

    for i, (stem, mean_val, std_val, note) in enumerate(_SCAN_PROFILES, start=1):
        filename = f"{stem}.dcm"
        path = os.path.join(output_folder, filename)
        _make_dicom(
            path=path,
            patient_name=f"Synthetic^Patient{i:02d}",
            patient_id=f"{i:05d}",
            mean_val=mean_val,
            std_val=std_val,
            seed=42 + i,
        )
        print(f"  [{i:02d}/{len(_SCAN_PROFILES)}] {filename}  ({note})")

    print("-" * 60)
    print(f"Done.  Run the pipeline with:")
    print(f"  python -c \"from src.pipeline import process_folder; r = process_folder(); print(r.summary())\"")
    print(f"Or open the demo notebook:")
    print(f"  jupyter notebook notebooks/demo_walkthrough.ipynb")


if __name__ == "__main__":
    generate()
