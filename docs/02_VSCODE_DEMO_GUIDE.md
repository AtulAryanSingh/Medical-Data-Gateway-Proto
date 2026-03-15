# VS Code Demo Guide — Setup to Confident Presentation

> **Goal of this document**
>
> After reading this you will be able to:
> 1. Open the project in VS Code and navigate every file.
> 2. Run any script from the integrated terminal.
> 3. Use the Python debugger to pause, inspect, and step through code.
> 4. Deliver a confident 15-minute live demo of the full pipeline.

---

## Table of Contents

| Section | Topic |
|--------:|-------|
| [V1](#v1--installing-vs-code-and-python) | Installing VS Code and Python |
| [V2](#v2--installing-vs-code-extensions) | Installing VS Code extensions |
| [V3](#v3--opening-the-project) | Opening the project |
| [V4](#v4--the-vs-code-interface-a-map) | The VS Code interface — a map |
| [V5](#v5--the-integrated-terminal) | The integrated terminal |
| [V6](#v6--running-a-python-script) | Running a Python script |
| [V7](#v7--the-python-debugger) | The Python debugger |
| [V8](#v8--reading-a-file-with-no-noise) | Reading a file with no noise |
| [V9](#v9--running-the-tests) | Running the tests |
| [V10](#v10--demo-walkthrough-script) | Demo walkthrough script |

---

## V1 — Installing VS Code and Python

### Install Python 3.10 or newer

1. Go to **https://python.org/downloads**
2. Download the latest installer for your OS
3. Run the installer — on Windows, **tick "Add Python to PATH"**
4. Verify in a terminal:
   ```
   python --version
   ```
   You should see `Python 3.x.x`.

### Install Visual Studio Code

1. Go to **https://code.visualstudio.com**
2. Download and install for your OS (free)

---

## V2 — Installing VS Code extensions

Extensions add features to VS Code.  Open the **Extensions panel** with
`Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (Mac).

Search for and install each of these:

| Extension | Publisher | Why you need it |
|-----------|-----------|----------------|
| **Python** | Microsoft | Runs, lints, and debugs Python files |
| **Pylance** | Microsoft | Intelligent autocomplete and type checking |
| **Jupyter** | Microsoft | View and run `.ipynb` notebooks inline |

After installing, VS Code may ask you to reload — click **Reload**.

---

## V3 — Opening the project

1. Open VS Code.
2. Go to **File → Open Folder…** (or `Ctrl+K Ctrl+O`).
3. Navigate to your `Medical-Data-Gateway-Proto` folder and click
   **Select Folder** (Windows) or **Open** (Mac/Linux).

You will see the **Explorer** panel on the left showing all files and folders.

### Select the Python interpreter

VS Code needs to know which Python installation to use.

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P`) to open the **Command Palette**.
2. Type `Python: Select Interpreter` and press Enter.
3. Choose the Python 3.x version you installed.

### Install project dependencies

Open the terminal (`Ctrl+`` ` `) and run:

```bash
pip install -r requirements.txt
```

Wait for it to finish.  You only need to do this once.

---

## V4 — The VS Code interface: a map

```
┌─────────────────────────────────────────────────────────────────┐
│  TITLE BAR                                                      │
│  Medical-Data-Gateway-Proto — Visual Studio Code                │
├──────┬──────────────────────────────────────────────────────────┤
│      │  EDITOR AREA (main reading/writing area)                 │
│  A   │                                                          │
│  C   │  ┌─────────────────────────────────────────────────────┐ │
│  T   │  │  src/anonymizer.py  ×  │  src/pipeline.py           │ │
│  I   │  ├─────────────────────────────────────────────────────┤ │
│  V   │  │                                                     │ │
│  I   │  │  1  """                                             │ │
│  T   │  │  2  anonymizer.py - DICOM de-identification module. │ │
│  Y   │  │  3  """                                             │ │
│      │  │  4                                                  │ │
│  B   │  │  5  import logging                                  │ │
│  A   │  │                                                     │ │
│  R   └──┤                                                     │ │
│         │                                                     │ │
│ Explorer│                                                     │ │
│ Search  │                                                     │ │
│ Git     │                                                     │ │
│ Debug   └─────────────────────────────────────────────────────┘ │
│ Extensions                                                      │
├─────────────────────────────────────────────────────────────────┤
│  TERMINAL (bottom panel)                                        │
│  $ python scripts/run_full_pipeline.py                          │
│  INFO     Starting pipeline: 10 files to process.              │
└─────────────────────────────────────────────────────────────────┘
```

### Activity Bar (left strip — icons)

| Icon | Opens | Shortcut |
|------|-------|----------|
| 📄 Files | Explorer panel | `Ctrl+Shift+E` |
| 🔍 Magnifier | Search panel | `Ctrl+Shift+F` |
| 🔀 Branch | Git / Source Control | `Ctrl+Shift+G` |
| 🐛 Bug | Run and Debug | `Ctrl+Shift+D` |
| 🧩 Blocks | Extensions | `Ctrl+Shift+X` |

### Explorer panel (file tree)

- Click any file to open it in the editor.
- Click a folder triangle to expand/collapse it.
- Right-click a file for options (rename, delete, etc.).

### Editor area (main area)

- Multiple files open as **tabs** at the top.
- The currently active file is highlighted.
- Line numbers run down the left edge.
- **Minimap** on the far right shows the full file at a tiny scale.

### Status bar (bottom strip)

Shows: current file, current line/column, Python version, Git branch.

---

## V5 — The integrated terminal

The terminal is a text window where you type commands.
Open it: `` Ctrl+` `` (backtick key, top-left of keyboard).

The terminal starts in the project root folder automatically.

### Essential terminal commands

```bash
# Show where you are
pwd

# List files in the current folder
ls                    # Mac/Linux
dir                   # Windows

# Change folder
cd src                # go into the src/ folder
cd ..                 # go up one level
cd /full/path/here    # go to an absolute path

# Run a Python script
python scripts/generate_sample_data.py

# Run the tests
python -m pytest tests/ -v

# Install a package
pip install pydicom
```

**Tip:** Press the `↑` arrow key to repeat the last command.
Press `Tab` to auto-complete file and folder names.

---

## V6 — Running a Python script

### Method 1 — Right-click in the editor

1. Open any `.py` file.
2. Right-click anywhere in the editor.
3. Choose **"Run Python File in Terminal"**.

### Method 2 — The terminal (recommended)

```bash
python scripts/generate_sample_data.py
python scripts/run_full_pipeline.py
```

### Method 3 — Run button (top right of editor)

When a `.py` file is open, a **▶ Run Python File** button appears in the
top-right corner.  Click it.

### What you should see when running the pipeline

```
Writing 10 synthetic DICOM files to: data/raw
  [01/10] scan_01.dcm  (normal head CT)
  ...
  [10/10] scan_10.dcm  (high-contrast bone phantom)
Done.
```

Then:

```
INFO     Starting pipeline: 10 files to process.
INFO     Upload succeeded for scan_01.dcm (attempt 1).
...
INFO     ==================================================
INFO     PIPELINE SUMMARY
INFO     ==================================================
INFO     Total files found : 10
INFO     Successfully processed: 10
INFO     Failed               : 0
INFO     Total time           : 0.84s
```

---

## V7 — The Python debugger

The debugger lets you **pause** the program at any line and **inspect**
every variable at that moment.  This is how you truly understand what code
is doing.

### Setting a breakpoint

1. Open any `.py` file (start with `src/anonymizer.py`).
2. Click in the **gutter** (grey area left of line numbers) next to a line.
3. A **red dot** appears — that is your breakpoint.
4. The program will pause right before executing that line.

### Starting the debugger

1. Open the file you want to debug.
2. Press `F5` (or go to **Run → Start Debugging**).
3. If VS Code asks "Select a debug configuration" choose **"Python File"**.

### Debug controls (toolbar at the top)

| Button | Key | What it does |
|--------|-----|--------------|
| ▶ Continue | `F5` | Run until the next breakpoint |
| ⤵ Step Over | `F10` | Run current line, stop at next |
| ⤴ Step Into | `F11` | Go inside the function being called |
| ⤳ Step Out | `Shift+F11` | Run rest of current function, stop after |
| ⏹ Stop | `Shift+F5` | End the debugging session |

### The Variables panel

While paused, the left panel shows **Variables** — every variable that
exists at this point in the program, with its current value.

Click the triangle next to a variable to expand it and see its contents
(e.g. expand a `Dataset` object to see all its DICOM tags).

### The Watch panel

Add any expression to **Watch** and VS Code evaluates it every time the
debugger pauses:

1. In the Watch panel, click `+`.
2. Type an expression: `ds.PatientName` or `len(files)`.

### The Debug Console

While paused, you can type any Python expression in the **Debug Console**
at the bottom and see the result immediately.

```python
> ds.PatientName
'Doe^John'
> hasattr(ds, "InstitutionName")
True
> len(TAGS_TO_REMOVE)
25
```

### Practical exercise — debug the anonymizer

1. Open `src/anonymizer.py`.
2. Set a breakpoint on the line inside the `for tag_name in TAGS_TO_REMOVE:` loop.
3. Create a test script `/tmp/debug_test.py`:
   ```python
   import sys
   sys.path.insert(0, ".")
   import pydicom
   from src.anonymizer import anonymize_dataset
   ds = pydicom.dcmread("dicom(100)/I1", force=True)
   anonymize_dataset(ds)
   ```
4. Press `F5` to debug.
5. Each time it pauses, look at `tag_name` in the Variables panel.
6. Press `F10` (Step Over) to move to the next iteration.

You will *watch* the loop run, tag by tag.

---

## V8 — Reading a file with no noise

When learning, you want to read the actual source code with no
distractions.  Here are the VS Code features that help:

### Folding

Click the triangle `▸` next to a function or class to **fold** (hide)
its contents.  Click `▾` to unfold.  This lets you get a high-level
overview of a file before diving into details.

### Go To Definition

Hover over any function name and press `F12` (or right-click →
"Go to Definition").  VS Code jumps to where that function is defined —
extremely useful for tracing `from src.anonymizer import anonymize_dataset`
back to the actual code.

### Peek Definition

`Alt+F12` (or right-click → "Peek Definition") shows the definition in a
small inline popup without navigating away.

### Hover for documentation

Hover over any function, class, or variable name.  VS Code shows the
docstring and type information in a tooltip.

### Find all references

Right-click on any name → "Find All References" to see every place in the
codebase that uses it.

### Split editor

Drag a tab to the right half of the screen to see two files side by side.
Useful for reading `src/anonymizer.py` and `tests/test_anonymizer.py`
simultaneously.

---

## V9 — Running the tests

Tests prove the code works.  Running them takes 2 seconds.

### Run all tests from the terminal

```bash
python -m pytest tests/ -v
```

Expected output (all green):

```
tests/test_anonymizer.py::TestTagRemoval::test_phi_tags_removed         PASSED
tests/test_anonymizer.py::TestTagRemoval::test_non_phi_tags_preserved   PASSED
...
======================== 36 passed, 22 warnings in 1.31s ========================
```

### Run one specific test file

```bash
python -m pytest tests/test_anonymizer.py -v
```

### Run one specific test function

```bash
python -m pytest tests/test_anonymizer.py::TestTagRemoval::test_phi_tags_removed -v
```

### VS Code Test Explorer

1. Click the **Testing** icon in the Activity Bar (flask icon 🧪).
2. VS Code discovers all pytest tests automatically.
3. Click the ▶ button next to any test to run it.
4. A green ✓ means passed; red ✗ means failed.
5. Click a failed test to see the error message.

---

## V10 — Demo walkthrough script

This is a **word-for-word script** you can follow when presenting the
project.  Estimated time: 12–15 minutes.

---

### Before you start (preparation)

1. Open VS Code with the project.
2. Open a terminal and run:
   ```bash
   python scripts/generate_sample_data.py
   ```
3. Confirm `data/raw/` contains 10 `.dcm` files.
4. Open the following files as tabs (so you can switch quickly):
   - `src/anonymizer.py`
   - `src/windowing.py`
   - `src/pipeline.py`
   - `src/clustering.py`
   - `src/scanner_qc.py`
   - `tests/test_anonymizer.py`
5. Open a Python REPL in the terminal:
   ```bash
   python
   ```

---

### SLIDE 1 — Introduce the problem (1 minute)

**Say:** "We have a mobile CT scanner in a van.  It scans patients and
produces DICOM files.  These files contain the patient's name, date of
birth, hospital ID.  Before we send the file to a central server, we
must remove all of that.  This project does that — automatically,
every time, in under a second per file."

**Show:** Open `dicom(100)/I1` in the terminal:

```python
>>> import pydicom
>>> ds = pydicom.dcmread("dicom(100)/I1", force=True)
>>> ds.PatientName
```

**Say:** "There it is — patient identity sitting in plain text.
If this file gets intercepted or sent unmodified, the patient's
privacy is violated.  Let's fix that."

---

### SLIDE 2 — The anonymizer (3 minutes)

**Show:** Switch to `src/anonymizer.py`.

**Say:** "This is the anonymizer.  It has two lists.
`TAGS_TO_REMOVE` — these 25 tags are deleted entirely.
`TAGS_TO_REPLACE` — date tags are replaced with a neutral value
so the DICOM stays structurally valid but carries no real date."

**Show:** Scroll to the `anonymize_dataset` function.

**Say:** "The function works in five steps.  Step 1: loop over the
removal list.  For each tag, if it exists, delete it.  Two lines of
Python.  Step 2: replace date tags with 1900-01-01.  Step 3: remove
vendor private tags — we cannot enumerate those so we delete them all.
Step 4: stamp `PatientIdentityRemoved = YES` — the international DICOM
signal that this file has been de-identified.  Step 5: stamp the station
name so the server knows which scanner sent this."

**Live demo:**

```python
>>> from src.anonymizer import anonymize_dataset
>>> ds.PatientName
[whatever it was]
>>> anonymize_dataset(ds)
>>> hasattr(ds, 'PatientName')
False
>>> ds.PatientIdentityRemoved
'YES'
```

**Say:** "Gone.  In one function call."

---

### SLIDE 3 — The windowing module (2 minutes)

**Show:** Switch to `src/windowing.py`.

**Say:** "Raw CT pixel values are meaningless without knowing the
scanner calibration.  Hounsfield Units give us a universal scale.
Air is −1000, water is 0, bone is 400+.  The formula is:
`HU = pixel × slope + intercept`.  The slope and intercept are stored
in the DICOM header."

**Show:** Scroll to `WINDOW_PRESETS`.

**Say:** "Radiologists look at CT scans through different windows.
A brain window uses a very narrow range — 80 HU — centred at 40.
This makes subtle differences in brain tissue visible.  A bone window
is wide — 1800 HU — to show the full density range of bone."

**Live demo:**

```python
>>> from src.windowing import window_from_dataset
>>> import pydicom
>>> ds2 = pydicom.dcmread("data/raw/scan_01.dcm")
>>> brain = window_from_dataset(ds2, preset="brain")
>>> print(brain.min(), brain.max())   # → 0.0 1.0
>>> print(brain.shape)                # → (128, 128)
```

---

### SLIDE 4 — The pipeline (2 minutes)

**Show:** Switch to `src/pipeline.py`.

**Say:** "The pipeline is the orchestrator.  It reads every file in
`data/raw`, runs the anonymizer, saves the clean file to
`data/processed`, and then simulates uploading it to a server.
The upload uses exponential backoff — if it fails, wait 1 second,
retry; if it fails again, wait 2 seconds, then 4, then 8.
This is the standard pattern every cloud provider recommends."

**Show:** The `process_folder` function.

**Say:** "It returns a `PipelineReport` — a dataclass that holds counters:
how many files total, how many succeeded, how many failed, total time.
We used `@dataclass` which is Python shorthand for classes that mainly
hold data — it writes the constructor for us automatically."

**Live demo in terminal:**

```bash
python -c "
from src.pipeline import process_folder
report = process_folder()
print(report.summary())
"
```

---

### SLIDE 5 — Clustering (2 minutes)

**Show:** Switch to `src/clustering.py`.

**Say:** "Now for the analysis layer.  K-Means clustering groups pixels
by intensity into k clusters.  With k=3 on a CT slice, the clusters
loosely correspond to air, soft tissue, and bone — not because we told
the algorithm what tissues are, but because those tissues occupy distinct
intensity ranges.  It discovers the structure automatically."

**Say:** "After clustering, we compute a silhouette score — a number from
−1 to +1 that measures how well-separated the clusters are.  Greater
than 0.5 means they are clearly distinct."

**Live demo:**

```python
>>> from src.clustering import cluster_scan
>>> import pydicom
>>> ds3 = pydicom.dcmread("data/raw/scan_01.dcm")
>>> windowed, cluster_map, score = cluster_scan(ds3, n_clusters=3)
>>> print("Score:", round(score, 3))
>>> print("Cluster labels:", set(cluster_map.flatten()))
```

---

### SLIDE 6 — Fleet QC (2 minutes)

**Show:** Switch to `src/scanner_qc.py`.

**Say:** "The fleet QC module looks at all scans together.  For each
file, it computes three numbers: average pixel value, standard deviation,
maximum value.  These three numbers describe each scan as a point in 3-D
space.  We then cluster those points.  A scan that lands far from the
main cluster deserves a closer look — it might indicate a miscalibrated
scanner or a corrupted file."

**Live demo:**

```bash
python -c "
from src.scanner_qc import run_qc
records, matrix, labels, score = run_qc('data/processed')
for r, label in zip(records, labels):
    flag = '⚠ OUTLIER' if label != labels[0] else ''
    print(f'{r.filename}  cluster={label}  avg={r.avg_density:.0f}  {flag}')
"
```

---

### SLIDE 7 — Tests (1 minute)

**Show:** Switch to `tests/test_anonymizer.py`.

**Say:** "Every module has automated tests.  This one verifies the
anonymizer.  The helper `_make_dataset` builds a DICOM in memory with
known PHI.  Each test: arrange a specific scenario, call the function,
assert the outcome.  36 tests.  If I change one line of the anonymizer
and break it, the tests catch it in 1.3 seconds."

**Live demo:**

```bash
python -m pytest tests/ -v
```

**Say:** "All green.  No regressions."

---

### Closing (30 seconds)

**Say:** "Three layers.  Layer 1: read.  Layer 2: anonymize and window.
Layer 3: cluster and QC.  Each layer is one file.  Each file is one
responsibility.  The tests prove each responsibility is correctly met.
The config file means you change settings in one place.
That is the whole system."

---

## Bonus — Keyboard shortcuts cheat sheet

| Shortcut | Action |
|----------|--------|
| `Ctrl+P` | Quick open any file by name |
| `Ctrl+Shift+P` | Command palette (any VS Code action) |
| `Ctrl+`` ` `` | Toggle terminal |
| `F5` | Start debugging |
| `F10` | Step over (debugger) |
| `F11` | Step into (debugger) |
| `F12` | Go to definition |
| `Alt+F12` | Peek definition |
| `Ctrl+Shift+F` | Search across all files |
| `Ctrl+/` | Toggle line comment |
| `Shift+Alt+F` | Format the current file |
| `Ctrl+Z` | Undo |
| `Ctrl+Shift+Z` | Redo |
| `Ctrl+D` | Select next occurrence of word |
| `Ctrl+B` | Toggle sidebar |

---

*Next: read `docs/03_CODE_WALKTHROUGH.md` for line-by-line annotation of every source file.*
