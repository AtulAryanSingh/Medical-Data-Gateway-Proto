# MedSendX Edge-Native Pipeline (Prototype)

## Overview
This project is a lightweight, edge-native DICOM processing pipeline designed for mobile medical units (e.g., Mammography Trucks) operating in low-connectivity environments.

It addresses four critical challenges:
1.  **Data Privacy:** GDPR-compliant anonymization at the source.
2.  **Bandwidth Constraints:** "Smart Retry" logic for unstable 4G/LTE connections.
3.  **Clinical Triage:** On-device AI segmentation (Bone vs. Tissue) to prioritize urgent scans.
4.  **Fleet Analytics:** Population-level data mining to detect scanner faults or outliers.

## What Problem Does This Solve?

Mobile medical units — like mammography trucks or remote CT vans — generate DICOM scan files in the field, far from hospital infrastructure. Sending raw patient data over an unreliable 4G connection raises three immediate problems:

1. **Privacy risk:** Raw DICOM files contain the patient's name, ID, and other personal identifiers. Transmitting them unmodified raises GDPR compliance concerns without proper safeguards.
2. **Network fragility:** A dropped connection mid-upload corrupts the transfer and loses the scan.
3. **No triage:** A radiologist back at HQ has no way to know which scans are urgent without downloading and reviewing every one.

This pipeline runs entirely **on the truck** (the "edge") to solve all three problems before a single byte leaves the vehicle.

---

## Pipeline: End-to-End Data Flow

```
[Scanner]
    |
    | Raw DICOM file (contains patient PII)
    v
[anonymizer.py / batch_processor.py]  <-- STEP 1: Anonymize & Tag
    |
    | Strips PatientName, PatientID
    | Adds StationName = "REMOTE_MOBILE_CLINIC_01"
    | Saves to: batch_anonymized/
    v
[Mock Upload with Exponential Backoff] <-- STEP 2: Resilient Transmission
    |
    | Simulates 4G drop + retry logic
    | In production: uploads to AWS S3 / PACS
    v
[density_plot.py]                      <-- STEP 3: Clinical AI (per patient)
    |
    | K-Means on pixel values (3 clusters)
    | Labels: Air | Soft Tissue | Bone
    | Output: highlighted_scan.png
    v
[miner.py]                             <-- STEP 4: Fleet BI (across all patients)
    |
    | Extracts meta-features: Avg Density, Contrast, Peak Bone
    | K-Means across patients (2 clusters)
    | Cluster B = outlier scans (broken scanner? calibration fault?)
    | Output: mining_report.png
    v
[Cloud / Dashboard]                    <-- FUTURE: REST API to MedSendX Web
```

---

## Architecture

```
Truck (Edge)  -->  Gateway (Python Script)  -->  Cloud (AWS S3 / PACS)
```

The Python scripts act as the **Gateway layer** — they run locally on the truck's on-board computer, process files before transmission, and hand off clean, anonymized data to the cloud.

---

## Key Modules

### 1. `anonymizer.py` (The Privacy Layer — Single File)
- **Input:** `test_scan.dcm` (a raw DICOM file from the scanner)
- **What it does:**
  - Reads the DICOM metadata envelope (PatientName, PatientID, Modality, etc.)
  - Overwrites PII: `PatientName = "ANONYMOUS"`, `PatientID = "00000"`
  - Adds a provenance tag: `StationName = "REMOTE_MOBILE_CLINIC_01"` so the server knows which truck sent it
  - Saves the clean file as `anonymized_scan.dcm`
- **Compliance:** Aligns with GDPR data minimization — direct patient identifiers (PatientName, PatientID) are stripped before any data leaves the truck. The `StationName` tag is retained as an audit-trail metadata field to identify the source unit.

### 2. `batch_processor.py` (The Resilience Layer — Many Files)
- **Input:** A folder of raw DICOM files (`2_skull_ct/DICOM/`)
- **What it does:**
  - Loops over every file in the folder (demo: first 5)
  - Applies the same anonymization as `anonymizer.py` to each file
  - Calls `mock_upload()` after each file — simulates a 4G upload with a 30% chance of a connection drop
  - On drop: waits and retries (exponential backoff pattern) — **no data is lost**
  - Saves clean files to `batch_anonymized/`
- **Why it matters:** A real mobile unit may lose signal mid-batch. This layer ensures every file is eventually delivered.

### 3. `viewer.py` (The Inspection Tool)
- **Input:** A specific file from `batch_anonymized/`
- **What it does:** Reads the anonymized DICOM and prints its metadata (PatientName, PatientID, image dimensions) to confirm anonymization worked, then displays the raw CT slice.
- **Role in pipeline:** Manual QC / verification step after `batch_processor.py`

### 4. `inspector.py` (The Raw File Explorer)
- **Input:** `test_scan.dcm` (the original file)
- **What it does:** Prints DICOM metadata (Patient ID, Modality, Study Date) and displays the raw pixel array. Useful for exploring a new scanner's output format before integrating it into the pipeline.

### 5. `density_plot.py` (The Clinical AI Layer — Per Patient)
- **Target user:** The Radiologist
- **Input:** First file found in `batch_anonymized/`
- **What it does:**
  - Loads the pixel array (a 2D grid of intensity values)
  - Reshapes it into a 1D list of pixel intensities and runs **K-Means (k=3)**
  - Each pixel gets assigned to one of 3 clusters: **Air** (dark) | **Soft Tissue** (mid) | **Bone** (bright)
  - Displays a side-by-side visualization: original grayscale scan vs. AI-coloured segmentation
  - Saves to `highlighted_scan.png`
- **Clinical value:** Lets a radiologist instantly see bone vs. soft tissue without manual review. Can be used to triage scans by severity.

### 6. `miner.py` (The Business Intelligence Layer — Across All Patients)
- **Target user:** The Fleet Manager
- **Input:** All files in `batch_anonymized/`
- **What it does:**
  - For every patient file, extracts 3 numerical "meta-features":
    - **Average Density** — overall brightness of the scan (proxy for tissue density)
    - **Contrast** — standard deviation of pixel values (proxy for image sharpness/quality)
    - **Peak Bone Density** — maximum pixel value (proxy for bone intensity)
  - Runs **K-Means (k=2)** across all patients using Density and Contrast as axes
  - Plots a scatter chart: Cluster A (normal scans) vs. Cluster B (outliers)
  - Saves to `mining_report.png`
- **Operational value:** If Cluster B consistently contains scans from one truck, that truck's scanner may be miscalibrated or faulty — triggering a maintenance alert without anyone manually reviewing images.

---

## How to Run

### Prerequisites
```bash
pip install -r requirements.txt
```

### Step-by-step

1. **Explore a raw scan** (optional):
   ```bash
   python inspector.py        # needs test_scan.dcm in the working directory
   ```

2. **Anonymize a single file** (optional):
   ```bash
   python anonymizer.py       # needs test_scan.dcm; produces anonymized_scan.dcm
   ```

3. **Batch-anonymize and simulate upload**:
   ```bash
   python batch_processor.py  # needs 2_skull_ct/DICOM/ folder; produces batch_anonymized/
   ```

4. **Inspect the cleaned output** (optional):
   ```bash
   python viewer.py           # reads from batch_anonymized/
   ```

5. **Run clinical AI segmentation** (per patient):
   ```bash
   python density_plot.py     # reads from batch_anonymized/; produces highlighted_scan.png
   ```

6. **Run fleet analytics** (across all patients):
   ```bash
   python miner.py            # reads from batch_anonymized/; produces mining_report.png
   ```

---

## Future Roadmap (Production)
- **Containerization:** Dockerize the pipeline for OS-agnostic deployment on truck hardware.
- **Storage:** Replace local mock storage with AWS S3 encrypted buckets.
- **Integration:** Connect output directly to MedSendX Web Dashboard via REST API.
- **Real-time streaming:** Replace batch processing with a file-watcher that triggers the pipeline the moment a scan is saved by the scanner.
- **Model upgrade:** Replace K-Means segmentation with a trained CNN (e.g., U-Net) for higher clinical accuracy.

---
* Author: Atul Aryan
* Status: MVP