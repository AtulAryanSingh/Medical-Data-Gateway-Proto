# Code Walkthrough — Every Line Explained

> **How to use this document**
>
> Read it alongside the actual source file open in VS Code.
> Each section explains every line, every keyword, every design decision.
> Nothing is assumed.  Nothing is skipped.

---

## Table of Contents

| Section | File |
|--------:|------|
| [C1](#c1--srcconfigpy) | `src/config.py` |
| [C2](#c2--srcanonymizerpy) | `src/anonymizer.py` |
| [C3](#c3--srcwindowingpy) | `src/windowing.py` |
| [C4](#c4--srcpipelinepy) | `src/pipeline.py` |
| [C5](#c5--srcclusteringpy) | `src/clustering.py` |
| [C6](#c6--srcscanner_qcpy) | `src/scanner_qc.py` |
| [C7](#c7--srcvisualizationpy) | `src/visualization.py` |
| [C8](#c8--testtest_anonymizerpy) | `tests/test_anonymizer.py` |
| [C9](#c9--testtest_pipelinepy) | `tests/test_pipeline.py` |
| [C10](#c10--testtest_windowingpy) | `tests/test_windowing.py` |
| [C11](#c11--testtest_scanner_qcpy) | `tests/test_scanner_qc.py` |

---

## C1 — `src/config.py`

Open the file in VS Code: **Explorer → src → config.py**

```python
"""
config.py - Configuration loader for the Medical Data Gateway.
```

A **docstring** — a string literal at the very top of a module.
It describes what the module does.  Triple quotes `"""` allow the string
to span multiple lines.  Python does not execute it; it is documentation.

```python
Loads settings from config.yaml with sensible defaults so that no
path or tuning parameter is hard-coded inside a module.
"""
```

End of the module docstring.

```python
import os
```

`import os` loads Python's built-in `os` module.  After this line we can
call `os.path.join(...)`, `os.path.exists(...)`, etc.
The `os` module handles file paths, folder operations, and environment
variables in a way that works on Windows, Mac, and Linux.

```python
import yaml
```

`import yaml` loads the **PyYAML** library (installed via
`pip install pyyaml` — it is listed in `requirements.txt`).
YAML is a human-readable format for configuration files.
`yaml.safe_load(...)` parses a YAML text file into a Python dictionary.

```python
from typing import Any
```

`from typing import Any` imports the `Any` type hint from Python's
`typing` module (built-in, no installation needed).
`Any` means "this value can be of any type" — used in the return type
`dict[str, Any]` to say "a dict whose values could be strings, numbers,
other dicts, or None".

```python
# Resolve the config file relative to the repo root, not the CWD,
# so imports work regardless of where the script is launched from.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

This one line is doing three operations chained together.  Let's unpack
from the inside out:

- `__file__` — Python automatically sets this to the path of the current
  script, e.g. `/home/atul/project/src/config.py`.
- `os.path.abspath(__file__)` — converts to an absolute path (resolves
  any `..` or `.`), e.g. `/home/atul/project/src/config.py`.
- `os.path.dirname(...)` — returns the parent directory of that path,
  e.g. `/home/atul/project/src`.
- The outer `os.path.dirname(...)` goes up one more level:
  `/home/atul/project`.

So `_REPO_ROOT` ends up being the path to the repository root, no matter
where in the file system you launch the script from.

The leading underscore in `_REPO_ROOT` is a Python convention meaning
"this is an internal implementation detail; don't import it from outside
this module".

```python
_CONFIG_PATH = os.path.join(_REPO_ROOT, "config.yaml")
```

`os.path.join(a, b)` joins path components with the correct separator
(`/` on Mac/Linux, `\` on Windows).
Result: `/home/atul/project/config.yaml`.

```python
_DEFAULTS: dict[str, Any] = {
```

`_DEFAULTS` is a module-level variable (defined outside any function —
accessible to all functions in this file).

The type hint `dict[str, Any]` means: a dictionary with `str` keys and
values of any type.

The opening `{` begins a dictionary literal.  The closing `}` is at
the end of the block below.

```python
    "paths": {
        "input_folder": "data/raw",
        "output_folder": "data/processed",
        "reports_folder": "reports",
    },
```

`"paths"` is the key; the value is another dictionary (nested dict).
This represents the `paths:` section you see in `config.yaml`.
The comma after `}` separates entries in the outer dict.

```python
    "anonymization": {
        "station_name": "REMOTE_MOBILE_01",
    },
```

Default station name — the identifier stamped on each anonymized file.

```python
    "pipeline": {
        "max_files": None,
```

`None` means "not set" — process all files by default.

```python
        "retry": {
            "max_attempts": 5,
            "base_delay": 1.0,
            "max_delay": 30.0,
        },
    },
    "clustering": {
        "n_clusters": 3,
    },
}
```

End of the `_DEFAULTS` dictionary.

```python
def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge *override* into *base*, returning a new dict."""
```

`def` starts a function definition.
`_deep_merge` (leading underscore = private helper).
Parameters: `base: dict` and `override: dict` — both type-hinted as dicts.
`-> dict` — the function returns a dict.
The docstring describes what the function does.

```python
    result = base.copy()
```

`dict.copy()` makes a **shallow copy** of the dictionary — a new dict
object with the same key-value pairs.  We work with `result` so we do not
modify `base` in place.

```python
    for key, value in override.items():
```

`dict.items()` returns all key-value pairs as tuples.
`for key, value in ...` **unpacks** each tuple into two variables.
So for every key-value pair in `override`, we process it.

```python
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
```

Three conditions joined with `and` — all must be True:
1. `key in result` — this key already exists in base (can merge, not just add).
2. `isinstance(result[key], dict)` — the base value is a dict (can go deeper).
3. `isinstance(value, dict)` — the override value is also a dict.

`isinstance(x, SomeType)` returns True if `x` is an instance of `SomeType`.

```python
            result[key] = _deep_merge(result[key], value)
```

Both values are dicts — **recursively merge** them.  This is **recursion**:
the function calls itself with a smaller problem.  This handles arbitrarily
deep nesting (dicts inside dicts inside dicts).

```python
        else:
            result[key] = value
```

Not both dicts: the override value wins directly.  This is what
"override takes priority" means — user config beats defaults.

```python
    return result
```

Return the merged dictionary.

```python
def load_config(config_path: str = _CONFIG_PATH) -> dict[str, Any]:
```

`config_path: str = _CONFIG_PATH` — parameter with a **default value**.
If the caller doesn't pass `config_path`, it uses the module-level path
we computed above.

```python
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            user_config = yaml.safe_load(f) or {}
```

`os.path.exists(...)` returns True if the file exists.
`with open(config_path, "r") as f:` — opens the file in read mode (`"r"`).
The `with` keyword ensures the file is automatically closed when the block
ends, even if an error occurs.  `f` is the file object.
`yaml.safe_load(f)` reads and parses the entire YAML file into a dict.
`or {}` — if the YAML file is empty, `safe_load` returns `None`; the `or {}`
gives us an empty dict instead (to avoid `None` being merged).

```python
    else:
        user_config = {}
```

If the config file doesn't exist (e.g. fresh clone without one),
use an empty dict — defaults will fill everything in.

```python
    return _deep_merge(_DEFAULTS, user_config)
```

Merge defaults and user config.  User wins on any key they specified;
defaults fill in anything the user omitted.

```python
# Module-level singleton so callers can just do `from src.config import CONFIG`
CONFIG = load_config()
```

This line runs **once when the module is first imported**.  It calls
`load_config()` and stores the result in `CONFIG`.  Every other module
that writes `from src.config import CONFIG` gets this same pre-loaded
dict without re-reading the YAML file.

The comment "singleton" means "there is only one instance of this —
all users share it".

---

## C2 — `src/anonymizer.py`

```python
"""
anonymizer.py - DICOM de-identification module.
```

Module docstring.

```python
Implements a subset of the DICOM PS3.15 Annex E Basic Application Level
Confidentiality Profile.
```

This cites the international standard being partially implemented.
**DICOM PS3.15 Annex E** is the formal specification for how to remove
patient identity from DICOM files.  "Subset" is honest — this code does
not implement every requirement of the full standard.

```python
IMPORTANT LIMITATIONS
---------------------
- Does NOT handle burned-in annotations (text overlaid on pixel data).
```

Some scanners write the patient's name directly into the image pixels
(visible text in the image).  This anonymizer only touches the header;
it does not detect or redact text inside the image.

```python
import logging
```

Loads Python's built-in `logging` module for writing status messages.

```python
from typing import Optional
```

`Optional` is a type hint helper: `Optional[str]` means the value is
either a `str` or `None`.

```python
import pydicom
from pydicom.dataset import Dataset
```

`import pydicom` — the pydicom library for reading/writing DICOM files.
`from pydicom.dataset import Dataset` — imports just the `Dataset` class,
so we can use it in type hints: `def fn(ds: Dataset)`.

```python
logger = logging.getLogger(__name__)
```

Creates a **logger** for this module.
`__name__` is automatically set to the module path, e.g. `"src.anonymizer"`.
Using `__name__` as the logger name means log messages from this module
are tagged `src.anonymizer`, making it easy to filter logs by module in
a large system.

```python
TAGS_TO_REMOVE: list[str] = [
```

`TAGS_TO_REMOVE` is a **module-level constant** (by convention, UPPER_CASE
means constant — don't change it).
Type hint: `list[str]` — a list of strings.

```python
    "PatientName",
    "PatientID",
    "PatientBirthDate",
    "PatientSex",
    "PatientAge",
    "PatientAddress",
    "PatientTelephoneNumbers",
    "OtherPatientIDs",
    "OtherPatientNames",
    "OtherPatientIDsSequence",
    "ReferringPhysicianName",
    "ReferringPhysicianAddress",
    "ReferringPhysicianTelephoneNumbers",
    "InstitutionName",
    "InstitutionAddress",
    "InstitutionalDepartmentName",
    "PerformingPhysicianName",
    "OperatorsName",
    "NameOfPhysiciansReadingStudy",
    "RequestingPhysician",
    "ScheduledPerformingPhysicianName",
    "AccessionNumber",
    "StudyID",
    "DeviceSerialNumber",
    "RequestedProcedureID",
]
```

25 tag names.  These correspond to DICOM attributes that contain patient
or operator identity.  The names match the keyword attributes pydicom uses
(e.g. `ds.PatientName`, `ds.InstitutionName`).

```python
TAGS_TO_REPLACE: dict[str, str] = {
    "StudyDate": "19000101",
    "SeriesDate": "19000101",
    "AcquisitionDate": "19000101",
    "ContentDate": "19000101",
    "StudyTime": "000000",
    "SeriesTime": "000000",
    "AcquisitionTime": "000000",
    "ContentTime": "000000",
}
```

Type hint: `dict[str, str]` — keys and values are both strings.
Date format in DICOM is `YYYYMMDD` (no dashes): `"19000101"` = Jan 1, 1900.
Time format: `HHMMSS` — `"000000"` = midnight.

Why replace instead of delete?  DICOM validators expect date tags to be
*present* (just not identifying).  Deleting them would make some downstream
tools flag the file as malformed.

```python
def anonymize_dataset(
    ds: Dataset,
    station_name: str = "REMOTE_MOBILE_01",
) -> Dataset:
```

Function definition.  Two parameters:
- `ds: Dataset` — the pydicom Dataset to anonymize (required).
- `station_name: str = "REMOTE_MOBILE_01"` — defaults to this value if
  not provided.

Return type `-> Dataset` — returns the same Dataset (modified in place).

```python
    """
    Remove or replace PHI tags in a pydicom Dataset **in place**.

    The function:
    1. Deletes every tag listed in TAGS_TO_REMOVE (silently skips missing ones).
    2. Replaces every tag listed in TAGS_TO_REPLACE with its dummy value.
    3. Removes all private (vendor-specific) tags via pydicom's built-in helper.
    4. Stamps the dataset with DICOM-standard de-identification markers.
    5. Sets StationName so the receiving server knows the scan origin.
    ...
    """
```

The docstring explains all five steps.  A well-written docstring makes
the function self-documenting — reading the docstring gives you the
full picture without reading the code body.

```python
    # Step 1 — Remove PHI tags
    for tag_name in TAGS_TO_REMOVE:
```

Loop over the list of tag names, one at a time.
On the first iteration, `tag_name = "PatientName"`.
On the second, `tag_name = "PatientID"`.  And so on.

```python
        if hasattr(ds, tag_name):
```

`hasattr(object, name)` — returns `True` if the object has an attribute
with that name.  We check before deleting because not every DICOM file
has every possible tag.  If we tried to delete a non-existent tag,
Python would raise `AttributeError` and crash.

```python
            delattr(ds, tag_name)
```

`delattr(object, name)` — removes the attribute.
This is why we can't just write `del ds.PatientName` — the tag name is in
a *variable*, not written literally in the code.  `delattr` lets us use a
variable as the attribute name.

```python
            logger.debug("Removed tag: %s", tag_name)
```

Log at DEBUG level — only visible if logging is configured to show DEBUG.
`%s` is a placeholder; Python fills it with `tag_name` at format time.
Logging is preferred over `print()` because you can control verbosity
centrally (set level to INFO to hide all DEBUG messages).

```python
    # Step 2 — Replace date/time tags with neutral values
    for tag_name, dummy_value in TAGS_TO_REPLACE.items():
```

`.items()` on a dict returns `(key, value)` pairs.
`for tag_name, dummy_value in ...` **unpacks** each pair into two variables.
So `tag_name = "StudyDate"` and `dummy_value = "19000101"` on first pass.

```python
        if hasattr(ds, tag_name):
            setattr(ds, tag_name, dummy_value)
```

`setattr(object, name, value)` — set an attribute by name.
Same reason for `setattr` instead of `ds.StudyDate = ...`: the name is in
a variable.

```python
            logger.debug("Replaced tag %s → %s", tag_name, dummy_value)
```

Log the replacement for debugging.

```python
    # Step 3 — Remove all private (odd-group) tags.
    # Private tags are vendor extensions and may contain PHI we cannot
    # enumerate in advance, so blanket removal is the safe approach.
    ds.remove_private_tags()
```

`remove_private_tags()` is a method built into pydicom's `Dataset` class.
DICOM private tags have tag group numbers that are odd (e.g. `0009`, `0011`).
Scanner manufacturers use these for proprietary data.  Their content is
unknown to us, so we remove all of them.

```python
    # Step 4 — DICOM-standard de-identification markers
    ds.PatientIdentityRemoved = "YES"
```

Sets a new tag on the dataset.  `PatientIdentityRemoved` is a standard
DICOM tag (0012,0062).  Downstream systems check for this tag to know
whether a file has been de-identified.

```python
    ds.DeidentificationMethod = (
        "DICOM PS3.15 Annex E subset. No UID remap, no pixel scrub."
    )
```

Another standard tag (0012,0063).  VR=LO (Long String), max 64 characters.
The value honestly states what was done and what was NOT done.

```python
    # Step 5 — Stamp with the edge device identifier
    ds.StationName = station_name
```

`StationName` (0008,1010) VR=SH (Short String), max 16 characters.
The default `"REMOTE_MOBILE_01"` is exactly 16 characters.

```python
    return ds
```

Return the modified dataset.  Since we modified `ds` **in place**
(no copy was made), the caller's variable also reflects the changes —
`return ds` is optional here but makes the function usable in a chain:
`result = anonymize_dataset(ds)`.

```python
def anonymize_file(
    input_path: str,
    output_path: str,
    station_name: str = "REMOTE_MOBILE_01",
) -> None:
```

A convenience wrapper that handles the file I/O around `anonymize_dataset`.
`-> None` — this function does not return a value (it produces side effects
— saving a file — instead).

```python
    ds = pydicom.dcmread(input_path)
```

`pydicom.dcmread(path)` reads a DICOM file from disk and returns a `Dataset`
object in memory.

```python
    anonymize_dataset(ds, station_name=station_name)
```

Call the anonymizer we just defined.  Pass `station_name` as a
**keyword argument** (using the name instead of positional order) —
makes the call easier to read.

```python
    ds.save_as(output_path)
```

`save_as(path)` is a pydicom `Dataset` method that serialises the dataset
back to a DICOM binary file at the given path.

```python
    logger.info("Anonymized %s → %s", input_path, output_path)
```

Log at INFO level — this is visible in normal operation.

---

## C3 — `src/windowing.py`

```python
WINDOW_PRESETS: dict[str, tuple[float, float]] = {
    "brain": (40.0, 80.0),
    "bone": (400.0, 1800.0),
    "lung": (-600.0, 1500.0),
    "soft_tissue": (50.0, 400.0),
}
```

`tuple[float, float]` — a tuple of exactly two floats.
Each value in this dict is a `(centre, width)` pair.
A **tuple** is like a list but immutable — its values cannot be changed.
Used here because `(centre, width)` is a fixed pair, not a growable list.

```python
def to_hounsfield(
    pixel_array: np.ndarray,
    slope: float = 1.0,
    intercept: float = 0.0,
) -> np.ndarray:
```

`np.ndarray` — a NumPy array.  The type hint tells us the input and output
are both NumPy arrays.

```python
    return pixel_array.astype(np.float64) * slope + intercept
```

`.astype(np.float64)` — convert pixel values to 64-bit floats.
This is important because the original pixels are 16-bit integers (0–65535).
Multiplying integers by `slope` and adding `intercept` could overflow or
lose precision without first converting to float.

`* slope + intercept` — NumPy applies this to *every element simultaneously*,
without a for loop.  This is called **vectorised** computation and is
much faster than a Python for loop for large arrays.

```python
def apply_window(
    hu_array: np.ndarray,
    center: float,
    width: float,
) -> np.ndarray:
    lower = center - width / 2.0
    upper = center + width / 2.0
```

For brain window: `center=40, width=80` → `lower = 40 - 40 = 0`, `upper = 80`.
Only HU values between 0 and 80 will be visible in the full range.

```python
    if width <= 0:
        raise ValueError(
            f"Window width must be > 0, got width={width}."
        )
```

**Validation** — check inputs before using them.
`raise ValueError(...)` intentionally crashes the program with a descriptive
error message.  This is better than letting a `ZeroDivisionError` or silent
wrong result appear later.
The test `test_zero_width_raises` in `tests/test_windowing.py` verifies
this line works correctly.

```python
    windowed = np.clip(hu_array, lower, upper)
```

`np.clip(array, min, max)` — every element below `min` becomes `min`,
every element above `max` becomes `max`, values in between are unchanged.
This clamps the HU values to the window range.

```python
    return (windowed - lower) / (upper - lower)
```

**Normalise to [0, 1]:**
- `windowed - lower` shifts values so the minimum is 0.
- `/ (upper - lower)` scales so the maximum is 1.
- Result: values between 0.0 (pure black) and 1.0 (pure white).

```python
def window_from_dataset(
    ds: Dataset,
    preset: Optional[str] = None,
    center: Optional[float] = None,
    width: Optional[float] = None,
) -> np.ndarray:
```

All three keyword arguments default to `None` (caller may omit any of them).
The priority logic inside determines which takes effect.

```python
    slope = float(getattr(ds, "RescaleSlope", 1.0))
    intercept = float(getattr(ds, "RescaleIntercept", 0.0))
```

`getattr(object, name, default)` — three-argument form: if the attribute
doesn't exist, return `default` instead of raising `AttributeError`.
`float(...)` converts to float in case pydicom returned a `DSfloat` wrapper.

```python
    hu = to_hounsfield(ds.pixel_array, slope=slope, intercept=intercept)
```

`ds.pixel_array` — pydicom property that decodes the raw pixel bytes into
a NumPy array.  Calling `to_hounsfield` converts to HU.

```python
    if center is not None and width is not None:
        wc, ww = center, width
```

**Priority 1**: explicit arguments passed by the caller.
`wc, ww = center, width` is **tuple unpacking** — assigns two variables
in one line.

```python
    elif preset is not None:
        if preset not in WINDOW_PRESETS:
            raise ValueError(...)
        wc, ww = WINDOW_PRESETS[preset]
```

**Priority 2**: named preset.  Look it up in the dict and unpack the tuple.

```python
    else:
        dicom_wc = getattr(ds, "WindowCenter", None)
        dicom_ww = getattr(ds, "WindowWidth", None)
        if dicom_wc is not None and dicom_ww is not None:
            wc = float(dicom_wc) if not hasattr(dicom_wc, "__iter__") else float(list(dicom_wc)[0])
            ww = float(dicom_ww) if not hasattr(dicom_ww, "__iter__") else float(list(dicom_ww)[0])
```

**Priority 3**: read from DICOM header.
Some DICOM files store `WindowCenter` as a single value; others as a
`MultiValue` list (when multiple windows are defined).
`hasattr(x, "__iter__")` checks if the object is iterable (like a list).
If it is, `list(dicom_wc)[0]` takes the first item.

```python
        else:
            logger.warning("No window parameters found; defaulting to soft_tissue preset.")
            wc, ww = WINDOW_PRESETS["soft_tissue"]
```

**Priority 4 (fallback)**: if nothing else is available, use soft_tissue.
Log a warning so the operator knows a default was used.

```python
    logger.debug("Applying window: centre=%.1f, width=%.1f", wc, ww)
    return apply_window(hu, center=wc, width=ww)
```

Log the parameters (at DEBUG level — hidden in production).
Call `apply_window` with the resolved centre and width.

---

## C4 — `src/pipeline.py`

```python
import random
import time
from dataclasses import dataclass, field
```

`random` — built-in module for random number generation.
`time` — built-in module: `time.sleep(n)` pauses for n seconds,
`time.time()` returns the current time as a float (seconds since 1970-01-01).
`dataclass`, `field` — tools for creating data-holding classes.

```python
from src.anonymizer import anonymize_dataset
from src.config import CONFIG
```

**Relative imports** — these reference other files within our own `src/`
package.  `from src.anonymizer import anonymize_dataset` finds
`src/anonymizer.py` and brings in the `anonymize_dataset` function.
`from src.config import CONFIG` brings in the pre-loaded config dict.

```python
@dataclass
class ProcessingResult:
    """Summary of a single file's processing outcome."""
    filename:   str
    success:    bool
    error:      str | None = None
    duration_s: float = 0.0
```

`@dataclass` is a **decorator** — a function that wraps another function
or class to modify its behaviour.  When applied to a class, it generates:
- `__init__` (constructor) with one parameter per field.
- `__repr__` (readable string representation for printing).
- `__eq__` (equality comparison).

`str | None` — Python 3.10+ syntax for "str or None" (equivalent to
`Optional[str]` from `typing`).

Fields with default values (`= None`, `= 0.0`) must come after fields
without defaults (just like parameters in a function).

```python
@dataclass
class PipelineReport:
    """Aggregate report produced at the end of a batch run."""
    total_files: int = 0
    processed: int = 0
    failed: int = 0
    elapsed_s: float = 0.0
    results: list[ProcessingResult] = field(default_factory=list)
```

`field(default_factory=list)` — this is necessary when the default value
is a **mutable** object (like a list).  Without `default_factory`, all
instances would share the SAME list object (a famous Python gotcha).
`default_factory=list` means: "call `list()` to create a NEW empty list
for each new `PipelineReport` instance".

```python
    def summary(self) -> str:
        lines = [
            "=" * 50,
```

`"=" * 50` — Python string repetition: `"="` repeated 50 times.
`["=" * 50, ...]` builds a list of strings, one per line of the summary.

```python
            f"Total files found : {self.total_files}",
```

`self.total_files` — inside a method, `self` refers to the specific instance.
So `self.total_files` is the `total_files` attribute of THIS report object.

```python
        return "\n".join(lines)
```

`"\n".join(iterable)` — joins all strings in `lines` with a newline `\n`
between them.  The result is a single multi-line string ready for `print()`.

```python
def mock_upload(
    filename: str,
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    failure_rate: float = 0.3,
) -> bool:
```

`failure_rate: float = 0.3` — 30% of simulated upload attempts will fail.

```python
    for attempt in range(max_attempts):
```

`range(max_attempts)` generates integers 0, 1, 2, ..., max_attempts-1.
`attempt` is the current attempt number (0-based).

```python
        if random.random() < failure_rate:
```

`random.random()` returns a random float in [0.0, 1.0).
If the random number is less than `failure_rate` (0.3), we simulate failure.
On average this is True 30% of the time.

```python
            delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
```

**Exponential backoff with jitter:**
- `2 ** attempt` — 2 to the power of attempt: `1, 2, 4, 8, 16, ...`
- `base_delay * (2 ** attempt)` — `1.0, 2.0, 4.0, 8.0, ...`
- `+ random.uniform(0, 1)` — add a random *jitter* (0 to 1 second).
  Jitter prevents all clients from retrying at the exact same moment
  (which would cause a "thundering herd" and overload the server).
- `min(..., max_delay)` — never wait longer than `max_delay` seconds.

```python
            time.sleep(delay)
```

Pause the program for `delay` seconds before the next attempt.

```python
        else:
            logger.info("Upload succeeded for %s (attempt %d).", filename, attempt + 1)
            return True
```

`return True` — exits the function immediately.
`attempt + 1` converts 0-based to human-readable 1-based.

```python
    logger.error("All %d upload attempts failed for %s.", max_attempts, filename)
    return False
```

If the loop finishes without a successful return, all attempts failed.
The `return False` is reached only after the `for` loop exhausts all attempts.

```python
def process_folder(
    input_folder: Optional[str] = None,
    output_folder: Optional[str] = None,
    max_files: Optional[int] = None,
    station_name: Optional[str] = None,
) -> PipelineReport:
```

All parameters are `Optional` — the caller can omit any of them and the
function will use config defaults.  This makes the function easy to call
from tests with specific values and from production with config values.

```python
    input_folder = input_folder or CONFIG["paths"]["input_folder"]
```

`x or y` — if `x` is falsy (None, empty string, 0), use `y`.
So: if `input_folder` was not passed (None), use the config value.

```python
    report = PipelineReport()
    batch_start = time.time()
```

Create a new empty report.  Record the start time.
`time.time()` returns a float: seconds since 1 Jan 1970 (Unix epoch).

```python
    if not os.path.isdir(input_folder):
        logger.error("Input folder not found: %s", input_folder)
        return report
```

**Guard clause** — check for an error condition early and return
immediately.  This avoids deep nesting.  Returning early with an empty
report tells the caller "nothing was processed".

```python
    os.makedirs(output_folder, exist_ok=True)
```

`os.makedirs(path, exist_ok=True)` — creates the directory (and any
missing parent directories).  `exist_ok=True` means: don't raise an error
if the directory already exists.

```python
    files = sorted(
        f for f in os.listdir(input_folder) if not f.startswith(".")
    )
```

**Generator expression inside sorted():**
- `os.listdir(input_folder)` — returns a list of all filenames in the folder.
- `for f in ...` — iterate over each filename.
- `if not f.startswith(".")` — skip hidden files (`.gitkeep`, `.DS_Store`).
- `sorted(...)` — sort alphabetically so processing order is consistent.

```python
    if max_files is not None:
        files = files[:max_files]
```

**List slicing:** `list[:n]` returns the first `n` elements.
Only applied if `max_files` was set (not None).

```python
    report.total_files = len(files)
    logger.info("Starting pipeline: %d files to process.", report.total_files)
```

Record how many files we found, then log it.

```python
    for filename in files:
        file_start = time.time()
        result = ProcessingResult(filename=filename, success=False)
```

For each file: record start time, create a result object (default: failed).
We start with `success=False` so that if an exception occurs and we never
set `success=True`, the default is already correct.

```python
        try:
            full_path = os.path.join(input_folder, filename)
            ds = pydicom.dcmread(full_path)
```

**`try` block** — if any exception occurs in this block, jump to `except`.
`os.path.join` builds the full path: `"data/raw/scan_01.dcm"`.
`pydicom.dcmread(full_path)` — read the DICOM file into memory.

```python
            anonymize_dataset(ds, station_name=station_name)
```

Modify `ds` in place — remove PHI.

```python
            output_path = os.path.join(output_folder, f"Clean_{filename}")
            ds.save_as(output_path)
```

Construct output path: `"data/processed/Clean_scan_01.dcm"`.
`ds.save_as(output_path)` — write the anonymized dataset to disk.

```python
            uploaded = mock_upload(
                filename,
                max_attempts=max_attempts,
                base_delay=base_delay,
                max_delay=max_delay,
            )
```

Simulate the network upload.  Returns `True` or `False`.

```python
            result.success = uploaded
            if uploaded:
                report.processed += 1
            else:
                result.error = "Upload failed after all retries"
                report.failed += 1
```

**`+=`** means "add to itself": `report.processed += 1` is shorthand for
`report.processed = report.processed + 1`.

File saved but upload failed → counted as `failed`.
File saved AND uploaded → counted as `processed`.

```python
        except Exception as exc:
            result.error = str(exc)
            report.failed += 1
            logger.exception("Error processing %s: %s", filename, exc)
```

`except Exception as exc` — catches any exception (any type of error).
`str(exc)` — converts the exception to a readable string for the report.
`logger.exception(...)` — logs at ERROR level AND includes the full
stack trace (line numbers showing exactly where the error occurred).
After `except`, the loop continues with the next file.

```python
        result.duration_s = time.time() - file_start
        report.results.append(result)
```

`time.time() - file_start` — current time minus start time = elapsed seconds.
`.append(result)` — add this result to the report's list.
This line is *outside* the try/except, so it always runs (whether the
file succeeded or failed).

```python
    report.elapsed_s = time.time() - batch_start
    logger.info(report.summary())
    return report
```

After the loop finishes: record total elapsed time, log the summary,
return the complete report.

---

## C5 — `src/clustering.py`

```python
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
```

`sklearn` is scikit-learn — a machine learning library.
`KMeans` — the K-Means clustering algorithm class.
`silhouette_score` — a function to evaluate clustering quality.

```python
from src.windowing import window_from_dataset
```

Import from another module in our own project.  This creates a **dependency**:
`clustering.py` needs `windowing.py` to work.

```python
def cluster_scan(
    ds: Dataset,
    n_clusters: int = 3,
    window_preset: str = "soft_tissue",
    random_state: int = 42,
) -> tuple[np.ndarray, np.ndarray, float]:
```

Returns **three values** as a tuple: windowed image, cluster map, score.
`random_state: int = 42` — K-Means uses randomness internally (for
initial cluster centres).  Setting a fixed seed (`42` is conventional)
makes results identical every time you run.

```python
    windowed = window_from_dataset(ds, preset=window_preset)
```

Call `window_from_dataset` from `windowing.py` to get the normalised [0,1]
image array.

```python
    X = windowed.reshape(-1, 1)
```

The image is shape `(H, W)` — a 2-D grid.
`reshape(-1, 1)` flattens to shape `(H*W, 1)`.
`-1` means "figure out this dimension automatically" from the total size.
Result: each row is one pixel, each column is one feature (intensity).
scikit-learn's `KMeans` expects `(n_samples, n_features)`.

```python
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
```

Create a KMeans **object** (an instance of the `KMeans` class).
`n_clusters` — how many clusters to find.
`n_init=10` — run the algorithm 10 times with different starting points and
keep the best result.  More restarts = more reliable results.

```python
    labels = kmeans.fit_predict(X)
```

`fit_predict(X)` does two things in one call:
1. **fit** — runs the K-Means algorithm on `X`, learning the cluster centres.
2. **predict** — assigns each point to its nearest cluster centre.

Returns a 1-D array of cluster labels (integers 0 to n_clusters-1),
one per pixel.  Shape: `(H*W,)`.

```python
    cluster_map = labels.reshape(windowed.shape)
```

Reshape labels back to the image shape `(H, W)` so each pixel position
has its cluster label.  Now we can display it as an image.

```python
    sample_size = min(len(X), 5000)
    rng = np.random.default_rng(random_state)
    idx = rng.choice(len(X), size=sample_size, replace=False)
    score = silhouette_score(X[idx], labels[idx])
```

`silhouette_score` is computationally expensive on large arrays.
**Subsampling:** randomly select up to 5000 pixels to score.
`min(len(X), 5000)` — take 5000 or all pixels if fewer than 5000.
`np.random.default_rng(seed)` — creates a random number generator with
the given seed for reproducibility.
`rng.choice(n, size=k, replace=False)` — pick `k` unique indices from 0..n-1.
`X[idx]` — fancy indexing: select only the rows at those indices.
`silhouette_score(X[idx], labels[idx])` — score the subsample.

```python
    logger.info("Clustering complete: k=%d, silhouette=%.3f", n_clusters, score)
    return windowed, cluster_map, score
```

Log and return all three values.  The caller can unpack them:
`windowed, cluster_map, score = cluster_scan(ds)`.

---

## C6 — `src/scanner_qc.py`

```python
from sklearn.preprocessing import StandardScaler
```

`StandardScaler` transforms features so each has **mean=0 and std=1**.
This is called **standardisation** or **z-score normalisation**.
It prevents features with large absolute values from dominating distance
calculations in K-Means.

```python
@dataclass
class ScanFeatures:
    """Image-level statistics extracted from one DICOM slice."""
    filename: str
    avg_density: float    # Mean pixel value — proxy for overall tissue density
    contrast: float       # Std dev — proxy for image sharpness / dynamic range
    peak_value: float     # Max pixel value — proxy for peak bone/contrast density
```

A simple data container for the three statistics extracted from one file.
The comments after the field type explain the medical interpretation.

```python
def extract_features(folder: str) -> tuple[list[ScanFeatures], np.ndarray]:
```

Returns a tuple of:
1. `list[ScanFeatures]` — one feature record per file.
2. `np.ndarray` — the same data as a matrix: shape `(n_files, 3)`.
   Having both lets callers choose the format they need.

```python
    if not os.path.isdir(folder):
        logger.error("Folder not found: %s", folder)
        return [], np.empty((0, 3))
```

Guard clause: if the folder doesn't exist, return empty results immediately.
`np.empty((0, 3))` — a NumPy array with 0 rows and 3 columns
(valid but empty — shape `(0, 3)`).

```python
    files = sorted(f for f in os.listdir(folder) if not f.startswith("."))
    records: list[ScanFeatures] = []
```

`records: list[ScanFeatures] = []` — annotated type hint on a variable.
Creates an empty list that will hold `ScanFeatures` objects.

```python
    for fname in files:
        full_path = os.path.join(folder, fname)
        try:
            ds = pydicom.dcmread(full_path, force=True)
```

`force=True` — tells pydicom to attempt reading even if the file doesn't
have a proper DICOM preamble (some older scanners omit it).

```python
            pixels = ds.pixel_array.astype(np.float64)
            rec = ScanFeatures(
                filename=fname,
                avg_density=float(np.mean(pixels)),
                contrast=float(np.std(pixels)),
                peak_value=float(np.max(pixels)),
            )
```

`.astype(np.float64)` — convert to 64-bit float before statistics.
`np.mean`, `np.std`, `np.max` — NumPy functions that compute the mean,
standard deviation, and maximum of all pixel values.
`float(...)` — convert NumPy scalar to a plain Python float.

```python
        except Exception as exc:
            logger.warning("Could not process %s: %s", fname, exc)
```

If one file is corrupt, log a warning and continue.  Using `logger.warning`
(not `logger.error`) because this is an expected occasional situation,
not a bug.

```python
    if not records:
        return [], np.empty((0, 3))
```

If no files were successfully processed, return empty results.
`if not records` — `not []` evaluates to `True` (an empty list is "falsy").

```python
    matrix = np.array(
        [[r.avg_density, r.contrast, r.peak_value] for r in records],
        dtype=np.float64,
    )
    return records, matrix
```

**List comprehension inside `np.array()`:**
For each record `r`, create a row `[avg, contrast, peak]`.
The result is a list of lists: `[[…], […], …]`.
`np.array(...)` converts that to a 2-D NumPy array of shape `(n, 3)`.

```python
def run_qc(folder, n_clusters=2, random_state=42):
    records, matrix = extract_features(folder)

    if len(records) < 2:
        logger.warning("Not enough files to cluster (need ≥ 2, got %d).", len(records))
        labels = np.zeros(len(records), dtype=int)
        return records, matrix, labels, float("nan")
```

`np.zeros(n, dtype=int)` — array of `n` zeros (all files in one cluster).
`float("nan")` — Not a Number; used to signal "silhouette score is undefined".

```python
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(matrix)
```

`fit_transform` does two steps:
1. `fit` — compute mean and std of each column.
2. `transform` — subtract mean and divide by std for every value.

Result: each column has mean≈0 and std≈1.

```python
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
```

Same pattern as `clustering.py`.  Now operates on 3 features (per scan)
rather than 1 (per pixel).

```python
    score = silhouette_score(X_scaled, labels) if (n_clusters > 1 and len(records) > n_clusters) else float("nan")
```

**Conditional expression** (ternary): `value_if_true if condition else value_if_false`.
Silhouette score is only defined when: there is more than 1 cluster AND
there are more samples than clusters.  Otherwise return NaN.

```python
    return records, matrix, labels, score
```

Return four values — callers unpack them:
`records, matrix, labels, score = run_qc(folder)`.

---

## C7 — `src/visualization.py`

```python
import matplotlib.pyplot as plt
```

`matplotlib` is the most widely used Python plotting library.
`pyplot` is the sub-module with the main plotting functions.
Importing as `plt` is the universal convention (you will see `plt` in
every matplotlib tutorial).

```python
plt.rcParams.update({"figure.dpi": 100, "axes.titlesize": 11})
```

`rcParams` is matplotlib's global settings dictionary.
`.update(...)` changes multiple settings at once.
This runs once when the module is imported, applying consistent styling
to all plots in the project.

```python
def plot_raw_scan(ds: Dataset, title: str = "CT Slice") -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 6))
```

`plt.subplots()` creates a **figure** and one or more **axes** (plot areas).
- `fig` — the overall container.
- `ax` — the specific plot area to draw on.
- `figsize=(6, 6)` — 6 inches × 6 inches.

```python
    ax.imshow(ds.pixel_array, cmap="gray")
```

`imshow` — display a 2-D array as an image.
`cmap="gray"` — use a greyscale colour map (low values = black, high = white).

```python
    ax.set_title(title)
    ax.axis("off")
    return fig
```

`ax.axis("off")` — hide the axis lines, tick marks, and labels.
Appropriate for images where the coordinate numbers are meaningless.
`return fig` — return the figure; the caller decides whether to show or save.

```python
def plot_windowed_comparison(ds: Dataset) -> plt.Figure:
    presets = list(WINDOW_PRESETS.keys())
    fig, axes = plt.subplots(1, len(presets), figsize=(4 * len(presets), 4))
```

`plt.subplots(1, n)` — 1 row, n columns of plots.
Returns `axes` as a list of `n` Axes objects.
`figsize=(4*n, 4)` — 4 inches wide per plot, 4 inches tall.

```python
    for ax, preset in zip(axes, presets):
```

`zip(list1, list2)` — pairs items: `(axes[0], presets[0])`, then
`(axes[1], presets[1])`, etc.  Same length assumed.

```python
        windowed = window_from_dataset(ds, preset=preset)
        center, width = WINDOW_PRESETS[preset]
        ax.imshow(windowed, cmap="gray")
        ax.set_title(f"{preset.replace('_', ' ').title()}\n(C={center}, W={width})")
```

`str.replace('_', ' ')` — `"soft_tissue"` → `"soft tissue"`.
`.title()` — capitalise each word: `"Soft Tissue"`.
`\n` in a string — newline character (creates a second line in the title).

```python
    fig.suptitle("Windowed Views (same slice)", y=1.02)
    fig.tight_layout()
    return fig
```

`fig.suptitle(...)` — a title for the whole figure (not just one subplot).
`y=1.02` — position it slightly above the top of the plots.
`fig.tight_layout()` — automatically adjust spacing so subplots don't overlap.

```python
def plot_clustering(ds: Dataset, n_clusters: int = 3) -> plt.Figure:
    windowed, cluster_map, silhouette = cluster_scan(ds, n_clusters=n_clusters)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
```

`fig, (ax1, ax2)` — unpacking: `plt.subplots(1, 2)` returns a figure and
an array of 2 Axes; we unpack the array into `ax1` and `ax2`.

```python
    ax2.imshow(cluster_map, cmap="plasma")
```

`cmap="plasma"` — a perceptually uniform colour map from dark purple (0)
to yellow (high).  Good for visualising discrete cluster labels.

```python
def plot_fleet_qc(records, labels, silhouette) -> plt.Figure:
    X = np.array([[r.avg_density, r.contrast] for r in records])
    unique_labels = np.unique(labels)
    colors = plt.cm.tab10(np.linspace(0, 0.5, len(unique_labels)))
```

`np.unique(arr)` — returns sorted unique values.
`plt.cm.tab10` — a colour map with 10 distinct colours.
`np.linspace(0, 0.5, n)` — `n` evenly spaced floats from 0 to 0.5.
Passing these into `plt.cm.tab10(...)` gives n distinct colours.

```python
    for label, color in zip(unique_labels, colors):
        mask = labels == label
        ax.scatter(X[mask, 0], X[mask, 1], s=100, color=color, label=f"Group {label}")
```

`labels == label` — NumPy **boolean mask**: array of True/False,
True where label matches.
`X[mask, 0]` — rows where mask is True, column 0 (avg_density).
`ax.scatter(x, y)` — draw a scatter plot point for each scan in this cluster.
`s=100` — marker size (in points²).
`label=f"Group {label}"` — used in the legend.

```python
    for i, rec in enumerate(records):
        ax.annotate(rec.filename, (X[i, 0], X[i, 1]), ...)
```

`ax.annotate(text, (x, y))` — add a text label next to a point.
`xytext=(5, 5), textcoords="offset points"` — shift label 5 pixels
right and up from the point so text doesn't overlap the dot.

---

## C8 — `tests/test_anonymizer.py`

```python
def _make_dataset(**kwargs) -> Dataset:
```

`**kwargs` — **keyword arguments**: captures any extra arguments as a
dictionary.  `_make_dataset(PatientAge="30")` would set `kwargs = {"PatientAge": "30"}`.
The leading `_` signals this is a private helper, not a test.

```python
    file_meta = pydicom.Dataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.UID("1.2.840.10008.5.1.4.1.1.2")
```

`MediaStorageSOPClassUID` identifies the type of DICOM file.
`"1.2.840.10008.5.1.4.1.1.2"` is the UID for "CT Image Storage".

```python
    ds = FileDataset(filename_or_obj=None, dataset={}, file_meta=file_meta, preamble=b"\0" * 128)
```

`FileDataset` — pydicom class for a complete DICOM file (header + data).
`filename_or_obj=None` — no file on disk, just in memory.
`b"\0" * 128` — the DICOM preamble: 128 null bytes.  The complete DICOM
file format requires 128 null bytes followed immediately by the 4-byte
magic string `"DICM"`.  When you call `ds.save_as(...)`, pydicom
automatically appends the `"DICM"` magic bytes right after the preamble,
so you only need to supply the 128 null bytes here.
`b"..."` is a **bytes literal** — raw binary data, not human-readable text.

```python
class TestTagRemoval:
    def test_phi_tags_removed(self):
        ds = _make_dataset()         # ARRANGE
        anonymize_dataset(ds)        # ACT
        for tag in [...]:
            assert not hasattr(ds, tag), f"{tag} should have been removed"  # ASSERT
```

`assert condition, message` — if `condition` is False, pytest marks the
test as FAILED and shows `message`.
`f"{tag} should have been removed"` — a helpful failure message that tells
you *which* tag was not removed.

```python
    def test_deidentification_method_set(self):
        ...
        assert len(ds.DeidentificationMethod) <= 64, (
            "DeidentificationMethod exceeds VR LO max length of 64 chars"
        )
```

This tests a **DICOM compliance rule**: VR=LO has a maximum length of 64
characters.  The long string `"DICOM PS3.15 Annex E subset..."` is checked
to ensure it fits.

---

## C9 — `tests/test_pipeline.py`

```python
def _write_dicom(path: str, patient_name: str = "Test^Patient") -> None:
    ds.PixelData = np.zeros((4, 4), dtype=np.uint16).tobytes()
```

`np.zeros((4, 4), dtype=np.uint16)` — a 4×4 grid of zeros (16-bit integers).
`.tobytes()` — serialise the NumPy array to raw bytes (binary).
This is what DICOM stores as pixel data — raw bytes, not a NumPy array.

```python
class TestMockUpload:
    def test_upload_eventually_succeeds(self):
        result = mock_upload("test.dcm", failure_rate=0.0)
        assert result is True
```

`failure_rate=0.0` — every attempt succeeds instantly (no random failure).
`is True` — not just truthy, but the exact value `True`.

```python
    def test_upload_fails_when_always_failing(self):
        result = mock_upload(
            "test.dcm",
            failure_rate=1.0,
            max_attempts=3,
            base_delay=0.0,   # ← no delay in tests (fast!)
            max_delay=0.0,
        )
        assert result is False
```

`base_delay=0.0, max_delay=0.0` — set delays to zero so the test
doesn't actually wait 15 seconds.  Tests should be fast.

```python
class TestPipelineCounters:
    def test_upload_failure_increments_failed_not_processed(self, tmp_path):
        from unittest.mock import patch

        with patch("src.pipeline.mock_upload", return_value=False):
```

`unittest.mock.patch` — **replaces** `mock_upload` in `src.pipeline` with
a fake version that always returns `False`.
`with patch(...):` — the replacement is only active inside the `with` block;
the real function is restored afterwards.
This technique is called **mocking** and lets you test error paths without
depending on real network behaviour.

---

## C10 — `tests/test_windowing.py`

```python
def _make_ds_with_pixels(pixels: np.ndarray, slope=1.0, intercept=0.0):
    ds.PixelData = pixels.astype(np.uint16).tobytes()
    ds.RescaleSlope = slope
    ds.RescaleIntercept = intercept
    return ds
```

The helper builds a minimal DICOM Dataset in memory with known pixel
data and rescale parameters.  Tests use this to control exactly what
`window_from_dataset` will compute.

```python
class TestWindowing:
    def test_center_maps_to_half(self):
        hu = np.array([40.0])
        windowed = apply_window(hu, center=40, width=80)
        assert abs(windowed[0] - 0.5) < 1e-9
```

`abs(x - y) < 1e-9` — float comparison.  Never use `==` with floats
because of tiny rounding errors.  `1e-9` = 0.000000001 (essentially zero).
The test verifies that the exact centre of the window maps to 0.5.

```python
    def test_zero_width_raises(self):
        with pytest.raises(ValueError, match="Window width must be > 0"):
```

`pytest.raises(ErrorType, match=pattern)` — asserts that the code inside
raises the specified exception.  `match` checks that the error message
contains the given text (regex pattern).  If no exception is raised,
or a different exception is raised, the test FAILS.

---

## C11 — `tests/test_scanner_qc.py`

```python
def _write_dicom(path: str, mean_value: int = 100) -> None:
    pixels = np.full((4, 4), mean_value, dtype=np.uint16)
```

`np.full(shape, fill_value, dtype)` — create an array filled with
`fill_value`.  A 4×4 grid where every pixel equals `mean_value`.
This gives us precise control over the statistics (mean=mean_value,
std=0, max=mean_value) making tests predictable.

```python
class TestRunQC:
    def test_single_file_returns_nan_silhouette(self, tmp_path):
        ...
        assert math.isnan(score)
```

`math.isnan(x)` — True if `x` is NaN (Not a Number).
`float("nan") == float("nan")` is always `False` in Python (a quirk of
the IEEE 754 floating-point standard).  Always use `math.isnan()` to
check for NaN.

```python
    def test_two_files_with_k2_returns_nan_not_crash(self, tmp_path):
        """With n_samples == n_clusters, silhouette_score is undefined and must not crash."""
```

Documents a **mathematical constraint**: silhouette score requires more
samples than clusters.  With 2 files and k=2, each file is its own cluster
— no meaningful separation to measure.  The test verifies the code handles
this gracefully (returns NaN, does not crash).

---

## Summary — patterns you will recognise everywhere

After reading all 11 source files you will see these patterns repeat:

| Pattern | Where seen | Purpose |
|---------|-----------|---------|
| Module docstring at top | every `.py` | Explain what the file does |
| `logger = logging.getLogger(__name__)` | every `src/` file | Per-module logging |
| Guard clauses (`if not …: return early`) | `pipeline.py`, `scanner_qc.py` | Avoid deep nesting |
| `hasattr / delattr / setattr` loop | `anonymizer.py` | Dynamic attribute manipulation |
| `reshape(-1, 1)` before sklearn | `clustering.py`, `scanner_qc.py` | Prepare data for scikit-learn |
| `try / except Exception` per-item | `pipeline.py`, `scanner_qc.py` | Isolate failures |
| `return fig` in plot functions | `visualization.py` | Decouple rendering from display |
| `assert not hasattr(ds, tag)` | `test_anonymizer.py` | Verify removal |
| `with patch(...):` | `test_pipeline.py` | Replace real functions with fakes |
| `math.isnan(score)` | `test_scanner_qc.py` | NaN-safe float comparison |
| `@dataclass` | `pipeline.py`, `scanner_qc.py` | Structured data containers |
| `field(default_factory=list)` | `pipeline.py` | Mutable default on dataclass |

---

*You have now read and understood every line of every source file.
Go to `docs/02_VSCODE_DEMO_GUIDE.md` to practise presenting this.*
