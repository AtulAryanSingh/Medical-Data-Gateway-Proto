# Medical Data Engineering Toolkit 🏥 🐍

## Overview
A comprehensive Python-based toolkit for handling **DICOM medical imaging data**.
This project simulates the core logic of a **Medical Images Gateway (MIG)**, focusing on GDPR compliance, batch processing, and pixel-level analysis.

## 🛠 Modules Built

### 1. `anonymizer.py` (The Prototype)
* **Function:** Single-file processor.
* **Logic:** strips PII (Patient Name/ID) and injects "Edge" origin tags (e.g., `REMOTE_MOBILE_CLINIC_01`).
* **Tech:** `pydicom`, `os`.

### 2. `batch_processor.py` (The Engine)
* **Function:** High-volume automated processing.
* **Logic:** Iterates through full CT scan volumes, applying anonymization rules to hundreds of slices in seconds.
* **Key Feature:** Robust error handling and dynamic folder creation.

### 3. `viewer.py` (The Eyes)
* **Function:** Diagnostic visualization.
* **Logic:** Renders raw DICOM pixel data into human-readable X-Ray images using a bone-specific colormap.
* **Tech:** `matplotlib`.

### 4. `density_plot.py` (The Analyst)
* **Function:** Tissue density analysis.
* **Logic:** Flattens 2D pixel arrays to generate histograms of Hounsfield Units (radiodensity), distinguishing between air, soft tissue, and bone.

## 🚀 How to Run
1.  **Install dependencies:**
    ```bash
    pip install pydicom matplotlib
    ```
2.  **Run the batch processor:**
    ```bash
    python batch_processor.py
    ```
3.  **Visualize the results:**
    ```bash
    python viewer.py
    ```

## 🧠 Key Learnings
* **DICOM Structure:** Understanding Header (Metadata) vs. Pixel Data.
* **Data Hygiene:** The importance of "cleaning" data at the Edge before Cloud transfer.
* **Visualization:** Translating raw integer arrays into diagnostic imagery.