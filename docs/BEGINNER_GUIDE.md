# Medical Data Gateway — Step-by-Step Beginner Guide

> **How to use this guide**
>
> Think of this as building a house, one brick at a time.
> Every section answers three questions: **What** is this? **Why** do we
> need it? **How** does the code actually do it?
>
> Read one brick, try the snippet, then move to the next.
> Do not rush. Understanding Brick 3 makes Brick 4 easy.

---

## Table of Contents

| Brick | Topic |
|------:|-------|
| [1](#brick-1--what-is-this-project) | What is this project? |
| [2](#brick-2--what-is-a-dicom-file) | What is a DICOM file? |
| [3](#brick-3--project-layout--setup) | Project layout & setup |
| [4](#brick-4--the-foundation--configpy--configyaml) | The foundation — configuration |
| [5](#brick-5--layer-1-reading-a-dicom-file) | Layer 1 — Reading a DICOM file |
| [6](#brick-6--the-privacy-problem) | The privacy problem (PHI / HIPAA) |
| [7](#brick-7--layer-2-anonymization) | Layer 2 — Anonymization |
| [8](#brick-8--layer-2-hounsfield-units--windowing) | Layer 2 — Hounsfield Units & Windowing |
| [9](#brick-9--layer-2-the-pipeline-orchestrator) | Layer 2 — The Pipeline Orchestrator |
| [10](#brick-10--layer-3-intensity-clustering) | Layer 3 — Intensity Clustering |
| [11](#brick-11--layer-3-fleet-quality-control) | Layer 3 — Fleet Quality Control |
| [12](#brick-12--making-it-visual) | Making it visual |
| [13](#brick-13--running-the-full-pipeline) | Running the full pipeline |
| [14](#brick-14--tests--why-they-matter) | Tests — why they matter |
| [15](#brick-15--whats-next-production-gaps) | What's next — production gaps |

---

## Brick 1 — What is this project?

### What

This repository is a **learning prototype** for a medical data pipeline.
It reads CT scan files from a mobile X-ray/CT unit, removes patient-
identifying information, and prepares the data for further analysis or
storage.

### Why

Mobile medical units (vans, trailers, field hospitals) scan patients and
produce image files.  Those files contain the patient's name, date of
birth, hospital ID, and other private details.  Before the file can leave
the device and travel to a central server, that private information must
be removed.  This is a legal requirement in most countries (HIPAA in the
USA, GDPR in Europe).

### How the big picture looks

```
┌─────────────────────────────────────────────────────────┐
│                   MOBILE SCANNER VAN                    │
│                                                         │
│  Patient scanned → DICOM file created → data/raw/       │
└──────────────────────────┬──────────────────────────────┘
                           │  (file on disk)
                           ▼
┌─────────────────────────────────────────────────────────┐
│              LAYER 1 — READ  (src/pipeline.py)          │
│  Open every file in data/raw/                           │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│           LAYER 2 — PROCESS  (src/anonymizer.py         │
│                               src/windowing.py)         │
│  Strip patient identity.  Convert pixels to HU values.  │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│           LAYER 3 — ANALYSE  (src/clustering.py         │
│                               src/scanner_qc.py)        │
│  Group pixel intensities.  Flag unusual scans.          │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
                  data/processed/  +  reports/
```

Each layer feeds the next.  You cannot analyse data you have not
read; you should not send data you have not anonymised.

---

## Brick 2 — What is a DICOM file?

### What

**DICOM** stands for *Digital Imaging and Communications in Medicine*.
It is the global standard format for medical images — CT scans, X-rays,
MRIs.  Every DICOM file contains two things bundled together:

1. **Header** — hundreds of labelled fields called *tags* (patient name,
   scan date, machine settings, etc.)
2. **Pixel data** — the actual image, stored as a grid of numbers.

### Why

Medical equipment from any manufacturer (GE, Siemens, Philips…) all
speak the same DICOM language.  One standard means you can write one
piece of software that works with any scanner.

### How a DICOM file is structured (simplified)

```
┌──────────────────────────────────────────────────────┐
│  DICOM FILE (e.g. scan_01.dcm)                       │
│                                                      │
│  ┌─────────────────────────────────────────────────┐ │
│  │  HEADER (metadata tags)                         │ │
│  │  PatientName    = "Doe^John"                    │ │
│  │  PatientID      = "12345"                       │ │
│  │  PatientDOB     = "19800101"                    │ │
│  │  InstitutionName= "City Hospital"               │ │
│  │  Modality       = "CT"                          │ │
│  │  Rows           = 512                           │ │
│  │  Columns        = 512                           │ │
│  │  RescaleSlope   = 1.0                           │ │
│  │  RescaleIntercept = -1024.0                     │ │
│  │  ... 200+ more tags ...                         │ │
│  └─────────────────────────────────────────────────┘ │
│                                                      │
│  ┌─────────────────────────────────────────────────┐ │
│  │  PIXEL DATA (the image)                         │ │
│  │  512 × 512 grid of 16-bit integers              │ │
│  │  e.g. [[1024, 1100, 800, ...], ...]             │ │
│  └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

Each tag is identified by a pair of hexadecimal numbers called a **tag
address**, for example `(0010,0010)` is always PatientName, no matter
which scanner made the file.

### Try it yourself

```python
import pydicom

# Load any .dcm file from the dicom(100)/ folder
ds = pydicom.dcmread("dicom(100)/I1")

# Print a summary of all header tags
print(ds)

# Access one specific tag
print("Patient name:", ds.PatientName)

# Get the pixel grid (a NumPy array)
print("Image shape:", ds.pixel_array.shape)
```

---

## Brick 3 — Project layout & setup

### What

Before touching any code, you need to know *where things live* and
*how to install the dependencies*.

### Project structure

```
Medical-Data-Gateway-Proto/
│
├── config.yaml              ← settings (paths, retry counts, …)
│
├── src/                     ← all source code lives here
│   ├── config.py            ← reads config.yaml
│   ├── anonymizer.py        ← removes patient identity
│   ├── windowing.py         ← converts pixels → HU display values
│   ├── pipeline.py          ← runs the whole batch (Layer 1 + 2)
│   ├── clustering.py        ← groups pixels by intensity (Layer 3)
│   ├── scanner_qc.py        ← detects unusual scans (Layer 3)
│   └── visualization.py     ← produces the charts
│
├── scripts/                 ← runnable helper scripts
│   ├── generate_sample_data.py   ← creates fake DICOM files for practice
│   └── run_full_pipeline.py      ← runs everything end-to-end
│
├── tests/                   ← automated tests (proves the code works)
│
├── data/
│   ├── raw/                 ← DICOM files go IN here
│   └── processed/           ← anonymised files come OUT here
│
└── reports/                 ← saved chart images
```

### Why this layout

Each concern lives in its own file.  `anonymizer.py` only anonymises;
it does not know about clustering.  This separation makes the code
easier to read, test, and change.

### Setup (one-time)

```bash
# 1. Clone the repository
git clone https://github.com/AtulAryanSingh/Medical-Data-Gateway-Proto.git
cd Medical-Data-Gateway-Proto

# 2. Install Python dependencies (pydicom, numpy, scikit-learn, matplotlib)
pip install -r requirements.txt

# 3. Generate 10 synthetic DICOM files so you have something to practise with
python scripts/generate_sample_data.py
```

### What `requirements.txt` means

It is a plain text list of Python packages this project needs.  `pip
install -r requirements.txt` reads the list and downloads everything
automatically.  You do not need to know what each package does yet;
the relevant ones will be explained as they appear.

---

## Brick 4 — The Foundation: `config.py` / `config.yaml`

### What

`config.yaml` is the single place where you change settings without
editing Python code.  `src/config.py` reads that file and makes the
settings available to every other module.

### Why

Imagine you want to change the output folder from `data/processed` to
`D:/hospital_data/out`.  Without a config file you would have to open
several Python files and change it in multiple places — and you might
miss one.  With a config file you change it in exactly one place and
every module automatically picks it up.

### How `config.yaml` looks

```yaml
paths:
  input_folder: "data/raw"
  output_folder: "data/processed"
  reports_folder: "reports"

pipeline:
  max_files: null          # null means "process all files"
  retry:
    max_attempts: 5
    base_delay: 1.0        # seconds to wait before first retry
    max_delay: 30.0        # cap — never wait longer than this

clustering:
  n_clusters: 3
```

YAML uses indentation (like Python) to show nesting.
`paths.input_folder` means "the key `input_folder` inside `paths`".

### How `src/config.py` reads it

```python
import yaml

def load_config(config_path):
    with open(config_path, "r") as f:
        user_config = yaml.safe_load(f)   # parse YAML → Python dict
    return user_config
```

`yaml.safe_load` converts the YAML text into a regular Python
dictionary:

```python
{
    "paths": {
        "input_folder": "data/raw",
        "output_folder": "data/processed",
    },
    "pipeline": {
        "max_files": None,
        "retry": {"max_attempts": 5, "base_delay": 1.0, "max_delay": 30.0},
    },
    "clustering": {"n_clusters": 3},
}
```

### Deep merge — handling missing keys safely

The real `load_config` also defines **defaults** so that if you delete
a key from `config.yaml` the code still works:

```python
# Simplified version of what _deep_merge does
defaults = {"clustering": {"n_clusters": 3}}
user    = {"clustering": {"n_clusters": 5}}   # user overrides it

# Result: user wins where they specified a value
result  = {"clustering": {"n_clusters": 5}}
```

### Try it yourself

```python
from src.config import CONFIG   # the merged config dict

print(CONFIG["paths"]["input_folder"])   # → "data/raw"
print(CONFIG["pipeline"]["retry"])       # → {'max_attempts': 5, ...}
```

---

## Brick 5 — Layer 1: Reading a DICOM file

### What

Layer 1 is the entry point of the pipeline: open the file from disk
and get the data into memory so the rest of the code can work with it.
The library that does this is **pydicom**.

### Why

DICOM files are binary files with a specific internal structure.
Reading them correctly — parsing the header, decoding the pixel data —
would take thousands of lines of code.  `pydicom` has already done that
work.  We just call one function.

### How `pydicom.dcmread` works

```python
import pydicom

ds = pydicom.dcmread("data/raw/scan_01.dcm")
```

`ds` is now a **Dataset** object.  Think of it as a Python object
that holds all the DICOM tags as attributes:

```python
ds.PatientName     # → "Synthetic^Patient01"
ds.Modality        # → "CT"
ds.Rows            # → 128
ds.Columns         # → 128
ds.pixel_array     # → 2-D NumPy array, shape (128, 128)
```

### What `pixel_array` gives you

Every pixel is a 16-bit integer (0 – 65535).  For a CT scan these
numbers encode tissue density, but in a raw form that depends on the
scanner's calibration.  Brick 8 explains how to convert them into
meaningful **Hounsfield Units**.

### The loop in `src/pipeline.py` (Layer 1 core)

```python
import os, pydicom

files = os.listdir("data/raw")          # get every filename in the folder

for filename in files:
    full_path = os.path.join("data/raw", filename)
    ds = pydicom.dcmread(full_path)     # ← this is Layer 1
    # ... Layer 2 processing happens here (next bricks)
```

---

## Brick 6 — The Privacy Problem

### What

**PHI** stands for *Protected Health Information*.  It is any detail
that could be used to identify a patient: name, date of birth, address,
hospital ID, etc.

### Why it matters

1. **Legal** — HIPAA (USA) and GDPR (EU) impose heavy fines for
   exposing patient identity.
2. **Ethical** — patients trust their medical data will stay private.
3. **Practical** — a CT scan file sent to a cloud server carries PHI
   in its header by default.  Someone who intercepts or reads the file
   can see the patient's identity.

### What PHI looks like inside a DICOM file

| Tag name | Example value | Problem |
|---|---|---|
| PatientName | "Doe^John" | Directly identifies the person |
| PatientID | "12345" | Links to hospital records |
| PatientBirthDate | "19800101" | Combined with name = identity |
| InstitutionName | "City General Hospital" | Narrows location |
| AccessionNumber | "ACC001" | Links back to the radiology system |
| StudyDate | "20230601" | Combined with other tags = identity |

### The solution: de-identification

Before the file leaves the scanner, run it through an **anonymizer**
that:
1. **Deletes** tags that contain direct identity (name, ID, address…)
2. **Replaces** dates with a neutral dummy value (1900-01-01)
3. **Removes** private/vendor tags that could also carry PHI
4. **Stamps** the file with a flag saying "this has been de-identified"

The next brick shows exactly how `src/anonymizer.py` does this.

---

## Brick 7 — Layer 2: Anonymization

### What

`src/anonymizer.py` removes or replaces every PHI tag in a DICOM
Dataset.  It implements a subset of **DICOM PS3.15 Annex E** — the
international standard for medical image de-identification.

### Why a dedicated module

If the anonymisation logic lived inside `pipeline.py` it would be
harder to test in isolation, update, or re-use.  A single-
responsibility module (`anonymizer.py`) is easy to verify: load a
dataset with known PHI, run the anonymizer, check the PHI is gone.

### How it works — step by step

**Step 0: Two lists that drive everything**

```python
# Tags to DELETE entirely
TAGS_TO_REMOVE = [
    "PatientName",
    "PatientID",
    "PatientBirthDate",
    "PatientSex",
    "InstitutionName",
    "AccessionNumber",
    # … 20 more …
]

# Tags to REPLACE with a neutral dummy value
TAGS_TO_REPLACE = {
    "StudyDate":       "19000101",
    "SeriesDate":      "19000101",
    "AcquisitionDate": "19000101",
    "StudyTime":       "000000",
    # … more date/time tags …
}
```

Separating "remove" from "replace" matters.  Some tags (like
`PatientName`) should simply disappear.  Date tags must keep *some*
value or the DICOM file becomes structurally invalid, so we replace
them with a harmless placeholder.

**Step 1: Delete PHI tags**

```python
for tag_name in TAGS_TO_REMOVE:
    if hasattr(ds, tag_name):        # only try if the tag exists
        delattr(ds, tag_name)        # remove it from the dataset
```

`hasattr / delattr` are standard Python.  We check before deleting
because the tag might not be present in every file.

**Step 2: Replace date/time tags**

```python
for tag_name, dummy_value in TAGS_TO_REPLACE.items():
    if hasattr(ds, tag_name):
        setattr(ds, tag_name, dummy_value)   # overwrite with dummy
```

**Step 3: Remove private (vendor) tags**

```python
ds.remove_private_tags()
```

DICOM allows scanner manufacturers to store extra data in *private*
tags (tags with an odd group number, e.g. `(0009,0010)`).  Their
contents are undocumented and may contain PHI.  `remove_private_tags()`
is a pydicom helper that deletes all of them in one call.

**Step 4: Stamp the de-identification markers**

```python
ds.PatientIdentityRemoved = "YES"
ds.DeidentificationMethod = "DICOM PS3.15 Annex E subset. ..."
ds.StationName = "REMOTE_MOBILE_01"
```

The `PatientIdentityRemoved = "YES"` tag is the DICOM-standard signal
that tells any downstream system "this file has been de-identified".

### The complete function signature

```python
def anonymize_dataset(ds, station_name="REMOTE_MOBILE_01"):
    """Modify `ds` in place: remove PHI, replace dates, stamp markers."""
    ...
    return ds   # same object, now de-identified
```

Note "in place": the function modifies the Dataset it receives and
returns it.  It does **not** create a copy.  This saves memory for
large scans.

### Try it yourself

```python
import pydicom
from src.anonymizer import anonymize_dataset

ds = pydicom.dcmread("data/raw/scan_01.dcm")
print("Before:", ds.PatientName, ds.PatientID)

anonymize_dataset(ds)

print("PatientName present?", hasattr(ds, "PatientName"))   # → False
print("PatientIdentityRemoved:", ds.PatientIdentityRemoved) # → "YES"
```

---

## Brick 8 — Layer 2: Hounsfield Units & Windowing

### What

Raw CT pixel values are scanner-dependent integers.  **Hounsfield
Units (HU)** convert them to a universal scale where every tissue has
the same HU value regardless of the machine.  **Windowing** then maps
a medically relevant HU range to a 0–1 display range so the image
looks correct on screen.

### Why this matters

Without HU conversion, comparing scans from two different scanners
is meaningless — their raw integers use different baselines.
Without windowing, the 4000 HU range of a CT collapses into grey mush;
you would not see soft tissue or bone clearly.

### The HU formula

```
HU = raw_pixel_value × RescaleSlope + RescaleIntercept
```

These two parameters (`RescaleSlope`, `RescaleIntercept`) are stored
in the DICOM header by the scanner.  Typical values: slope=1, intercept=-1024.

```python
# src/windowing.py — to_hounsfield
def to_hounsfield(pixel_array, slope=1.0, intercept=0.0):
    return pixel_array.astype(float) * slope + intercept
```

**Common tissue HU values** (the scale you get after conversion):

| Tissue | HU range |
|--------|----------|
| Air | ≈ −1000 |
| Fat | ≈ −100 |
| Water | ≈ 0 |
| Soft tissue | ≈ +40 |
| Bone | ≈ +400 to +1000 |

### The windowing formula

A *window* is defined by two numbers:

- **Centre** (also called *Level*) — the HU value shown as mid-grey.
- **Width** — the HU range shown from black to white.

```
lower = centre − width / 2
upper = centre + width / 2

display_value = (HU − lower) / (upper − lower)    # 0 to 1
display_value = clamp(display_value, 0.0, 1.0)    # clip out-of-range
```

```python
# src/windowing.py — apply_window (simplified)
def apply_window(hu_array, center, width):
    lower = center - width / 2.0
    upper = center + width / 2.0
    clipped = np.clip(hu_array, lower, upper)
    return (clipped - lower) / (upper - lower)   # → [0, 1]
```

### Clinical window presets

Radiologists use preset windows for common tasks:

| Preset | Centre | Width | Shows clearly |
|--------|--------|-------|---------------|
| brain | 40 | 80 | Brain hemorrhage, edema |
| bone | 400 | 1800 | Fractures, bone detail |
| lung | −600 | 1500 | Lung nodules, air |
| soft_tissue | 50 | 400 | Muscles, organs |

```python
WINDOW_PRESETS = {
    "brain":       (40.0,    80.0),
    "bone":        (400.0, 1800.0),
    "lung":        (-600.0, 1500.0),
    "soft_tissue": (50.0,  400.0),
}
```

### Try it yourself

```python
import pydicom
from src.windowing import window_from_dataset

ds = pydicom.dcmread("data/raw/scan_01.dcm")

# Returns a 2-D float array with values in [0, 1]
brain_window  = window_from_dataset(ds, preset="brain")
bone_window   = window_from_dataset(ds, preset="bone")

print("Brain window min/max:", brain_window.min(), brain_window.max())
print("Bone  window min/max:", bone_window.min(),  bone_window.max())
```

---

## Brick 9 — Layer 2: The Pipeline Orchestrator

### What

`src/pipeline.py` ties Layer 1 and Layer 2 together.  It loops over
every file in the input folder, calls the anonymizer, saves the result,
and then simulates uploading the cleaned file.

### Why a separate orchestrator

The anonymizer does not know about files on disk.  Reading files does
not know about anonymization.  The pipeline is the *glue* that
connects them — and this separation keeps each piece testable alone.

### How it works — the main loop

```python
def process_folder(input_folder, output_folder):

    files = sorted(os.listdir(input_folder))

    for filename in files:
        # ── Layer 1: Read ─────────────────────────────────
        full_path = os.path.join(input_folder, filename)
        ds = pydicom.dcmread(full_path)

        # ── Layer 2: Process ──────────────────────────────
        anonymize_dataset(ds)

        # ── Write output ──────────────────────────────────
        output_path = os.path.join(output_folder, f"Clean_{filename}")
        ds.save_as(output_path)

        # ── Simulated upload ──────────────────────────────
        mock_upload(filename)
```

### Exponential backoff — the upload retry pattern

Real networks are unreliable.  If an upload fails, you do not want to
hammer the server immediately.  The standard approach is **exponential
backoff**: wait a short time, retry; if it fails again, wait longer:

```
Attempt 1 fails → wait 1 s
Attempt 2 fails → wait 2 s
Attempt 3 fails → wait 4 s
Attempt 4 fails → wait 8 s
Attempt 5 fails → give up
```

The formula: `delay = min(base_delay × 2^attempt, max_delay)`

```python
def mock_upload(filename, max_attempts=5, base_delay=1.0, max_delay=30.0):
    for attempt in range(max_attempts):
        if random.random() < failure_rate:          # simulated failure
            delay = min(base_delay * (2 ** attempt), max_delay)
            time.sleep(delay)                       # wait before retry
        else:
            return True                             # success!
    return False                                    # all attempts used up
```

In production this `mock_upload` call would be replaced by an actual
HTTP POST to an S3 bucket or DICOM-web endpoint.

### Data classes — structured return values

The pipeline returns a **PipelineReport** so the caller can see exactly
what happened:

```python
from dataclasses import dataclass

@dataclass
class ProcessingResult:
    filename: str
    success:  bool
    error:    str | None = None
    duration_s: float   = 0.0

@dataclass
class PipelineReport:
    total_files: int      = 0
    processed:   int      = 0
    failed:      int      = 0
    elapsed_s:   float    = 0.0
    results: list[ProcessingResult] = ...
```

A **dataclass** is a Python shortcut for creating a class that mainly
holds data.  Writing `@dataclass` above a class definition tells Python
to auto-generate `__init__`, `__repr__`, and other boilerplate for you.

### Try it yourself

```python
from src.pipeline import process_folder

report = process_folder(
    input_folder="data/raw",
    output_folder="data/processed",
)
print(report.summary())
```

---

## Brick 10 — Layer 3: Intensity Clustering

### What

`src/clustering.py` groups the pixels of a CT slice into intensity
clusters using the **K-Means** algorithm.  The result is a colour map
that shows which regions of the image share similar density values.

### Why clustering, not segmentation

True medical segmentation (identifying exactly which pixels are brain,
bone, tumour…) requires a trained neural network and validated ground
truth data.  K-Means gives a first approximation purely from intensity —
no training needed.  It is a useful *visualisation* and *quality check*,
not a diagnosis.

### How K-Means works (the concept)

Imagine you have a 1-D list of windowed pixel values between 0 and 1.
K-Means with k=3 finds 3 "centre" values that best summarise the data:

```
pixels: [0.02, 0.03, 0.50, 0.52, 0.48, 0.95, 0.98, 0.01]
                ↑ dark           ↑ mid             ↑ bright

K-Means centres (after fitting):
  Cluster 0 centre ≈ 0.02   (air / very dark)
  Cluster 1 centre ≈ 0.50   (soft tissue / mid-grey)
  Cluster 2 centre ≈ 0.96   (bone / bright)
```

Each pixel is assigned to the nearest centre.  The algorithm repeats
the centre-update and assignment steps until the centres stop moving.

### How the code uses it

```python
from sklearn.cluster import KMeans

# 1. Flatten the 2-D image to a 1-D column of values
X = windowed_image.reshape(-1, 1)   # shape: (512×512, 1)

# 2. Fit K-Means
kmeans = KMeans(n_clusters=3, random_state=42)
labels = kmeans.fit_predict(X)      # each pixel → cluster 0, 1, or 2

# 3. Reshape labels back to the image shape
cluster_map = labels.reshape(windowed_image.shape)
```

### Silhouette score — how good is the clustering?

```python
from sklearn.metrics import silhouette_score

score = silhouette_score(X, labels)
# Ranges from -1 (poor) to +1 (excellent)
# > 0.5 means clusters are well-separated
```

### Try it yourself

```python
import pydicom
from src.clustering import cluster_scan

ds = pydicom.dcmread("data/raw/scan_01.dcm")
windowed, cluster_map, silhouette = cluster_scan(ds, n_clusters=3)

print("Silhouette score:", round(silhouette, 3))
print("Cluster map shape:", cluster_map.shape)
print("Unique labels:", set(cluster_map.flatten()))
```

---

## Brick 11 — Layer 3: Fleet Quality Control

### What

`src/scanner_qc.py` looks at the *whole fleet* — all the anonymised
scans in `data/processed/` — and flags any scan that looks statistically
unusual compared to the others.

### Why fleet QC

A scanner that is drifting out of calibration will produce consistently
darker or lower-contrast images.  A single scan looks fine in isolation;
only when you compare it to 50 others from the same fleet does the
problem become visible.

### How it works — three steps

**Step 1: Extract simple features from each scan**

```python
@dataclass
class ScanFeatures:
    filename:    str
    avg_density: float   # mean pixel value — overall brightness
    contrast:    float   # std dev — how much variation (sharpness)
    peak_value:  float   # max pixel value — brightest region
```

For each DICOM file, calculate these three numbers.  Together they
describe the scan in a way that is quick to compute and captures the
most common scanner problems.

**Step 2: Standardise the features**

The three features live on very different scales (avg_density might be
~1000, contrast ~100, peak_value ~4000).  K-Means uses distances, so
a large-scale feature would unfairly dominate.  **StandardScaler**
fixes this:

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
scaled = scaler.fit_transform(feature_matrix)
# Now every column has mean=0 and std=1
```

**Step 3: Cluster the fleet and surface outliers**

```python
kmeans = KMeans(n_clusters=2)   # "normal" vs "unusual"
labels = kmeans.fit_predict(scaled)
```

The smaller cluster (by file count) is likely the outlier group.
That does not mean the scans are bad — it means they deserve a closer
look by a biomedical engineer.

### Try it yourself

```python
from src.scanner_qc import run_qc

records, labels, silhouette = run_qc("data/processed")
for rec, label in zip(records, labels):
    print(f"  {rec.filename}  cluster={label}  "
          f"avg={rec.avg_density:.0f}  contrast={rec.contrast:.0f}")
```

---

## Brick 12 — Making it Visual

### What

`src/visualization.py` contains every matplotlib chart the project
uses.  It is deliberately kept as one file so that all plotting logic
is in one place — easy to find and easy to swap out.

### Why separate visualisation

Mixing plotting code into `clustering.py` or `pipeline.py` would make
those modules harder to test (you do not want a chart to pop up every
time you run a unit test).  By isolating plotting, you can import
`clustering.py` in tests without any matplotlib interaction.

### Key chart functions

| Function | What it produces |
|---|---|
| `plot_raw_scan(ds)` | Greyscale CT slice, raw pixel values |
| `plot_windowed_comparison(ds)` | Side-by-side brain / bone / lung / soft-tissue windows |
| `plot_clustering(windowed, cluster_map)` | Original image + colour-coded cluster map |
| `plot_fleet_qc(records, labels, score)` | 2-D scatter of avg_density vs contrast, coloured by cluster |

### The pattern every chart follows

```python
import matplotlib.pyplot as plt

def plot_something(data):
    fig, ax = plt.subplots(figsize=(8, 6))  # create figure + axes
    ax.imshow(data, cmap="gray")            # draw the image
    ax.set_title("My Chart Title")
    ax.axis("off")                          # hide axis numbers for images
    return fig                              # return, don't show — caller decides
```

Returning `fig` instead of calling `plt.show()` inside the function
means:
- In a script: `fig.savefig("reports/chart.png")`
- In a notebook: `plt.show()`
- In a test: just check the figure exists — no window pops up

---

## Brick 13 — Running the full pipeline

### What

`scripts/run_full_pipeline.py` is a convenience script that runs
every stage in sequence: generate sample data → anonymise → cluster →
QC → save charts.

### The sequence

```
generate_sample_data.py
       ↓ creates 10 synthetic .dcm files in data/raw/

process_folder()          ← pipeline.py
       ↓ anonymises each file, saves to data/processed/

cluster_scan()            ← clustering.py
       ↓ K-Means on one slice

run_qc()                  ← scanner_qc.py
       ↓ fleet statistics + outlier detection

plot_*()                  ← visualization.py
       ↓ saves PNGs to reports/
```

### Run it

```bash
# Make sure you have installed dependencies (Brick 3)
python scripts/run_full_pipeline.py
```

You will see log output like:

```
INFO     Starting pipeline: 10 files to process.
INFO     Upload succeeded for scan_01.dcm (attempt 1).
INFO     Upload succeeded for scan_02.dcm (attempt 2).
...
INFO     PIPELINE SUMMARY
INFO     Total files found : 10
INFO     Successfully processed: 10
INFO     Failed               : 0
INFO     Total time           : 0.83s
```

Charts are saved in `reports/`.

---

## Brick 14 — Tests: why they matter

### What

The `tests/` folder contains automated tests written with **pytest**.
Each test is a small function that sets up a controlled scenario, calls
one function, and asserts that the result is what we expect.

### Why tests

1. **Confidence** — after you change code, run the tests to verify
   you have not accidentally broken something.
2. **Documentation** — a test named `test_private_tags_removed` is
   self-explanatory about what the anonymizer must do.
3. **Regression prevention** — a bug fixed once, tested, cannot
   silently reappear.

### How a test is structured

```python
# tests/test_anonymizer.py

def test_phi_tags_removed():
    # ARRANGE — build a dataset with known PHI
    ds = _make_dataset()   # helper that creates a test DICOM with PHI

    # ACT — run the function being tested
    anonymize_dataset(ds)

    # ASSERT — check the outcome matches expectations
    assert not hasattr(ds, "PatientName"), "PatientName should be gone"
    assert not hasattr(ds, "PatientID"),   "PatientID should be gone"
```

The **Arrange / Act / Assert** pattern makes every test read like a
tiny story: set the scene, do the thing, check what happened.

### Run tests

```bash
pytest tests/ -v
```

`-v` means *verbose* — you see each test name and whether it passed (`.`)
or failed (`F`).

### Read a test failure

```
FAILED tests/test_anonymizer.py::TestTagRemoval::test_phi_tags_removed
AssertionError: PatientName should be gone
```

This tells you: the test in `test_anonymizer.py`, inside class
`TestTagRemoval`, function `test_phi_tags_removed` failed because
`PatientName` was still present after anonymisation.  You then look
at the `anonymize_dataset` function and find the bug.

---

## Brick 15 — What's next: production gaps

### What

This prototype is intentionally simple.  Several important pieces are
missing before it could handle real patient data in a hospital setting.

### The gaps and how they would be filled

| Gap | Why it matters | What production needs |
|-----|---------------|----------------------|
| **UID remapping** | `StudyInstanceUID` etc. are unique identifiers. If you keep them, different de-identified files from the same patient can be re-linked. | Generate new random UIDs for every file. |
| **Pixel scrubbing** | Some scanners burn patient name or ID directly into the pixel data (as text visible in the image). The anonymizer does not detect this. | OCR + redaction of text regions in the image. |
| **Real upload** | `mock_upload` does not send any bytes. | Replace with authenticated S3 or DICOM-web POST. |
| **Compliance audit** | This code is a prototype, not a certified system. | Engage a HIPAA/GDPR specialist. Obtain formal sign-off. |
| **Containerisation** | Running on any machine requires matching Python version and packages. | Package in Docker so it runs identically everywhere. |
| **Validated segmentation** | K-Means is a visualisation tool, not a clinical segmenter. | Train and validate a segmentation model against expert-labelled ground truth. |

### How to think about the layers in production

```
Layer 1 — Ingest   : Real-time DICOM listener (DICOM C-STORE SCP),
                     not a folder scan.

Layer 2 — Process  : Full DICOM PS3.15 Annex E with UID remap +
                     pixel scrub + formal audit trail.

Layer 3 — Analyse  : Validated AI models, not K-Means prototypes.
                     Results reviewed by qualified clinicians.
```

Each layer in this prototype is a deliberate simplification to keep the
code readable.  Understanding the simplification *and why* you would
replace it is exactly the learning goal.

---

## Summary — the complete journey

```
Brick  1  What is this project?           → the goal
Brick  2  What is a DICOM file?           → the raw material
Brick  3  Project layout & setup          → the toolbox
Brick  4  config.py / config.yaml         → the settings foundation
       ─── LAYER 1 ──────────────────────────────────────────────
Brick  5  pydicom.dcmread                 → get data into memory
       ─── LAYER 2 ──────────────────────────────────────────────
Brick  6  The privacy problem             → understand WHY we anonymise
Brick  7  anonymizer.py                   → remove PHI
Brick  8  windowing.py                    → convert pixels → HU display
Brick  9  pipeline.py                     → glue layers 1 + 2 together
       ─── LAYER 3 ──────────────────────────────────────────────
Brick 10  clustering.py                   → group pixels by intensity
Brick 11  scanner_qc.py                   → flag unusual scans
       ─── PRESENTATION ─────────────────────────────────────────
Brick 12  visualization.py                → turn data into charts
       ─── EXECUTION ───────────────────────────────────────────
Brick 13  run_full_pipeline.py            → run everything
Brick 14  tests/                          → prove it works
Brick 15  Production gaps                 → know what's missing
```

You have now seen every file in the repository and know what each piece
does, why it exists, and how it fits into the whole.  The next house
you build will start with the same bricks — just arranged for a
different goal.

---

*Guide written for Medical Data Gateway Proto — Learning Prototype.*
*Author: Atul Aryan | Status: Learning Resource*
