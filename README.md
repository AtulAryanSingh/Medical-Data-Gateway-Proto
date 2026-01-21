# MedSendX Edge-Native Pipeline (Prototype)

## Overview
This project is a lightweight, edge-native DICOM processing pipeline designed for mobile medical units (e.g., Mammography Trucks) operating in low-connectivity environments.

It addresses four critical challenges:
1.  **Data Privacy:** GDPR-compliant anonymization at the source.
2.  **Bandwidth Constraints:** "Smart Retry" logic for unstable 4G/LTE connections.
3.  **Clinical Triage:** On-device AI segmentation (Bone vs. Tissue) to prioritize urgent scans.
4.  **Fleet Analytics:** Population-level data mining to detect scanner faults or outliers.

## Architecture
**Truck (Edge)** --> **Gateway (Python Script)** --> **Cloud (AWS S3/PACS)**

## Key Modules

### 1. `batch_processor.py` (The Resilience Layer)
- **Function:** Simulates the ingestion of raw DICOM files.
- **Features:**
  - Implements exponential backoff for network drops.
  - Automatically tags files with `StationName: REMOTE_MOBILE_CLINIC_01`.
  - Prevents data loss during signal interruptions.

### 2. `density_plot.py` (The Clinical AI Layer)
- **Target:** The Radiologist (Single Patient View).
- **Function:** Performs unsupervised K-Means clustering on pixel density.
- **Output:** Generates a segmented visualization (Air vs. Soft Tissue vs. Bone) to aid rapid review.

### 3. `miner.py` (The Business Intelligence Layer)
- **Target:** The Fleet Manager (Population View).
- **Function:** Aggregates meta-features (Average Density vs. Contrast) across all processed patients.
- **Algorithm:** Uses K-Means to detect outliers (e.g., "Cluster B").
- **Use Case:** Automated Quality Control (QC) to identify broken scanners or calibration issues in specific mobile units.

### 4. `anonymizer.py` (The Privacy Layer)
- **Function:** Strips PII (PatientID, PatientName) before the file leaves the truck.
- **Compliance:** Aligns with basic GDPR data minimization principles.

## Future Roadmap (Production)
- **Containerization:** Dockerize the pipeline for OS-agnostic deployment on truck hardware.
- **Storage:** Replace local mock storage with AWS S3 encrypted buckets.
- **Integration:** Connect output directly to MedSendX Web Dashboard via REST API.

---
* Author: Atul Aryan
* Status: MVP 