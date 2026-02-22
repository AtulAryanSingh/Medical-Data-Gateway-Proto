# Medical Data Gateway — DICOM Processing Prototype

A learning prototype for processing DICOM medical imaging files from mobile
clinical units.  Built to demonstrate core concepts in medical data engineering:
de-identification, image processing, and quality-control analytics.

---

## Scope & Limitations

This is a **prototype**, not a production system.

| What it does | What it does NOT do |
|---|---|
| Removes 25+ PHI tags (DICOM PS3.15 Annex E subset) | Handle burned-in pixel annotations |
| Replaces sensitive dates with dummy values | Remap UIDs to unlinkable values |
| Removes all private/vendor tags | Pass a formal HIPAA/GDPR compliance audit |
| Simulates upload with exponential backoff | Transfer any data over a real network |
| Visualises CT intensity clusters (K-Means) | Perform clinical segmentation or diagnosis |
| Flags statistically unusual scans for QC review | Replace radiologist interpretation |

---

## Architecture

```
data/raw/          →  src/pipeline.py  →  data/processed/
                          │
                    src/anonymizer.py      (de-identification)
                    src/windowing.py       (HU conversion)
                    src/clustering.py      (intensity visualisation)
                    src/scanner_qc.py      (fleet-level QC)
                    src/visualization.py   (all plotting)
```

The pipeline is intentionally linear and easy to trace — no frameworks,
no message queues, no microservices.

---

## Modules

| Module | What it does |
|---|---|
| `src/config.py` | Loads `config.yaml`; provides defaults if the file is missing |
| `src/anonymizer.py` | Removes / replaces PHI tags; removes private tags; stamps de-identification markers |
| `src/windowing.py` | Converts raw pixels to Hounsfield Units; applies clinical window presets |
| `src/pipeline.py` | Batch orchestrator; calls anonymizer; simulates upload with exponential backoff |
| `src/clustering.py` | K-Means intensity clustering on a single slice; reports silhouette score |
| `src/scanner_qc.py` | Extracts per-scan statistics; clusters the fleet; surfaces potential outliers |
| `src/visualization.py` | All matplotlib plotting in one place |

---

## Getting Started

### Clone the repository (first time)
```bash
git clone https://github.com/AtulAryanSingh/Medical-Data-Gateway-Proto.git
cd Medical-Data-Gateway-Proto
```

### Pull the latest changes (existing clone)
If you already have a local copy and want to download the newest updates:
```bash
cd Medical-Data-Gateway-Proto
git pull origin main
```

### Alternative: download as ZIP
If you don't use Git, click the green **Code** button on the
[repository page](https://github.com/AtulAryanSingh/Medical-Data-Gateway-Proto)
and choose **Download ZIP**. Extract it and replace your old folder.

---

## How to Run

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the demo notebook
```bash
jupyter notebook notebooks/demo_walkthrough.ipynb
```

### Run the batch pipeline
```python
from src.pipeline import process_folder
report = process_folder(input_folder="data/raw", output_folder="data/processed")
print(report.summary())
```

### Run tests
```bash
pytest tests/
```

---

## Configuration

Edit `config.yaml` to change paths, retry parameters, or the number of
clusters without touching source code:

```yaml
paths:
  input_folder: "data/raw"
  output_folder: "data/processed"

pipeline:
  max_files: null        # null = process all files
  retry:
    max_attempts: 5
    base_delay: 1.0      # seconds
    max_delay: 30.0

clustering:
  n_clusters: 3
```

---

## Future Improvements (Production Readiness)

1. **UID remapping** — replace StudyInstanceUID / SeriesInstanceUID / SOPInstanceUID
   with newly generated UIDs so datasets cannot be re-linked.
2. **Pixel scrubbing** — detect and redact burned-in annotations using OCR or a
   trained detector.
3. **Real upload** — replace `mock_upload` with authenticated S3 / DICOM-web calls.
4. **Formal compliance audit** — engage a HIPAA/GDPR specialist to review the
   de-identification pipeline.
5. **Containerisation** — Dockerize for OS-agnostic deployment on edge hardware.
6. **Validated segmentation** — replace K-Means with a model trained and validated
   on annotated ground-truth data.

---

## References

- [DICOM PS3.15 Annex E — Attribute Confidentiality Profiles](https://dicom.nema.org/medical/dicom/current/output/html/part15.html)
- [pydicom de-identification guide](https://pydicom.github.io/pydicom/dev/guides/deidentification.html)
- [Radiopaedia — Hounsfield Units](https://radiopaedia.org/articles/hounsfield-unit)

---

*Author: Atul Aryan | Status: Learning Prototype*
