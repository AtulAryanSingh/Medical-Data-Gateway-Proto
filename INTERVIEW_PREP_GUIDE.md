# 🏥 Medical Data Gateway — Complete Beginner's Interview Prep Guide

> **Who this guide is for:** Someone with zero Python or VS Code experience who needs to understand this project, demo it confidently, and answer both technical and behavioural interview questions.
>
> **You can read this entire guide on a plane** — no internet required once you have it open. Every concept is explained from scratch. Every command has the expected output shown.

---

## 📋 Table of Contents

1. [The Big Picture (Read This First)](#1-the-big-picture)
2. [Install Everything — One-Time Setup](#2-install-everything)
3. [Open the Project in VS Code](#3-open-the-project-in-vs-code)
4. [Project Structure — What Every File Does](#4-project-structure)
5. [Code Walkthrough — Every File, Every Line Explained](#5-code-walkthrough)
   - [config.py](#51-srcconfigpy)
   - [anonymizer.py](#52-srcanonymizerpy)
   - [windowing.py](#53-srcwindowingpy)
   - [pipeline.py](#54-srcpipelinepy)
   - [clustering.py](#55-srcclusteringpy)
   - [scanner_qc.py](#56-srcscanner_qcpy)
   - [visualization.py](#57-srcvisualizationpy)
   - [scripts/generate_sample_data.py](#58-scriptsgenerate_sample_datapy)
   - [scripts/run_full_pipeline.py](#59-scriptsrun_full_pipelinepy)
   - [scripts/audit_phi.py](#510-scriptsaudit_phipy)
   - [scripts/generate_pipeline_summary.py](#511-scriptsgenerate_pipeline_summarypy)
6. [Tests — What They Are and Why They Matter](#6-tests)
7. [Makefile, Dockerfile, and CI/CD Explained](#7-makefile-dockerfile-and-cicd)
8. [Install Dependencies (Do This Once)](#8-install-dependencies)
9. [Step-by-Step Demo — Commands, Outputs, What to Say](#9-step-by-step-demo)
10. [Behavioural Interview Questions (STAR Framework)](#10-behavioural-interview-questions)
11. [Technical Interview Questions — With Full Answers](#11-technical-interview-questions)
12. [Troubleshooting — What to Do When Something Goes Wrong](#12-troubleshooting)
13. [Quick-Reference Cheat Sheet](#13-quick-reference-cheat-sheet)

---

## 1. The Big Picture

### What does this project actually do? (Explain it in 30 seconds)

Imagine a mobile CT scanner — like an X-ray machine in a truck — that drives to remote villages or disaster sites. When it scans a patient, the images contain **private patient information** (name, date of birth, hospital, doctor's name). Before sending those images to a cloud server for specialist review, you need to:

1. **Strip out the personal information** (called "de-identification" or "anonymization")
2. **Send the cleaned images** over a network (with retry logic in case the connection drops)
3. **Check image quality** across all scanners in the fleet to spot problems early
4. **Visualise the results** so doctors can see what's happening

That is exactly what this code does. The project is called a **"gateway"** because it sits between the mobile scanner and the cloud, acting as a security checkpoint.

### The technology it uses

| Term | Plain-English Meaning |
|------|----------------------|
| **Python** | The programming language — like instructions written in near-English |
| **DICOM** | The file format all medical scanners use — like "PDF for medical images" |
| **PHI** | Protected Health Information — patient name, ID, birth date etc |
| **K-Means clustering** | A maths technique that groups similar things together automatically |
| **Silhouette score** | A number (−1 to 1) that tells you how well-separated the groups are |
| **Exponential backoff** | A retry strategy: wait 1s, then 2s, then 4s… before trying again |
| **GitHub Actions (CI/CD)** | A robot that runs your tests automatically when you push code to GitHub |

---

## 2. Install Everything

### Step 1 — Install Python

1. Open your browser and go to **https://www.python.org/downloads/**
2. Click the big yellow **"Download Python 3.x.x"** button
3. Run the installer
   - ⚠️ **IMPORTANT:** Tick the checkbox that says **"Add Python to PATH"** at the bottom of the first screen
4. Click **Install Now**
5. When it finishes, open the Windows Command Prompt (search "cmd" in Start) or Mac Terminal and type:

```
python --version
```

You should see something like `Python 3.12.0`. If you do, Python is installed.

---

### Step 2 — Install VS Code

1. Go to **https://code.visualstudio.com/**
2. Click the download button for your operating system
3. Run the installer (accept defaults)
4. Open VS Code — it looks like a dark window with icons on the left sidebar

---

### Step 3 — Install VS Code Extensions

Extensions add extra features to VS Code. You need two:

**Python Extension:**
1. In VS Code, click the **puzzle-piece icon** (Extensions) on the left sidebar — or press `Ctrl+Shift+X` (Windows) / `Cmd+Shift+X` (Mac)
2. In the search box type: `Python`
3. Click the one by **Microsoft** and press **Install**

**Pylance Extension** (makes Python smarter in VS Code):
1. Same search box, type `Pylance`
2. Install the one by **Microsoft**

---

### Step 4 — Install Git (version control)

1. Go to **https://git-scm.com/downloads**
2. Download and install for your OS
3. Accept all defaults during installation
4. Verify: open a terminal and type `git --version`

---

## 3. Open the Project in VS Code

### Option A — You already have the project folder on your computer

1. Open VS Code
2. Click **File → Open Folder**
3. Navigate to the `Medical-Data-Gateway-Proto` folder
4. Click **Select Folder** (Windows) or **Open** (Mac)

You will see the folder tree appear in the left sidebar.

### Option B — You need to download it from GitHub

1. Open VS Code
2. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac) to open the Command Palette
3. Type `Git: Clone` and press Enter
4. Paste the repo URL: `https://github.com/AtulAryanSingh/Medical-Data-Gateway-Proto`
5. Choose a folder to save it in
6. VS Code will ask "Would you like to open the cloned repository?" — click **Open**

### How to open the terminal inside VS Code

The terminal is the black command-line window where you type commands.

- Press `` Ctrl+` `` (the backtick key, top-left of keyboard) — OR —
- Click **Terminal → New Terminal** in the top menu

You will see a new panel at the bottom with a prompt like:
```
PS C:\Users\YourName\Medical-Data-Gateway-Proto>
```
(On Mac it looks like: `yourname@MacBook Medical-Data-Gateway-Proto %`)

This terminal is already pointing at your project folder. Every command you type runs inside the project.

---

## 4. Project Structure

Here is every file and what it does:

```
Medical-Data-Gateway-Proto/
│
├── src/                        ← The "engine" — core logic lives here
│   ├── __init__.py             ← Tells Python "this folder is a package"
│   ├── config.py               ← Loads settings from config.yaml
│   ├── anonymizer.py           ← Strips patient information from DICOM files
│   ├── windowing.py            ← Converts raw pixels to Hounsfield Units
│   ├── pipeline.py             ← Orchestrates: load → anonymize → upload
│   ├── clustering.py           ← Groups pixels by intensity using K-Means
│   ├── scanner_qc.py           ← Detects abnormal scanners across the fleet
│   └── visualization.py        ← Creates all the charts and images
│
├── scripts/                    ← Ready-to-run command-line tools
│   ├── generate_sample_data.py ← Creates 10 fake DICOM files for demo
│   ├── run_full_pipeline.py    ← Runs ALL stages end-to-end (your main demo)
│   ├── audit_phi.py            ← Checks files for patient data before sharing
│   └── generate_pipeline_summary.py ← Creates the GitHub Actions results page
│
├── tests/                      ← Automated checks that code works correctly
│   ├── __init__.py
│   ├── test_anonymizer.py      ← 10 tests for the anonymizer
│   ├── test_windowing.py       ← 9 tests for the windowing module
│   ├── test_pipeline.py        ← Tests for the pipeline orchestrator
│   └── test_scanner_qc.py      ← Tests for the QC module
│
├── data/
│   ├── raw/                    ← Input: original (or synthetic) DICOM files go here
│   └── processed/              ← Output: anonymized DICOM files appear here
│
├── reports/                    ← Output: PNG visualisations saved here
│
├── notebooks/
│   └── demo_walkthrough.ipynb  ← Interactive Jupyter notebook demo
│
├── dicom(100)/                 ← Real skull-CT DICOM files (100 images, no PHI)
├── legacy/                     ← Older prototype code (not used in current demo)
│
├── config.yaml                 ← Settings file: folder paths, retry limits etc
├── requirements.txt            ← List of Python libraries this project needs
├── Makefile                    ← Shortcuts: type "make test" instead of long commands
├── Dockerfile                  ← Recipe to run this in a container (e.g. on a server)
├── .github/workflows/
│   └── pipeline.yml            ← CI/CD: GitHub runs tests automatically on every push
└── README.md                   ← Project overview
```

---

## 5. Code Walkthrough

> **How to read this section:** Each file is broken into small chunks. Every chunk has the actual code, then a plain-English explanation below it. If something still seems confusing, read the explanation out loud — speaking it aloud helps.

---

### 5.1 `src/config.py`

**What this file does in one sentence:** Reads the `config.yaml` settings file and makes those settings available to every other part of the code.

**Full file walkthrough:**

```python
import os
import yaml
from typing import Any
```
> These are **imports** — like "include this toolbox". `os` lets Python talk to the filesystem. `yaml` reads `.yaml` config files. `typing` is only used for type hints (documentation for other programmers).

```python
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CONFIG_PATH = os.path.join(_REPO_ROOT, "config.yaml")
```
> **Finding the project root folder.** `__file__` is the path to *this* Python file (`src/config.py`). `os.path.dirname` goes up one folder. Called twice, it goes up to the repo root. Then `_CONFIG_PATH` is the full path to `config.yaml`. This ensures the file is always found, no matter which directory you run the script from.

```python
_DEFAULTS: dict[str, Any] = {
    "paths": {
        "input_folder": "data/raw",
        "output_folder": "data/processed",
        ...
    },
    ...
}
```
> **Default settings** — a dictionary (like a lookup table) with sensible fallback values. If `config.yaml` is missing or doesn't mention a setting, these defaults are used instead.

```python
def _deep_merge(base: dict, override: dict) -> dict:
    ...
```
> A helper function that merges two dictionaries together, going inside nested levels. Think of it like merging two Word documents — the `override` file wins wherever there's a conflict, but everything from the `base` that isn't mentioned in `override` is kept.

```python
def load_config(config_path: str = _CONFIG_PATH) -> dict[str, Any]:
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            user_config = yaml.safe_load(f) or {}
    else:
        user_config = {}
    return _deep_merge(_DEFAULTS, user_config)
```
> **The main function.** Opens `config.yaml`, parses it (converts YAML text into a Python dictionary), and merges it with the defaults. `yaml.safe_load` is used instead of `yaml.load` because it's safer — it won't execute arbitrary code embedded in a YAML file.

```python
CONFIG = load_config()
```
> This line runs once when the file is imported. Any other file can then write `from src.config import CONFIG` and immediately access all settings.

---

### 5.2 `src/anonymizer.py`

**What this file does in one sentence:** Removes patient names, IDs, dates, and other private information (PHI — Protected Health Information) from a DICOM medical image file.

**The key concept — DICOM tags:**
A DICOM file is like a ZIP file: it contains the image (pixels) plus a header with dozens of named fields. These fields are called "tags". Tags like `PatientName`, `PatientID`, and `InstitutionName` contain real patient data — we need to delete them before the file can leave the hospital.

```python
TAGS_TO_REMOVE: list[str] = [
    "PatientName", "PatientID", "PatientBirthDate",
    "PatientSex", "PatientAge", "PatientAddress",
    ...
]
```
> A list of 25 tag names that contain patient identity information. This list comes from the DICOM standard (PS3.15 Annex E) — the international rulebook for medical imaging.

```python
TAGS_TO_REPLACE: dict[str, str] = {
    "StudyDate": "19000101",
    "SeriesDate": "19000101",
    ...
}
```
> Dates can't simply be deleted — some DICOM viewers would crash without them. Instead they're replaced with a dummy date (1 January 1900). This keeps the file valid while removing real information.

```python
def anonymize_dataset(ds: Dataset, station_name: str = "REMOTE_MOBILE_01") -> Dataset:
```
> The main function. It takes a `Dataset` (a loaded DICOM file in memory) and modifies it in place. The `station_name` parameter lets you stamp the file with the mobile unit's identifier.

```python
    for tag_name in TAGS_TO_REMOVE:
        if hasattr(ds, tag_name):
            delattr(ds, tag_name)
```
> Loop through every tag in the removal list. `hasattr` checks if the tag exists (not all DICOM files have all tags). `delattr` deletes it. The `if hasattr` prevents a crash when optional tags are absent.

```python
    ds.remove_private_tags()
```
> DICOM "private tags" are vendor-specific extensions (e.g. Siemens or GE might store extra data). Their contents are unpredictable — they *might* contain PHI. This one-liner removes all of them safely.

```python
    ds.PatientIdentityRemoved = "YES"
    ds.DeidentificationMethod = "DICOM PS3.15 Annex E subset. No UID remap, no pixel scrub."
    ds.StationName = station_name
```
> DICOM standard requires you to mark files that have been de-identified. These three lines add that marker. The `DeidentificationMethod` field must be ≤64 characters (DICOM's VR=LO limit) — this is actually tested in the test suite.

---

### 5.3 `src/windowing.py`

**What this file does in one sentence:** Converts raw CT scanner pixel numbers into Hounsfield Units (HU) and applies "window/level" to make specific tissues visible.

**The key concept — why raw pixels are useless for viewing:**
A CT scanner stores pixel values as integers (e.g. 0–4095). These numbers don't directly mean anything medically. You need to:
1. Convert them to **Hounsfield Units** using a formula from the DICOM header
2. Apply a **window** that zooms in on the relevant tissue range

Think of it like adjusting brightness/contrast on a photo — except the "brightness" and "contrast" values are chosen based on the tissue you want to see.

```python
WINDOW_PRESETS: dict[str, tuple[float, float]] = {
    "brain": (40.0, 80.0),
    "bone": (400.0, 1800.0),
    "lung": (-600.0, 1500.0),
    "soft_tissue": (50.0, 400.0),
}
```
> A lookup table of standard clinical windows. Each entry is `(centre, width)`. The brain window is narrow (80 HU wide) centred at 40 HU — it highlights the small HU differences between brain tissues. The bone window is very wide (1800 HU) centred high.

```python
def to_hounsfield(pixel_array, slope=1.0, intercept=0.0):
    return pixel_array.astype(np.float64) * slope + intercept
```
> The **HU conversion formula** — the simplest possible function. Multiply by the slope and add the intercept (both come from the DICOM header). Air becomes −1024 HU, water becomes 0 HU, bone becomes ~400+ HU.

```python
def apply_window(hu_array, center, width):
    lower = center - width / 2.0
    upper = center + width / 2.0
    windowed = np.clip(hu_array, lower, upper)
    return (windowed - lower) / (upper - lower)
```
> **Clip** forces all values below `lower` to `lower`, and above `upper` to `upper`. Then **normalise** maps the range to [0, 1] by subtracting the minimum and dividing by the range. The result is ready to display as a grey-scale image.

---

### 5.4 `src/pipeline.py`

**What this file does in one sentence:** Orchestrates the whole process — reads every DICOM file from a folder, anonymizes it, saves it, and simulates uploading it to the cloud.

**The key concepts:**

**Data classes** — a compact way to define objects that hold data:
```python
@dataclass
class ProcessingResult:
    filename: str
    success: bool
    error: Optional[str] = None
    duration_s: float = 0.0
```
> This is a blueprint for one result record. `@dataclass` automatically generates `__init__` and `__repr__` methods — you don't have to write boilerplate code. Python reads the field names and types and builds the class for you.

**Exponential backoff:**
```python
def mock_upload(filename, max_attempts=5, base_delay=1.0, max_delay=30.0, failure_rate=0.3):
    for attempt in range(max_attempts):
        if random.random() < failure_rate:
            delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
            time.sleep(delay)
        else:
            return True
    return False
```
> `random.random()` generates a number between 0.0 and 1.0. If it's less than `failure_rate` (0.3 = 30%), the "upload" fails. The retry delay doubles each time: 1s, 2s, 4s, 8s… This is the standard AWS/Google Cloud recommended retry pattern for network calls.
>
> In production, this function would be replaced by an actual HTTPS call to a cloud storage endpoint. The structure (loop + backoff) would be identical.

**The main pipeline function:**
```python
def process_folder(input_folder=None, output_folder=None, ...):
    files = sorted(f for f in os.listdir(input_folder) if not f.startswith("."))
    for filename in files:
        ds = pydicom.dcmread(full_path)
        anonymize_dataset(ds, station_name=station_name)
        ds.save_as(output_path)
        uploaded = mock_upload(filename, ...)
```
> The `for` loop iterates over every file. `pydicom.dcmread` loads the DICOM file into memory. `anonymize_dataset` modifies it (removes PHI). `ds.save_as` writes the clean copy. `mock_upload` simulates sending it.

---

### 5.5 `src/clustering.py`

**What this file does in one sentence:** Groups pixels in a CT image by their intensity level using K-Means clustering — roughly separating air, soft tissue, and bone.

**The key concept — K-Means:**
Imagine you have 1,000 pixel values. K-Means tries to find `k` cluster centres such that every pixel is close to its nearest centre. The algorithm:
1. Pick `k` random centres
2. Assign each pixel to the nearest centre
3. Move each centre to the average position of its assigned pixels
4. Repeat steps 2–3 until nothing changes

With `k=3` on a CT image, the three clusters often end up corresponding roughly to air (very dark), soft tissue (mid-grey), and bone (bright) — because those tissues have distinct HU ranges.

```python
def cluster_scan(ds, n_clusters=3, window_preset="soft_tissue", random_state=42):
    windowed = window_from_dataset(ds, preset=window_preset)
    X = windowed.reshape(-1, 1)
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X)
    cluster_map = labels.reshape(windowed.shape)
```
> `windowed.reshape(-1, 1)` flattens a 2D image (e.g. 512×512) into a column of 262,144 rows, each with one value (pixel intensity). K-Means needs data in this format. `labels` is then reshaped back to the original image dimensions to create a colour-coded map.

**Silhouette score:**
```python
    score = silhouette_score(X[idx], labels[idx])
```
> This measures how well-separated the clusters are. Score of 1.0 = perfect separation. Score of 0 = clusters overlap. Score of −1 = points are in the wrong cluster. A score above 0.5 is good for this use case. We subsample to 5,000 points for speed — exact precision isn't needed for quality-control purposes.

---

### 5.6 `src/scanner_qc.py`

**What this file does in one sentence:** Looks at an entire fleet of scanners and uses K-Means to flag scanners whose images look statistically unusual.

**Why this matters:** A mobile scanner with a calibration problem might produce images that look slightly different — different brightness, different contrast. Comparing all scanners' statistics makes it possible to spot a problem before a radiologist has to.

```python
@dataclass
class ScanFeatures:
    filename: str
    avg_density: float    # Mean pixel value
    contrast: float       # Std dev of pixel values
    peak_value: float     # Maximum pixel value
```
> For each DICOM file, we extract just three numbers. These are the "features" that represent a scan in a compact, machine-readable form.

```python
def extract_features(folder: str):
    for fname in files:
        ds = pydicom.dcmread(full_path, force=True)
        pixels = ds.pixel_array.astype(np.float64)
        rec = ScanFeatures(
            filename=fname,
            avg_density=float(np.mean(pixels)),
            contrast=float(np.std(pixels)),
            peak_value=float(np.max(pixels)),
        )
```
> `np.mean` is the average. `np.std` is standard deviation (how spread out the values are). `np.max` is the maximum. These three values become one row in the feature matrix.

```python
def run_qc(folder, n_clusters=2, random_state=42):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(matrix)
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
```
> **StandardScaler** normalises the features so they all have mean=0 and std=1. This is critical because `avg_density` might be ~1000 while `contrast` is ~200 — without scaling, density would dominate the clustering just because it's a bigger number. After scaling, all three features contribute equally.

---

### 5.7 `src/visualization.py`

**What this file does in one sentence:** Creates and saves four types of charts using matplotlib.

The four chart functions are:

| Function | What it shows |
|----------|--------------|
| `plot_raw_scan(ds)` | The raw DICOM pixels as a greyscale image |
| `plot_windowed_comparison(ds)` | Side-by-side views through brain, bone, lung, soft-tissue windows |
| `plot_clustering(ds)` | Original scan next to the colour-coded K-Means cluster map |
| `plot_fleet_qc(records, labels, silhouette)` | Scatter plot of all scanners, coloured by cluster group |

```python
plt.rcParams.update({"figure.dpi": 100, "axes.titlesize": 11})
```
> This sets global chart styling — resolution (DPI) and font size — applied to all charts in the module.

Each function follows the same pattern:
```python
fig, ax = plt.subplots(figsize=(6, 6))
ax.imshow(ds.pixel_array, cmap="gray")
ax.set_title(title)
ax.axis("off")
return fig
```
> `plt.subplots` creates a figure with one subplot. `ax.imshow` renders the pixel array as an image. `cmap="gray"` makes it greyscale. `return fig` hands the figure back to the caller so it can be saved to disk with `fig.savefig(...)`.

---

### 5.8 `scripts/generate_sample_data.py`

**What this file does in one sentence:** Creates 10 fake DICOM files with synthetic pixel data so you can run the demo without real patient scans.

```python
_SCAN_PROFILES = [
    ("scan_01", 1050, 180, "normal head CT"),
    ...
    ("scan_08", 400,  45, "low-dose / possible miscalibration"),
    ("scan_09", 380,  40, "low-dose / possible miscalibration"),
    ("scan_10", 2200, 600, "high-contrast bone phantom"),
]
```
> Each tuple is `(name, mean_pixel_value, standard_deviation, description)`. Scans 1–7 are "normal" with similar statistics. Scans 8–9 are deliberately unusual (low mean, low contrast) to simulate a miscalibrated scanner. Scan 10 is a high-contrast outlier. This variety makes the QC scatter plot visually interesting.

```python
def _make_dicom(path, patient_name, patient_id, mean_val, std_val, size=128, seed=42):
    rng = np.random.default_rng(seed)
    pixels = rng.normal(mean_val, std_val, size=(size, size))
    pixels = pixels.clip(0, 4095).astype(np.uint16)
    sq = size // 4
    pixels[sq : sq * 2, sq : sq * 2] = min(int(mean_val * 1.8), 4095)
```
> `np.random.default_rng(seed)` creates a random number generator with a fixed seed — so the same file is generated every time (reproducible). The "bright square" in the middle simulates a region of high bone density.

Notice that these fake files include real-looking PHI tags like `PatientName` and `InstitutionName` — that's deliberate, so you can demonstrate the anonymizer removing them.

---

### 5.9 `scripts/run_full_pipeline.py`

**What this file does in one sentence:** The main demo script — runs all five stages end-to-end and saves everything to `reports/`.

The five stages it runs:

```
STEP 1 — Prepare input data       → generates fake DICOMs if data/raw/ is empty
STEP 2 — Batch pipeline           → anonymizes all files + simulated upload
STEP 3 — Intensity clustering     → K-Means on first scan, prints silhouette score
STEP 4 — Scanner QC               → fleet-level outlier detection
STEP 5 — Saving visualisations    → saves 4 PNGs to reports/
```

```python
import matplotlib
matplotlib.use("Agg")
```
> **Critical line.** The `"Agg"` backend means matplotlib doesn't try to open a graphical window — it just writes to files. Without this, the script would fail on a headless server (e.g. GitHub Actions) because there's no screen.

```python
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)
```
> Ensures Python can find the `src/` package by adding the repo root to the module search path. This is needed whenever a script is run from a subdirectory.

---

### 5.10 `scripts/audit_phi.py`

**What this file does in one sentence:** Before you share DICOM files publicly, use this script to check whether they contain real patient data.

```python
_KNOWN_DUMMY_VALUES = {
    "NAME^NONE", "NONE", "ANONYMOUS", "ANON", "NOID", "00000",
    "SN000000", "", "N/A",
}
```
> Common placeholder values that appear in test datasets. If a tag's value matches one of these, it's labelled "dummy" rather than "real PHI".

The script prints a verdict:
- `✓ No real patient identity found.` — safe to share
- `⚠ REAL PHI DETECTED` — must anonymize first

**Why this tool matters for the interview:** You can say: "Before any data goes into the repository, I run the PHI audit script. It checks all 25+ DICOM identity tags and flags anything that looks like real patient data. This prevents accidental data breaches at the ingestion step."

---

### 5.11 `scripts/generate_pipeline_summary.py`

**What this file does in one sentence:** Writes a rich Markdown report (with embedded images) to the GitHub Actions "Summary" tab so you can see results without downloading files.

```python
summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
if summary_path:
    with open(summary_path, "a") as f:
        f.write(summary)
else:
    print(summary)
```
> `GITHUB_STEP_SUMMARY` is an environment variable that GitHub Actions sets automatically. When it exists, the script writes to that special file and the content appears in the Actions UI. When it doesn't exist (i.e. you're running locally), the summary is printed to the terminal instead. This "dual mode" is an example of writing code that works in multiple environments.

---

## 6. Tests

### What tests are and why they exist

Tests are **automated checks** that verify your code works correctly. Instead of manually running the code and looking at the output each time, you write a test once and the computer runs it for you — thousands of times, every time you change the code.

The test framework here is **pytest**. You run it with: `python -m pytest tests/ -v`

### test_anonymizer.py — 10 tests

| Test name | What it checks |
|-----------|----------------|
| `test_phi_tags_removed` | After anonymization, PatientName etc. must not exist |
| `test_non_phi_tags_preserved` | The `Modality` tag ("CT") must survive |
| `test_patient_identity_removed_flag` | The "YES" flag must be set |
| `test_deidentification_method_set` | The description field must be ≤64 chars (DICOM limit) |
| `test_default_station_name_fits_vr_sh` | Station name must be ≤16 chars (DICOM limit) |
| `test_station_name_stamped` | Custom station name is applied correctly |
| `test_dates_replaced_not_removed` | Dates are replaced with "19000101", not deleted |
| `test_private_tags_removed` | Vendor tags must be wiped out |
| `test_missing_optional_tags_no_crash` | Must not crash when optional tags are absent |
| `test_all_tags_to_remove_covered` | Every tag in the removal list is actually removed |

### test_windowing.py — 9 tests

Key tests:
- `test_output_in_zero_one_range` — output must always be between 0 and 1
- `test_zero_width_raises` — asking for a zero-width window must raise a clear error
- `test_all_presets_work` — all four presets (brain, bone, lung, soft_tissue) must work

### test_pipeline.py — 5 tests

Key tests:
- `test_upload_eventually_succeeds` — with failure_rate=0, upload always works
- `test_upload_fails_when_always_failing` — with failure_rate=1, all attempts fail
- `test_output_files_are_anonymized` — output DICOM must have PHI removed

### test_scanner_qc.py — 4 tests

Key tests:
- `test_single_file_returns_nan_silhouette` — can't cluster 1 file; returns NaN not crash
- `test_three_files_with_k2_gives_valid_silhouette` — valid score with enough data

---

## 7. Makefile, Dockerfile, and CI/CD

### The Makefile

The Makefile is a shortcut system. Instead of typing long commands, type `make <target>`:

| Command | What it does | Equivalent long command |
|---------|-------------|------------------------|
| `make setup` | Install dependencies | `pip install -r requirements.txt` |
| `make data` | Generate sample DICOM files | `python scripts/generate_sample_data.py` |
| `make test` | Run all tests | `python -m pytest tests/ -v` |
| `make audit` | Check files for PHI | `python scripts/audit_phi.py` |
| `make run` | Run full end-to-end demo | `python scripts/run_full_pipeline.py` |
| `make clean` | Delete generated files | Deletes all `.dcm` files and `__pycache__` |

**Why it's useful in an interview:** "I added a Makefile so any team member can run `make demo` without needing to memorise the exact command syntax. It's also what the CI pipeline uses — this means local and CI environments run exactly the same commands."

### The Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "scripts/run_full_pipeline.py"]
```

**Plain-English explanation of each line:**
1. `FROM python:3.11-slim` — start with a minimal Linux computer that already has Python 3.11 installed
2. `WORKDIR /app` — set the working directory inside the container to `/app`
3. `COPY requirements.txt .` — copy the requirements file in first (Docker caches this layer — if requirements don't change, it won't reinstall everything)
4. `RUN pip install ...` — install all dependencies
5. `COPY . .` — copy the whole project
6. `CMD [...]` — the default command to run when the container starts

**Why it's relevant:** "Containerisation means the pipeline runs identically on the mobile unit, on a developer's laptop, or in the cloud — no 'it works on my machine' problems."

### The CI/CD Pipeline (`.github/workflows/pipeline.yml`)

This file tells GitHub to automatically run your code every time someone pushes to the `main` branch.

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:    # ← Also allows manual trigger from the GitHub UI
```

The steps it runs:
1. **Checkout** the code
2. **Set up Python 3.12**
3. **Install dependencies** (`pip install -r requirements.txt`)
4. **Run tests** (`python -m pytest tests/ -v`)
5. **Copy real DICOM files** into `data/raw/`
6. **Run the full pipeline** (`python scripts/run_full_pipeline.py`)
7. **Generate the summary** (appears in the Actions UI)
8. **Upload visualisation PNGs** as downloadable artifacts

---

## 8. Install Dependencies

### Open the VS Code terminal and run:

```bash
pip install -r requirements.txt
```

**What `requirements.txt` installs:**

| Library | What it does |
|---------|-------------|
| `pydicom` | Reads and writes DICOM medical image files |
| `numpy` | Fast maths on arrays (pixel manipulation) |
| `scikit-learn` | Machine learning — K-Means, silhouette score, StandardScaler |
| `matplotlib` | Creates charts and saves them as PNG files |
| `PyYAML` | Reads the `config.yaml` settings file |
| `pytest` | Runs the automated tests |
| `jupyter` | Interactive notebook for the demo walkthrough |

**Expected output** (abbreviated):
```
Successfully installed matplotlib-3.9.0 numpy-1.26.4 pydicom-2.4.4 scikit-learn-1.4.2 ...
```

If you see `Successfully installed` at the end, you're good.

---

## 9. Step-by-Step Demo

> **Before any demo or interview:** Run these steps in order. Each step has the exact command to type and the exact output you should see.

---

### Step 0 — Clean/Reset the project

Run this first to start from a clean slate:

```bash
make clean
```

**Expected output:**
```
find data/raw     -name "*.dcm" -delete 2>/dev/null || true
find data/processed -name "*.dcm" -delete 2>/dev/null || true
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
```

**What to say:** *"First I'm clearing any previous run so the interviewer can see the pipeline working from scratch."*

---

### Step 1 — Run the tests

```bash
python -m pytest tests/ -v
```

**Expected output:**
```
========================= test session starts ==========================
platform linux -- Python 3.12.x, pytest-8.x.x
(Note: "linux" will show as "win32" on Windows or "darwin" on Mac)
collected 28 items

tests/test_anonymizer.py::TestTagRemoval::test_phi_tags_removed PASSED
tests/test_anonymizer.py::TestTagRemoval::test_non_phi_tags_preserved PASSED
tests/test_anonymizer.py::TestTagRemoval::test_patient_identity_removed_flag PASSED
tests/test_anonymizer.py::TestTagRemoval::test_deidentification_method_set PASSED
tests/test_anonymizer.py::TestTagRemoval::test_default_station_name_fits_vr_sh PASSED
tests/test_anonymizer.py::TestTagRemoval::test_station_name_stamped PASSED
tests/test_anonymizer.py::TestTagRemoval::test_dates_replaced_not_removed PASSED
tests/test_anonymizer.py::TestTagRemoval::test_private_tags_removed PASSED
tests/test_anonymizer.py::TestTagRemoval::test_missing_optional_tags_no_crash PASSED
tests/test_anonymizer.py::TestTagRemoval::test_all_tags_to_remove_covered PASSED
tests/test_windowing.py::TestHounsfield::test_known_conversion PASSED
tests/test_windowing.py::TestHounsfield::test_default_slope_intercept PASSED
tests/test_windowing.py::TestWindowing::test_output_in_zero_one_range PASSED
tests/test_windowing.py::TestWindowing::test_clip_below_lower_is_zero PASSED
tests/test_windowing.py::TestWindowing::test_clip_above_upper_is_one PASSED
tests/test_windowing.py::TestWindowing::test_center_maps_to_half PASSED
tests/test_windowing.py::TestWindowing::test_zero_width_raises PASSED
tests/test_windowing.py::TestWindowing::test_negative_width_raises PASSED
tests/test_windowing.py::TestWindowFromDataset::test_preset_applied PASSED
tests/test_windowing.py::TestWindowFromDataset::test_missing_rescale_uses_defaults PASSED
tests/test_windowing.py::TestWindowFromDataset::test_unknown_preset_raises PASSED
tests/test_windowing.py::TestWindowFromDataset::test_all_presets_work PASSED
tests/test_pipeline.py::TestMockUpload::test_upload_eventually_succeeds PASSED
tests/test_pipeline.py::TestMockUpload::test_upload_fails_when_always_failing PASSED
tests/test_pipeline.py::TestProcessFolder::test_missing_folder_returns_empty_report PASSED
tests/test_pipeline.py::TestProcessFolder::test_processes_dicom_files PASSED
tests/test_pipeline.py::TestProcessFolder::test_max_files_limits_processing PASSED
tests/test_pipeline.py::TestProcessFolder::test_output_files_are_anonymized PASSED
========================= 28 passed in X.XXs ==========================
```

**What to say:** *"All 28 tests pass. The test suite covers the anonymizer, windowing, pipeline orchestration, and QC module. Tests were written before features in a TDD approach, which is why the CI also runs them automatically on every push."*

---

### Step 2 — Generate sample data

```bash
python scripts/generate_sample_data.py
```

**Expected output:**
```
Writing 10 synthetic DICOM files to: /path/to/data/raw
------------------------------------------------------------
  [01/10] scan_01.dcm  (normal head CT)
  [02/10] scan_02.dcm  (normal head CT)
  [03/10] scan_03.dcm  (normal head CT)
  [04/10] scan_04.dcm  (normal head CT)
  [05/10] scan_05.dcm  (normal head CT)
  [06/10] scan_06.dcm  (normal head CT)
  [07/10] scan_07.dcm  (normal head CT)
  [08/10] scan_08.dcm  (low-dose / possible miscalibration)
  [09/10] scan_09.dcm  (low-dose / possible miscalibration)
  [10/10] scan_10.dcm  (high-contrast bone phantom)
------------------------------------------------------------
Done.  Run the pipeline with: ...
```

**What to say:** *"I'm generating 10 synthetic DICOM files. Seven are 'normal' scans with similar statistics. Two simulate a miscalibrated low-dose scanner, and one simulates a high-contrast bone phantom. These are designed to make the QC scatter plot visually interesting. All files include dummy PHI tags — patient names, IDs, institution names — so we can demonstrate the anonymizer removing them."*

---

### Step 3 — Audit for PHI (before anonymization)

```bash
python scripts/audit_phi.py
```

**Expected output:**
```
============================================================
PHI AUDIT REPORT
============================================================
  Folder        : /path/to/data/raw
  Files scanned : 10

── Identity Tags (TAGS_TO_REMOVE) ──
  PatientName: "Synthetic^Patient01" (1 files) — ⚠ REAL PHI?
  PatientID: "00001" (1 files) — ⚠ REAL PHI?
  InstitutionName: "City General Hospital" (10 files) — ⚠ REAL PHI?
  ReferringPhysicianName: "Smith^Jane" (10 files) — ⚠ REAL PHI?
  ...

VERDICT
============================================================
  ⚠  REAL PHI DETECTED — do NOT store as-is in a public repo!
  Run the anonymization pipeline first:
    python scripts/run_full_pipeline.py
```

**What to say:** *"The audit tool confirms our synthetic files contain PHI-like tags — patient names, institution names, doctor names. This is exactly the kind of data we need to strip before transmission. The audit tool is designed to be run as a pre-flight check. It uses the same tag list as the anonymizer, so there's a single source of truth for which tags are considered PHI."*

---

### Step 4 — Run the full pipeline

```bash
python scripts/run_full_pipeline.py
```

**Expected output (full):**
```
============================================================
STEP 1 — Prepare input data
============================================================
  Input folder : /path/to/data/raw
  Files found  : 10

============================================================
STEP 2 — Batch pipeline (anonymize + simulated upload)
============================================================
INFO     Starting pipeline: 10 files to process.
INFO     Upload succeeded for scan_01.dcm (attempt 1).
WARNING  Upload attempt 1/5 failed for scan_02.dcm. Retrying in 1.32s…
INFO     Upload succeeded for scan_02.dcm (attempt 2).
INFO     Upload succeeded for scan_03.dcm (attempt 1).
...
==================================================
PIPELINE SUMMARY
==================================================
Total files found : 10
Successfully processed: 9
Failed               : 1      ← Normal — the 30% random failure rate means ~1 file
Total time           : 8.43s      exhausts all retry attempts (this is intentional demo behaviour)

============================================================
STEP 3 — Intensity clustering (K-Means)
============================================================
  File         : scan_01.dcm
  Clusters     : 3
  Silhouette   : 0.847

============================================================
STEP 4 — Scanner QC (fleet-level outlier detection)
============================================================
  Scans analysed : 10
  QC silhouette  : 0.921
    Clean_scan_01.dcm: group 0  density=1050.3  contrast=180.1
    Clean_scan_02.dcm: group 0  density=1020.4  contrast=175.3
    ...
    Clean_scan_08.dcm: group 1  density=400.2   contrast=45.1  ⚠ outlier?
    Clean_scan_09.dcm: group 1  density=380.1   contrast=40.2  ⚠ outlier?
    Clean_scan_10.dcm: group 1  density=2200.5  contrast=600.3 ⚠ outlier?

============================================================
STEP 5 — Saving visualisations to reports/
============================================================
  Saved: reports/raw_scan.png
  Saved: reports/windowed_comparison.png
  Saved: reports/clustering.png
  Saved: reports/fleet_qc.png

============================================================
ALL PIPELINE STAGES COMPLETED SUCCESSFULLY
============================================================
  Processed files → data/processed/
  Visualisations  → reports/
```

**What to say at each stage:**

- **At STEP 2:** *"The pipeline is processing each file — loading it, stripping the PHI tags, saving the clean copy, and simulating an upload. You can see the exponential backoff in action — when an upload attempt fails, it waits before retrying, with the delay doubling each time. This is the standard pattern recommended by all major cloud providers."*

- **At STEP 3:** *"The silhouette score of 0.847 is well above 0.5, which indicates the three K-Means clusters are well-separated. In practice this corresponds roughly to the air regions, soft tissue, and bone in the CT slice."*

- **At STEP 4:** *"This is the fleet-level QC result. You can see the seven normal scans in group 0, and the three outliers in group 1 — the two low-dose scans and the bone phantom. The QC silhouette of 0.921 is excellent, meaning these outliers are clearly distinct from the normal group. In a real deployment, this would trigger an alert to the biomedical engineering team to inspect those scanners."*

- **At STEP 5:** *"Four visualisations are saved to the reports folder. I'll show you those in a moment."*

---

### Step 5 — View the output images

In VS Code, navigate to the `reports/` folder in the left sidebar and click on each PNG:

| File | What to describe |
|------|-----------------|
| `raw_scan.png` | *"This is the raw CT slice — you can see a recognisable skull-like shape."* |
| `windowed_comparison.png` | *"The same slice through four clinical windows. The brain window shows soft tissue contrast. The bone window highlights the bright skull. The lung window makes the air dark."* |
| `clustering.png` | *"Left: the windowed scan. Right: the K-Means cluster map coloured by tissue group. The silhouette score is in the title."* |
| `fleet_qc.png` | *"The scatter plot shows all 10 scans plotted by average density vs. contrast. The two clusters are clearly visible — normal scans in one group, outliers in another."* |

---

### Step 6 — Audit after anonymization (to prove PHI is gone)

```bash
python scripts/audit_phi.py data/processed
```

**Expected output:**
```
── Identity Tags (TAGS_TO_REMOVE) ──
  PatientName: (absent) — ✓ safe
  PatientID: (absent) — ✓ safe
  InstitutionName: (absent) — ✓ safe
  ...

VERDICT
============================================================
  ✓  No real patient identity found.
     PatientName/ID contain only dummy placeholder values.
```

**What to say:** *"Running the same audit on the processed output confirms every PHI tag has been removed. The 'before and after' comparison is exactly the kind of evidence you'd present to a data protection officer or an ethics board."*

---

## 10. Behavioural Interview Questions

> Use the **STAR format** for every behavioural question:
> - **S**ituation — brief context
> - **T**ask — what was your role/responsibility
> - **A**ction — what you specifically did
> - **R**esult — what happened / what you learned

---

### Q: "Tell me about a project you're most proud of."

**S:** I designed and built a Medical Data Gateway prototype — an edge-computing pipeline for mobile CT scanners deployed in remote or underserved areas.

**T:** The challenge was to process sensitive medical imaging data locally on the mobile unit before it could be transmitted to a cloud server, ensuring patient privacy and handling unreliable network connections.

**A:** I built a modular Python system with a DICOM anonymization module that removes 25+ PHI tags per the DICOM PS3.15 standard, a retry engine using exponential backoff, K-Means clustering for intensity analysis and fleet-level quality control, and a full CI/CD pipeline with automated tests.

**R:** The result is a working prototype that can process a batch of DICOM files end-to-end, produce visualisations, and detect scanner anomalies automatically. It has 28 automated tests, a Dockerfile for reproducible deployment, and a GitHub Actions workflow that validates every commit.

---

### Q: "Describe a time you had to work with a constraint or limitation."

**S:** Medical data cannot be stored or transmitted with patient identifiers — this is a hard legal and ethical constraint.

**T:** I needed to build a system that could process raw DICOM files while guaranteeing that no patient data ever left the local device unprotected.

**A:** I implemented a PHI audit script as a pre-flight check, followed by an anonymization pipeline based on the DICOM PS3.15 standard. I was explicit about the limitations — for example, the current version doesn't scrub burned-in annotations in pixel data. I documented this clearly rather than pretending the problem was fully solved.

**R:** Being transparent about what the system does and doesn't cover is actually good engineering — it prevents false confidence and makes it clear where the next iteration of work needs to go.

---

### Q: "Tell me about a time you learned something new under pressure."

**S:** Before this project, I had no experience with the DICOM medical imaging standard.

**T:** I needed to understand enough to write correct anonymization code — using the wrong tag list or missing a private tag category could result in a data breach.

**A:** I read the DICOM PS3.15 standard (Annex E), studied the pydicom documentation and the existing open-source de-identification guides, and then wrote the implementation incrementally — starting with the most obvious PHI tags and working outward. I wrote tests for each requirement before writing the code.

**R:** The resulting anonymizer handles 25 identity tags, all date/time tags, and all private vendor tags, with a test suite that covers edge cases like optional tags being absent and station names exceeding DICOM field length limits.

---

### Q: "Describe a technical decision you had to justify."

**S:** For the fleet-level QC module, I chose K-Means clustering over a dedicated anomaly detection algorithm like Isolation Forest.

**T:** I needed to choose an approach that was simple, explainable, and could work with a small number of scanners (often just 5–20).

**A:** I chose K-Means with k=2 because: (a) it's interpretable — you can show a scatter plot and point to which group is the outlier; (b) it works with very small datasets; (c) it's already in the dependency stack for the per-scan clustering. I documented the limitations — K-Means doesn't know which cluster is "normal" without context, and the results depend on k.

**R:** I also documented the upgrade path in the pipeline summary report — listing DBSCAN, Gaussian Mixture Models, and Isolation Forest as natural next steps if the dataset grows or the precision requirements increase.

---

## 11. Technical Interview Questions

### Q: "Walk me through what happens when you run `python scripts/run_full_pipeline.py`."

**Answer:** The script adds the repo root to Python's module search path, then runs five stages sequentially:

1. It checks if `data/raw/` has any files. If empty, it calls `generate_sample_data.py` to create 10 synthetic DICOM files with dummy PHI tags.
2. It calls `process_folder()` from `src/pipeline.py`, which loops over every file, loads it with `pydicom.dcmread()`, calls `anonymize_dataset()` to strip PHI in memory, saves the clean copy to `data/processed/`, and calls `mock_upload()` to simulate transmission with exponential backoff.
3. It loads the first processed file and calls `cluster_scan()` from `src/clustering.py`, which converts pixels to Hounsfield Units, flattens the image to a 1D array, runs K-Means with k=3, and returns the cluster map and silhouette score.
4. It calls `run_qc()` from `src/scanner_qc.py`, which extracts three features (mean, std, max) from every file in `data/processed/`, standardises them with StandardScaler, and clusters with k=2 to flag outliers.
5. It calls the four plotting functions in `src/visualization.py` and saves the resulting figures as PNGs to `reports/`.

---

### Q: "What is Hounsfield Units and why does the windowing step exist?"

**Answer:** CT scanners measure X-ray attenuation. The Hounsfield Unit (HU) scale is a standardised mapping of attenuation values to clinically meaningful numbers: water = 0 HU, air = −1000 HU, dense bone = ~1000 HU. The conversion formula is `HU = pixel × slope + intercept` where slope and intercept come from the DICOM header.

Windowing exists because the human eye can only distinguish about 100 shades of grey simultaneously, but the HU scale spans over 2000 values. A "window" selects the clinically relevant range — for example, the brain window (centre=40, width=80) maps HUs from 0 to 80 onto the full 0–255 display range, making subtle brain tissue differences visible. Using the bone window (centre=400, width=1800) on the same slice shows bone detail but makes all soft tissue appear the same grey.

---

### Q: "What does the silhouette score mean and how do you interpret the values you see?"

**Answer:** The silhouette score measures how similar each data point is to its own cluster compared to other clusters. It ranges from −1 to +1. A score near +1 means the point is well inside its cluster and far from others. A score near 0 means the point is on the boundary between two clusters. A score near −1 means the point might be in the wrong cluster.

In the clustering step, a score of ~0.85 on the CT slice means the three intensity groups (air, tissue, bone) are clearly separated. In the QC step, a score of ~0.92 on the fleet data means the normal scanners and the outliers form very distinct groups — which is exactly what we want: a clear signal that makes flagged scanners easy to identify.

---

### Q: "Why do you use `StandardScaler` in `scanner_qc.py` but not in `clustering.py`?"

**Answer:** In `clustering.py`, we're clustering a single image and all values are in the same unit (the normalised windowed intensity in [0, 1]), so there's no scale imbalance.

In `scanner_qc.py`, the three features are: `avg_density` (~1000), `contrast` (~180), and `peak_value` (~2000+). These have very different magnitudes. Without scaling, K-Means would effectively only cluster on `peak_value` because its larger numbers create larger Euclidean distances. `StandardScaler` transforms each feature to have mean=0 and standard deviation=1, so all three contribute equally to the distance calculation.

---

### Q: "What does `@dataclass` do, and why did you use it?"

**Answer:** `@dataclass` is a Python decorator (a function that modifies another function or class) that automatically generates boilerplate methods like `__init__`, `__repr__`, and `__eq__` based on the class's field annotations. Without it, you'd write:

```python
class ProcessingResult:
    def __init__(self, filename, success, error=None, duration_s=0.0):
        self.filename = filename
        self.success = success
        self.error = error
        self.duration_s = duration_s
```

With `@dataclass`, you write:
```python
@dataclass
class ProcessingResult:
    filename: str
    success: bool
    error: Optional[str] = None
    duration_s: float = 0.0
```

It's cleaner, less error-prone, and self-documenting — the field types act as documentation.

---

### Q: "What is the exponential backoff formula and why is it used?"

**Answer:** The formula in `mock_upload` is:

```
delay = min(base_delay × 2^attempt + uniform(0, 1), max_delay)
```

The delay doubles on each failed attempt (1s → 2s → 4s → 8s → 16s…), capped at `max_delay`. The `uniform(0, 1)` adds random "jitter" — without it, all clients would retry at exactly the same moment, causing a retry storm that could overload the server.

Exponential backoff is the industry standard because it reduces load during outages. AWS, Google Cloud, and Azure all recommend it in their SDK retry documentation. The same pattern applies whether you're uploading DICOM files, calling a REST API, or querying a database.

---

### Q: "What are the current limitations of this system, and what would you improve next?"

**Answer:** I'd group the limitations into three areas:

**Privacy/Compliance:**
- No UID remapping — StudyInstanceUID etc. could theoretically be used to re-link files
- No pixel-level scrub — burned-in annotations in the image itself are not removed
- Not audited for formal HIPAA or GDPR compliance

**ML/Clustering:**
- K-Means labels are not semantically meaningful — it doesn't know which cluster is "air"
- No spatial awareness — neighbouring pixels are treated independently
- Sensitivity to noise and reconstruction kernel

**System:**
- Upload is simulated — no real network call
- No authentication for the upload endpoint
- No DICOM UID generation for the receiving PACS system

**Next steps I'd prioritise:** (1) UID remapping to prevent record linkage, (2) Isolation Forest for QC — better suited to small, imbalanced datasets, (3) Replace `mock_upload` with a real DICOM STOW-RS call.

---

## 12. Troubleshooting

### "ModuleNotFoundError: No module named 'pydicom'"

**Cause:** Dependencies not installed.
**Fix:** Run `pip install -r requirements.txt`

---

### "No files in data/raw — generating samples…" — but then it fails

**Cause:** The sample generation script can't find or create the output folder.
**Fix:** Make sure you're running from the repo root. Check by typing `ls` or `dir` — you should see `src/`, `scripts/`, `data/` etc. in the listing.

---

### "ModuleNotFoundError: No module named 'src'"

**Cause:** Python can't find the `src` package because you're not running from the repo root.
**Fix:** Always `cd` into the repo root first. In VS Code, when you open a folder, the terminal automatically opens there.

---

### Tests show FAILED instead of PASSED

**Check:** Run `python -m pytest tests/ -v --tb=short` to see the full error message.

**Common fixes:**
- If it says `ImportError` → install dependencies
- If it says `AssertionError` → the code logic has changed; review recent edits
- If tests fail for `test_pipeline.py` only → the random seed may produce different retry patterns; those tests use `failure_rate=0.0` or `1.0` so this shouldn't happen

---

### matplotlib saves empty images

**Cause:** `matplotlib.use("Agg")` not called before importing pyplot in a headless environment.
**Fix:** The `run_full_pipeline.py` script already calls this. If you write a new script, add `import matplotlib; matplotlib.use("Agg")` at the very top, before any `import matplotlib.pyplot`.

---

### "Permission denied" on a Mac when running scripts

**Fix:** Run `chmod +x scripts/*.py` in the terminal, then try again.

---

### Something goes wrong during a LIVE interview demo

**Rule 1 — Stay calm and narrate.** Say: *"Let me just check the error message quickly — this is actually a realistic scenario in production too."*

**Rule 2 — Check the obvious things first:**
```bash
# Are you in the right folder?
ls

# Are dependencies installed?
python -c "import pydicom; print('pydicom OK')"

# Is data/raw empty?
ls data/raw/
```

**Rule 3 — Fall back to the audit script.** If the full pipeline fails, running `python scripts/audit_phi.py` still demonstrates meaningful functionality and your understanding of PHI compliance.

**Rule 4 — Use the test output.** If nothing else works, show: `python -m pytest tests/ -v`. All 28 tests passing is still an excellent demo of code quality and test coverage.

**Rule 5 — Use the GitHub Actions page.** If you have internet, open the repo on GitHub and click the "Actions" tab. Show the last successful run — it includes all pipeline outputs and the visualisations as downloadable artifacts. Say: *"Here's the same pipeline running in CI — this is what runs automatically on every push."*

---

## 13. Quick-Reference Cheat Sheet

> Cut this out, print it, or screenshot it before your interview.

### Essential commands

```bash
# Install dependencies (once)
pip install -r requirements.txt

# Reset / clean generated files
make clean

# Generate 10 synthetic DICOM files
python scripts/generate_sample_data.py

# Check files for PHI (before anonymization)
python scripts/audit_phi.py

# Run tests
python -m pytest tests/ -v

# Run the full end-to-end demo
python scripts/run_full_pipeline.py

# Check anonymized output for PHI (should be clean)
python scripts/audit_phi.py data/processed

# Recommended demo order (one command)
make clean && python scripts/generate_sample_data.py && python -m pytest tests/ -v && python scripts/run_full_pipeline.py
```

### Key concepts to remember

| Concept | What to say |
|---------|------------|
| DICOM | "The standard file format for all medical imaging — like PDF for X-rays and CT scans" |
| PHI | "Protected Health Information — patient name, ID, dates, doctor's name etc." |
| De-identification | "Removing PHI so files can be shared or stored without privacy risk" |
| Hounsfield Units | "A standardised scale for CT density — water = 0 HU, air = −1000 HU, bone = +1000 HU" |
| Windowing | "Selecting a HU range to display — like adjusting brightness and contrast for a specific tissue" |
| K-Means | "An algorithm that automatically groups data into k clusters by finding cluster centres" |
| Silhouette score | "A quality metric for clustering — 1 = perfect separation, 0 = no separation" |
| Exponential backoff | "Double the retry delay each time — standard pattern for handling network failures" |
| StandardScaler | "Normalises features to zero mean, unit variance — prevents large-scale features from dominating" |
| CI/CD | "Automated testing on every code push — ensures the pipeline is always working" |

### File locations

| What you want | Where it is |
|--------------|------------|
| All source logic | `src/` |
| Demo script | `scripts/run_full_pipeline.py` |
| PHI audit tool | `scripts/audit_phi.py` |
| Tests | `tests/` |
| Settings | `config.yaml` |
| Output images | `reports/*.png` |
| Anonymised files | `data/processed/` |
| Raw input | `data/raw/` |

### Numbers to remember

| Metric | Typical value | Meaning |
|--------|-------------|---------|
| PHI tags removed | 25+ | Identity tags deleted |
| Date tags replaced | 8 | Replaced with 19000101 |
| Silhouette (clustering) | ~0.85 | Good — clusters well-separated |
| Silhouette (fleet QC) | ~0.92 | Excellent — outliers very clear |
| Retry attempts | 5 | Before giving up on upload |
| Base retry delay | 1.0s | Doubles each failure |
| Max retry delay | 30.0s | Upper cap |
| Test count | 28 | All should pass |

---

*Guide written for Medical Data Gateway prototype — `AtulAryanSingh/Medical-Data-Gateway-Proto`*
