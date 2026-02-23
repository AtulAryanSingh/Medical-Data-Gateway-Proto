"""
audit_phi.py - Check DICOM files for Protected Health Information (PHI).

Scans a folder of DICOM files and reports which PHI-related tags are
present and what values they contain.  Use this to decide whether data
needs to be anonymized before being stored in a public repository.

Usage
-----
    python scripts/audit_phi.py                          # scans data/raw/
    python scripts/audit_phi.py path/to/dicom/folder     # custom folder
"""

import logging
import os
import sys
from collections import Counter

import pydicom

# Ensure repo root is on sys.path
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)

from src.anonymizer import TAGS_TO_REMOVE, TAGS_TO_REPLACE  # noqa: E402
from src.config import CONFIG  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
logger = logging.getLogger(__name__)

# Values that are clearly placeholder / dummy — not real PHI
_KNOWN_DUMMY_VALUES = {
    "NAME^NONE", "NONE", "ANONYMOUS", "ANON", "NOID", "00000",
    "SN000000", "", "N/A",
}


def audit_folder(folder: str) -> dict:
    """
    Scan all DICOM files in *folder* and report PHI tag presence.

    Returns
    -------
    dict
        Audit results including per-tag value counts, private tag info,
        and an overall risk assessment.
    """
    if not os.path.isdir(folder):
        logger.error("Folder not found: %s", folder)
        return {}

    files = sorted(f for f in os.listdir(folder) if not f.startswith("."))
    if not files:
        logger.warning("No files found in %s", folder)
        return {}

    all_phi_tags = TAGS_TO_REMOVE + list(TAGS_TO_REPLACE.keys())
    tag_values: dict[str, Counter] = {t: Counter() for t in all_phi_tags}
    private_tag_counts: list[int] = []
    total_files = 0
    failed_files: list[str] = []

    for fname in files:
        full_path = os.path.join(folder, fname)
        try:
            ds = pydicom.dcmread(full_path, force=True)
            total_files += 1
            for tag in all_phi_tags:
                val = str(getattr(ds, tag, "")).strip()
                if val:
                    tag_values[tag][val] += 1
            private_tags = [elem for elem in ds if elem.tag.is_private]
            private_tag_counts.append(len(private_tags))
        except Exception as exc:
            failed_files.append(f"{fname}: {exc}")

    # Determine risk level
    real_phi_found = []
    for tag in TAGS_TO_REMOVE:
        for val in tag_values[tag]:
            if val.upper() not in {v.upper() for v in _KNOWN_DUMMY_VALUES}:
                real_phi_found.append((tag, val, tag_values[tag][val]))

    has_private = any(c > 0 for c in private_tag_counts)

    return {
        "folder": folder,
        "total_files": total_files,
        "failed_files": failed_files,
        "tag_values": tag_values,
        "private_tag_counts": private_tag_counts,
        "real_phi_found": real_phi_found,
        "has_private_tags": has_private,
    }


def print_report(results: dict) -> None:
    """Print a human-readable PHI audit report."""
    if not results:
        return

    print("=" * 60)
    print("PHI AUDIT REPORT")
    print("=" * 60)
    print(f"  Folder        : {results['folder']}")
    print(f"  Files scanned : {results['total_files']}")
    if results["failed_files"]:
        print(f"  Failed to read: {len(results['failed_files'])}")
    print()

    print("── Identity Tags (TAGS_TO_REMOVE) ──")
    for tag in TAGS_TO_REMOVE:
        values = results["tag_values"][tag]
        if values:
            for val, count in values.most_common():
                is_dummy = val.upper() in {v.upper() for v in _KNOWN_DUMMY_VALUES}
                status = "✓ dummy" if is_dummy else "⚠ REAL PHI?"
                print(f"  {tag}: \"{val}\" ({count} files) — {status}")
        else:
            print(f"  {tag}: (absent) — ✓ safe")

    print()
    print("── Date/Time Tags (TAGS_TO_REPLACE) ──")
    for tag in list(TAGS_TO_REPLACE.keys()):
        values = results["tag_values"][tag]
        if values:
            for val, count in values.most_common(3):
                print(f"  {tag}: \"{val}\" ({count} files)")
        else:
            print(f"  {tag}: (absent)")

    print()
    pc = results["private_tag_counts"]
    if pc:
        print(f"── Private/Vendor Tags: min={min(pc)}, max={max(pc)} per file ──")
    else:
        print("── Private/Vendor Tags: none ──")

    print()
    print("=" * 60)
    print("VERDICT")
    print("=" * 60)

    if results["real_phi_found"]:
        print("  ⚠  REAL PHI DETECTED — do NOT store as-is in a public repo!")
        print("  Run the anonymization pipeline first:")
        print("    python scripts/run_full_pipeline.py")
        print()
        print("  Tags with real PHI:")
        for tag, val, count in results["real_phi_found"]:
            print(f"    {tag}: \"{val}\" ({count} files)")
    else:
        print("  ✓  No real patient identity found.")
        print("     PatientName/ID contain only dummy placeholder values.")
        if results["has_private_tags"]:
            print()
            print("  ⚠  Private/vendor tags ARE present.")
            print("     These are unlikely to contain PHI in a public dataset,")
            print("     but running the pipeline will strip them to be safe:")
            print("       python scripts/run_full_pipeline.py")
        print()
        print("  RECOMMENDATION: The raw data appears safe for a public repo,")
        print("  but running the pipeline will remove dates and private tags")
        print("  for best practice.  Store anonymized output in data/processed/.")
    print()


def main() -> None:
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    else:
        folder = os.path.join(_REPO_ROOT, CONFIG["paths"]["input_folder"])

    results = audit_folder(folder)
    print_report(results)


if __name__ == "__main__":
    main()
