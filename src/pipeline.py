"""
pipeline.py - Batch DICOM processing orchestrator.

Reads every DICOM file from an input folder, de-identifies it using
src.anonymizer, and writes the cleaned file to an output folder.
A mock "upload" step with real exponential backoff demonstrates the
retry pattern that a production system would apply over an actual
network connection.

The upload itself is still simulated — no bytes leave the machine.
"""

import logging
import os
import random
import time
from dataclasses import dataclass, field
from typing import Optional

import pydicom

from src.anonymizer import anonymize_dataset
from src.config import CONFIG

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ProcessingResult:
    """Summary of a single file's processing outcome."""
    filename: str
    success: bool
    error: Optional[str] = None
    duration_s: float = 0.0


@dataclass
class PipelineReport:
    """Aggregate report produced at the end of a batch run."""
    total_files: int = 0
    processed: int = 0
    failed: int = 0
    elapsed_s: float = 0.0
    results: list[ProcessingResult] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            "=" * 50,
            "PIPELINE SUMMARY",
            "=" * 50,
            f"Total files found : {self.total_files}",
            f"Successfully processed: {self.processed}",
            f"Failed               : {self.failed}",
            f"Total time           : {self.elapsed_s:.2f}s",
        ]
        if self.failed > 0:
            lines.append("\nFailed files:")
            for r in self.results:
                if not r.success:
                    lines.append(f"  - {r.filename}: {r.error}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Mock upload with real exponential backoff
# ---------------------------------------------------------------------------

def mock_upload(
    filename: str,
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    failure_rate: float = 0.3,
) -> bool:
    """
    Simulate a network upload with exponential backoff + jitter.

    In production this would be replaced by an actual HTTP/S3 call.
    The backoff formula is:

        delay = min(base_delay * 2^attempt + uniform(0, 1), max_delay)

    This is the standard approach recommended by AWS, Google Cloud, and
    Azure for handling transient network errors.

    Parameters
    ----------
    filename : str
        Name of the file being uploaded (for log messages).
    max_attempts : int
        Maximum number of attempts before giving up.
    base_delay : float
        Starting delay in seconds.
    max_delay : float
        Maximum delay cap in seconds.
    failure_rate : float
        Probability that any single attempt fails (simulation only).

    Returns
    -------
    bool
        True if upload succeeded within the attempt budget.
    """
    for attempt in range(max_attempts):
        # Simulate a flaky network connection
        if random.random() < failure_rate:
            delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
            logger.warning(
                "Upload attempt %d/%d failed for %s. Retrying in %.2fs…",
                attempt + 1, max_attempts, filename, delay,
            )
            time.sleep(delay)
        else:
            logger.info("Upload succeeded for %s (attempt %d).", filename, attempt + 1)
            return True

    logger.error("All %d upload attempts failed for %s.", max_attempts, filename)
    return False


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------

def process_folder(
    input_folder: Optional[str] = None,
    output_folder: Optional[str] = None,
    max_files: Optional[int] = None,
    station_name: Optional[str] = None,
) -> PipelineReport:
    """
    Process all DICOM files in *input_folder* and write de-identified
    copies to *output_folder*.

    Parameters
    ----------
    input_folder : str, optional
        Source directory.  Defaults to config value.
    output_folder : str, optional
        Destination directory.  Defaults to config value.
    max_files : int, optional
        Cap on the number of files to process.  None = process all.
    station_name : str, optional
        Edge device identifier stamped on each file.

    Returns
    -------
    PipelineReport
        Summary of the batch run.
    """
    input_folder = input_folder or CONFIG["paths"]["input_folder"]
    output_folder = output_folder or CONFIG["paths"]["output_folder"]
    max_files = max_files if max_files is not None else CONFIG["pipeline"]["max_files"]
    station_name = station_name or CONFIG["anonymization"]["station_name"]

    retry_cfg = CONFIG["pipeline"]["retry"]
    max_attempts = retry_cfg["max_attempts"]
    base_delay = retry_cfg["base_delay"]
    max_delay = retry_cfg["max_delay"]

    report = PipelineReport()
    batch_start = time.time()

    if not os.path.isdir(input_folder):
        logger.error("Input folder not found: %s", input_folder)
        return report

    os.makedirs(output_folder, exist_ok=True)

    files = sorted(
        f for f in os.listdir(input_folder) if not f.startswith(".")
    )

    if max_files is not None:
        files = files[:max_files]

    report.total_files = len(files)
    logger.info("Starting pipeline: %d files to process.", report.total_files)

    for filename in files:
        file_start = time.time()
        result = ProcessingResult(filename=filename, success=False)

        try:
            full_path = os.path.join(input_folder, filename)
            ds = pydicom.dcmread(full_path)
            anonymize_dataset(ds, station_name=station_name)

            output_path = os.path.join(output_folder, f"Clean_{filename}")
            ds.save_as(output_path)

            uploaded = mock_upload(
                filename,
                max_attempts=max_attempts,
                base_delay=base_delay,
                max_delay=max_delay,
            )

            result.success = uploaded
            if uploaded:
                report.processed += 1
            else:
                result.error = "Upload failed after all retries"
                report.failed += 1

        except Exception as exc:
            result.error = str(exc)
            report.failed += 1
            logger.exception("Error processing %s: %s", filename, exc)

        result.duration_s = time.time() - file_start
        report.results.append(result)

    report.elapsed_s = time.time() - batch_start
    logger.info(report.summary())
    return report
