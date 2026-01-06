# DICOM Secure Gateway Prototype

## Overview
A Python-based learning prototype designed to handle the **safe retrieval and processing of medical imaging data** (DICOM).
I built this to understand the engineering challenges behind compliant medical data transfer—specifically regarding **GDPR anonymization** and **Edge-to-Cloud traceability**.

## Core Functions
* **Metadata Parsing:** separating header tags from pixel data.
* **Automated Anonymization:** Stripping PII (Patient Name/ID) to simulate a GDPR-compliant gateway.
* **Origin Tracking:** Injecting "StationName" tags (e.g., `REMOTE_MOBILE_CLINIC_01`) to trace files coming from decentralized sources.

## Tech Stack
* **Language:** Python 3.x
* **Library:** `pydicom`
##USAGE:
python inspector.py /path/to/dcm_folder
python anonymizer.py /path/to/dcm_folder /path/to/output_folder

## Purpose
This project explores the "Edge Gateway" architecture used in modern telemedicine, ensuring data is clean and traceable before it reaches central cloud storage.
