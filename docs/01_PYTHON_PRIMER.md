# Python Primer — Zero to Codebase-Ready

> **Goal of this document**
>
> You do not need to know Python before reading this.  By the end you will
> understand every Python concept used anywhere in this project.
> Work through it slowly, one section at a time.  Try every example in the
> VS Code terminal as you go.

---

## Table of Contents

| Section | Topic |
|--------:|-------|
| [P1](#p1--how-to-run-python) | How to run Python |
| [P2](#p2--variables-and-print) | Variables and print |
| [P3](#p3--data-types) | Data types |
| [P4](#p4--strings) | Strings |
| [P5](#p5--lists) | Lists |
| [P6](#p6--dictionaries) | Dictionaries |
| [P7](#p7--if--else) | if / else |
| [P8](#p8--for-loops) | for loops |
| [P9](#p9--functions) | Functions |
| [P10](#p10--none-and-optional-values) | None and optional values |
| [P11](#p11--importing-modules) | Importing modules |
| [P12](#p12--classes-and-objects) | Classes and objects |
| [P13](#p13--dataclasses) | Dataclasses |
| [P14](#p14--tryexcept-error-handling) | try / except |
| [P15](#p15--type-hints) | Type hints |
| [P16](#p16--f-strings) | f-strings |
| [P17](#p17--dynamic-attribute-functions-hasattr--getattr--setattr--delattr) | hasattr / getattr / setattr / delattr |
| [P18](#p18--logging) | Logging |
| [P19](#p19--numpy-arrays) | NumPy arrays |
| [P20](#p20--everything-is-an-object) | Everything is an object |

---

## P1 — How to run Python

Python is a programming language — a way of writing instructions that a
computer can follow.  Every Python instruction is a line of text in a file
that ends with `.py`.

**Two ways to run Python:**

### 1. Interactive (type → see result immediately)

Open the VS Code terminal (`Ctrl+`` ` on Windows/Linux, `Cmd+`` ` on Mac)
and type:

```
python
```

You will see `>>>` — that is Python waiting for your input.

```python
>>> 2 + 3
5
>>> print("hello")
hello
>>> exit()
```

Type `exit()` to leave.

### 2. Run a file

Write your code in a `.py` file and run it:

```
python my_script.py
```

---

## P2 — Variables and print

A **variable** is a named box that holds a value.

```python
# The # symbol starts a comment. Python ignores everything after #.
# Comments are notes for humans, not instructions for the computer.

patient_name = "John Doe"     # store a text value
age = 42                      # store a whole number
temperature = 37.5            # store a decimal number
is_anonymized = True          # store True or False
```

**Reading the assignment line:** `variable_name = value`
- Left of `=` is the name (you choose it).
- Right of `=` is the value being stored.
- `=` means *assign*, not *is equal to*.

**`print()`** sends a value to the screen:

```python
print(patient_name)    # → John Doe
print(age)             # → 42
print(is_anonymized)   # → True
```

**Variable naming rules:**
- Only letters, digits, and underscores (`_`).
- Cannot start with a digit.
- Python convention: use `snake_case` (words separated by underscores).
- `PatientName` and `patient_name` are two *different* variables.

---

## P3 — Data types

Every value has a **type** — a category that tells Python what kind of data
it is and what operations it supports.

| Type | Examples | Called |
|------|---------|--------|
| `int` | `42`, `-7`, `0` | Integer (whole number) |
| `float` | `3.14`, `-1024.0`, `0.5` | Floating-point (decimal) |
| `str` | `"hello"`, `'CT'` | String (text) |
| `bool` | `True`, `False` | Boolean (yes/no) |
| `list` | `[1, 2, 3]` | Ordered collection |
| `dict` | `{"key": "value"}` | Key-value mapping |
| `None` | `None` | Absence of a value |

Check the type with `type()`:

```python
print(type(42))          # → <class 'int'>
print(type(3.14))        # → <class 'float'>
print(type("hello"))     # → <class 'str'>
print(type(True))        # → <class 'bool'>
print(type(None))        # → <class 'NoneType'>
```

**Why types matter:**  Python behaves differently depending on type.
`"3" + "4"` gives `"34"` (joining two strings), but `3 + 4` gives `7` (addition).

---

## P4 — Strings

A **string** (`str`) is a sequence of characters enclosed in quotes
(either single `'…'` or double `"…"` — pick one style and be consistent).

```python
name = "Atul Aryan"
greeting = 'Hello, world!'

# Length of a string
print(len(name))           # → 10  (number of characters)

# Access one character (zero-based indexing)
print(name[0])             # → 'A'   (first character)
print(name[-1])            # → 'n'   (last character)

# Slice (a portion)
print(name[0:4])           # → 'Atul'

# Methods — built-in operations on strings
print(name.upper())        # → 'ATUL ARYAN'
print(name.lower())        # → 'atul aryan'
print(name.replace("Aryan", "Singh"))  # → 'Atul Singh'
print("  hello  ".strip()) # → 'hello'  (remove surrounding whitespace)

# Check if a string starts/ends with something
print(name.startswith("At"))  # → True
print(name.endswith("an"))    # → True
```

**In this project strings are used for:** file paths, patient names, tag
names, log messages, config values.

---

## P5 — Lists

A **list** (`list`) is an ordered, changeable collection of values.
You can put anything inside a list — even other lists.

```python
tags_to_remove = ["PatientName", "PatientID", "PatientBirthDate"]

# Access by position (zero-based)
print(tags_to_remove[0])   # → 'PatientName'
print(tags_to_remove[1])   # → 'PatientID'
print(tags_to_remove[-1])  # → 'PatientBirthDate'  (last element)

# Length
print(len(tags_to_remove)) # → 3

# Append an item to the end
tags_to_remove.append("InstitutionName")
print(len(tags_to_remove)) # → 4

# Loop over every item
for tag in tags_to_remove:
    print(tag)
# prints PatientName, PatientID, PatientBirthDate, InstitutionName one per line

# Check membership
print("PatientID" in tags_to_remove)     # → True
print("Modality" in tags_to_remove)      # → False

# Sort a list (alphabetical for strings, numerical for numbers)
sorted_tags = sorted(tags_to_remove)
```

**`sorted(...)` vs `.sort()`:**
- `sorted(my_list)` returns a *new* sorted list; original unchanged.
- `my_list.sort()` sorts the list *in place*; returns nothing.

**List comprehension — a compact way to build a list:**

```python
# Long way
files = []
for f in [".", ".hidden", "scan1.dcm", "scan2.dcm"]:
    if not f.startswith("."):
        files.append(f)

# Short way (list comprehension) — exactly the same result
files = [f for f in [".", ".hidden", "scan1.dcm", "scan2.dcm"] if not f.startswith(".")]
print(files)  # → ['scan1.dcm', 'scan2.dcm']
```

You will see this pattern everywhere in this codebase to filter file lists.

---

## P6 — Dictionaries

A **dictionary** (`dict`) maps *keys* to *values* — like a real dictionary
maps words to definitions.

```python
config = {
    "input_folder":  "data/raw",
    "output_folder": "data/processed",
    "max_files":     5,
}

# Read a value by its key
print(config["input_folder"])   # → 'data/raw'

# Change a value
config["max_files"] = 10

# Add a new key-value pair
config["reports_folder"] = "reports"

# Check if a key exists
print("max_files" in config)    # → True

# Loop over keys
for key in config:
    print(key, "→", config[key])

# Loop over key-value pairs simultaneously
for key, value in config.items():
    print(f"{key}: {value}")

# Nested dictionaries — a value that is itself a dict
settings = {
    "paths": {
        "input_folder": "data/raw",
    },
    "pipeline": {
        "max_files": None,
    },
}

# Access nested values with chained [ ][ ]
print(settings["paths"]["input_folder"])   # → 'data/raw'
```

**This is exactly how `config.yaml` is loaded** — YAML text becomes a nested
Python dict.

---

## P7 — if / else

`if` runs code only when a condition is True.

```python
tag_name = "PatientName"
is_present = True

if is_present:
    print("Tag exists, will delete it")   # runs only when is_present is True

# if / else
if tag_name == "PatientName":
    print("This is the patient name tag")
else:
    print("This is some other tag")

# if / elif / else  (elif = "else if")
value = 42
if value < 0:
    print("negative")
elif value == 0:
    print("zero")
else:
    print("positive")
```

**Comparison operators:**

| Operator | Meaning |
|----------|---------|
| `==` | Equal to |
| `!=` | Not equal to |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |
| `is` | Identical object (used with `None`) |
| `is not` | Not the same object |
| `in` | Member of a list/dict |
| `not` | Flip True↔False |

```python
# Common pattern in this codebase
max_files = None

if max_files is not None:
    files = files[:max_files]   # slice the list
```

`None` represents "no value" / "not set".  Always check `is None` or
`is not None`, never `== None`.

---

## P8 — for loops

A `for` loop repeats code once for each item in a sequence.

```python
filenames = ["scan1.dcm", "scan2.dcm", "scan3.dcm"]

for filename in filenames:
    print("Processing:", filename)
# prints each filename in turn

# range() generates numbers
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 4):       # 1, 2, 3
    print(i)

# enumerate() gives both index and value
for index, filename in enumerate(filenames):
    print(f"File {index + 1}: {filename}")
# File 1: scan1.dcm
# File 2: scan2.dcm
# File 3: scan3.dcm
```

**`break` and `continue`:**

```python
for attempt in range(5):
    if attempt == 2:
        continue          # skip this iteration, jump to next
    if attempt == 4:
        break             # stop the loop entirely
    print(attempt)
# prints 0, 1, 3
```

**In this codebase** `for` loops are used to:
- Iterate over every file in a folder
- Iterate over every tag name in a list
- Iterate over every key-value pair in a dict

---

## P9 — Functions

A **function** is a named, reusable block of code.  You *define* it once
and *call* it as many times as you need.

```python
# Define a function with 'def'
def greet(name):
    """This is a docstring — a description of what the function does."""
    message = "Hello, " + name + "!"
    return message          # return sends a value back to the caller

# Call the function
result = greet("Atul")
print(result)               # → Hello, Atul!
```

**Parameters with default values** (optional arguments):

```python
def anonymize(ds, station_name="REMOTE_MOBILE_01"):
    #                          ↑ default value — used if caller doesn't pass one
    ds.StationName = station_name
    return ds

anonymize(my_dataset)                         # uses default
anonymize(my_dataset, station_name="VAN_02")  # overrides default
```

**Multiple return values** — Python can return a tuple:

```python
def cluster_scan(ds):
    windowed = ...
    cluster_map = ...
    score = 0.85
    return windowed, cluster_map, score    # returns three values at once

# Unpack the three values on the left
img, labels, silhouette = cluster_scan(ds)
```

**Why functions:**
- Avoid repeating the same code in multiple places.
- Give a name to a piece of logic so the code reads like English.
- Make code testable: you can test one function without running the whole program.

---

## P10 — None and Optional values

`None` is Python's way of saying "nothing here" or "not provided".

```python
max_files = None

# Check if something is None
if max_files is None:
    print("Process all files")
else:
    print(f"Process only {max_files} files")
```

**`Optional[str]`** in function signatures means: "this argument can be
either a `str` or `None`".

```python
from typing import Optional

def process_folder(
    input_folder: Optional[str] = None,   # caller can pass None or omit it
) -> None:
    if input_folder is None:
        input_folder = "data/raw"         # use default
```

---

## P11 — Importing modules

A **module** is a Python file.  An **import** lets you use code from one
file inside another.

```python
# Import the whole module — use it as module.function()
import os
import time

os.path.join("data", "raw", "scan.dcm")   # → 'data/raw/scan.dcm'
time.sleep(1.0)                            # pause for 1 second

# Import specific names from a module — use them directly
from typing import Optional
from dataclasses import dataclass

# Import with an alias (shorter name)
import numpy as np
arr = np.array([1, 2, 3])
```

**The `os` module** — file-system operations:

```python
import os

os.path.join("data", "raw")           # 'data/raw' (safe path joining)
os.path.exists("config.yaml")         # True or False
os.path.isdir("data/raw")             # True if folder exists
os.listdir("data/raw")                # list of filenames in folder
os.makedirs("data/processed", exist_ok=True)  # create folder, no error if already exists
os.path.abspath(__file__)             # absolute path to the current script
os.path.dirname("/a/b/c.py")         # '/a/b'
os.path.basename("/a/b/c.py")        # 'c.py'
```

---

## P12 — Classes and objects

A **class** is a blueprint.  An **object** (also called an *instance*) is
one specific thing made from that blueprint.

**Analogy:** A "CT Scanner" is the class (blueprint).
"Scanner #A001 in Van 3" is one specific instance.

```python
class Scanner:
    """Represents one physical CT scanner."""

    def __init__(self, serial_number, location):
        # __init__ runs when you create a new instance.
        # 'self' refers to the specific instance being created.
        self.serial_number = serial_number   # store on the instance
        self.location = location

    def describe(self):
        # A method — a function that belongs to this class.
        # 'self' always comes first; it receives the instance automatically.
        return f"Scanner {self.serial_number} in {self.location}"


# Create two instances
scanner_a = Scanner("SN001", "Van 3")
scanner_b = Scanner("SN002", "Van 7")

print(scanner_a.describe())   # → Scanner SN001 in Van 3
print(scanner_b.describe())   # → Scanner SN002 in Van 7
print(scanner_a.serial_number) # → SN001
```

**`self`** is just a variable name (the most common convention) for "the
current instance".  Python passes it automatically when you call a method.

```python
scanner_a.describe()        # Python turns this into:
Scanner.describe(scanner_a) # exactly the same call
```

In this codebase, `pydicom.Dataset` is a class.  When you call
`ds = pydicom.dcmread("scan.dcm")`, `ds` is an *instance* of `Dataset`.
`ds.PatientName` is an *attribute* of that instance.

---

## P13 — Dataclasses

A **dataclass** is a shortcut for creating simple classes that mainly
store data.  Writing `@dataclass` above a class definition tells Python
to automatically generate `__init__` (and other boilerplate) for you.

```python
from dataclasses import dataclass, field

# Without dataclass — lots of boilerplate
class ProcessingResultManual:
    def __init__(self, filename, success, error=None, duration_s=0.0):
        self.filename   = filename
        self.success    = success
        self.error      = error
        self.duration_s = duration_s

# With @dataclass — much cleaner
@dataclass
class ProcessingResult:
    filename:   str
    success:    bool
    error:      str | None = None   # optional, defaults to None
    duration_s: float = 0.0         # optional, defaults to 0.0
```

Both are *identical* in behaviour.  The dataclass is just less typing.

**`field(default_factory=list)`** — used when the default is a mutable
object (like a list) that should not be shared across all instances:

```python
@dataclass
class PipelineReport:
    total_files: int   = 0
    results: list = field(default_factory=list)
    #                   ↑ each new PipelineReport gets its OWN empty list
```

---

## P14 — try / except: error handling

When something goes wrong at runtime, Python raises an **exception** —
a signal that an error occurred.  Without handling it, the program crashes.

```python
# Without error handling — crashes if file does not exist
ds = pydicom.dcmread("missing.dcm")   # FileNotFoundError!

# With error handling
try:
    ds = pydicom.dcmread("missing.dcm")
    print("Loaded OK")
except FileNotFoundError:
    print("File does not exist — skipping")
except Exception as exc:
    # 'except Exception' catches any other error
    # 'as exc' binds the error object to the name 'exc'
    print(f"Unexpected error: {exc}")
```

**How try/except flows:**
1. Python tries to run the code inside `try`.
2. If an error occurs, it jumps to the matching `except` block.
3. Code after the `except` continues normally.
4. If no error occurs, the `except` block is skipped.

**In `pipeline.py` this pattern wraps the per-file processing** so that
one bad file does not crash the whole batch:

```python
for filename in files:
    try:
        ds = pydicom.dcmread(full_path)
        anonymize_dataset(ds)
        ds.save_as(output_path)
    except Exception as exc:
        result.error = str(exc)   # record what went wrong
        report.failed += 1        # count it as failed
        # loop continues with the next file
```

---

## P15 — Type hints

**Type hints** are annotations that tell you (and your editor) what type
a variable or parameter is expected to be.  Python does NOT enforce them
at runtime — they are documentation for humans and tools.

```python
# Basic type hints on variables
name: str = "John"
age: int = 42
score: float = 0.85
is_done: bool = False

# Type hints on function parameters and return value
def greet(name: str) -> str:
    return "Hello, " + name

def process(files: list[str]) -> None:  # → None means returns nothing
    for f in files:
        print(f)
```

**`Optional[X]`** — can be X or None:

```python
from typing import Optional

def get_window(center: Optional[float] = None) -> float:
    if center is None:
        return 40.0       # default
    return center
```

**`dict[str, Any]`** — a dictionary with string keys and values of any type:

```python
from typing import Any

def load_config() -> dict[str, Any]:
    ...
```

**Why use type hints:**
1. Your editor (VS Code) can autocomplete and catch mistakes.
2. Other developers immediately know what to pass and what to expect.
3. Tools like `mypy` can statically check your whole codebase for type errors.

---

## P16 — f-strings

**f-strings** are the modern way to embed values inside a string.
Write `f"..."` and put expressions in `{...}`:

```python
filename = "scan_01.dcm"
attempt = 2
max_attempts = 5

# Old way (confusing)
msg = "Upload attempt " + str(attempt) + "/" + str(max_attempts) + " for " + filename

# f-string (clear and readable)
msg = f"Upload attempt {attempt}/{max_attempts} for {filename}"
# → 'Upload attempt 2/5 for scan_01.dcm'

# Formatting numbers
score = 0.87654
print(f"Silhouette score: {score:.3f}")   # → 'Silhouette score: 0.877'
# .3f means: fixed-point format with 3 decimal places

duration = 1.2
print(f"Time: {duration:.2f}s")           # → 'Time: 1.20s'
```

---

## P17 — Dynamic attribute functions: hasattr / getattr / setattr / delattr

These four built-in functions inspect and manipulate object attributes
*dynamically* — using strings as the attribute name instead of writing
it directly in the code.  They are the heart of the anonymizer.

```python
class MyObject:
    patient_name = "John"
    patient_id   = "12345"

obj = MyObject()

# hasattr — check whether an attribute exists
print(hasattr(obj, "patient_name"))   # → True
print(hasattr(obj, "modality"))       # → False

# getattr — get the value of an attribute by name
print(getattr(obj, "patient_name"))   # → 'John'
print(getattr(obj, "missing", "N/A")) # → 'N/A'  (third arg = default)

# setattr — set (create or overwrite) an attribute by name
setattr(obj, "patient_name", "ANONYMOUS")
print(obj.patient_name)               # → 'ANONYMOUS'

# delattr — delete an attribute by name
delattr(obj, "patient_id")
print(hasattr(obj, "patient_id"))     # → False
```

**Why use these instead of writing `obj.patient_name` directly?**

The anonymizer loops over a *list* of tag names:

```python
TAGS_TO_REMOVE = ["PatientName", "PatientID", "AccessionNumber", ...]

for tag_name in TAGS_TO_REMOVE:
    if hasattr(ds, tag_name):     # tag_name is a string variable
        delattr(ds, tag_name)     # cannot write ds.PatientName — name is unknown at write-time
```

If the list has 25 tags you would otherwise need 25 individual `if hasattr…
delattr` blocks.  The dynamic approach handles any length list with 2 lines.

---

## P18 — Logging

**Logging** is a way to write status messages that is more powerful than
`print()`.  Messages have a *level* (severity):

| Level | When to use |
|-------|-------------|
| `DEBUG` | Detailed internal steps (usually hidden in production) |
| `INFO` | Normal progress ("file saved", "pipeline started") |
| `WARNING` | Something unusual but not fatal |
| `ERROR` | A step failed; program continues |
| `CRITICAL` | Entire system is broken |

```python
import logging

# --- Setup (done once per module) ---
logger = logging.getLogger(__name__)
# __name__ is automatically set to the module's name (e.g. "src.anonymizer")
# This lets you filter logs by module in production.

# --- Usage ---
logger.debug("Removed tag: %s", "PatientName")
logger.info("Pipeline started: %d files to process.", 10)
logger.warning("No window parameters found; using default.")
logger.error("Input folder not found: %s", "/missing/path")
```

**Why `%s` placeholders instead of f-strings?**
Log messages with `%s` are only formatted if the message is actually
displayed.  If you set the log level to `ERROR`, `DEBUG` messages are
silently dropped *without* doing any string formatting — a small
performance win in tight loops.

**Setting up logging in a script:**

```python
import logging

logging.basicConfig(
    level=logging.INFO,           # show INFO and above; hide DEBUG
    format="%(levelname)-8s %(message)s",
)
```

---

## P19 — NumPy arrays

**NumPy** (`import numpy as np`) provides fast multi-dimensional arrays.
CT scan pixel data is stored as a NumPy array.

```python
import numpy as np

# Create arrays
a = np.array([1, 2, 3, 4])        # 1-D array, shape (4,)
b = np.array([[1, 2], [3, 4]])     # 2-D array (matrix), shape (2, 2)

# Shape — dimensions
print(a.shape)    # → (4,)
print(b.shape)    # → (2, 2)

# Data type
print(a.dtype)    # → int64

# Change type
c = a.astype(np.float64)   # convert to 64-bit float

# Math on every element at once (no for loop needed)
result = a * 2 + 1          # → array([3, 5, 7, 9])

# Statistics
print(np.mean(a))           # → 2.5
print(np.std(a))            # → 1.118...
print(np.max(a))            # → 4
print(np.min(a))            # → 1

# Clip — cap values to a range
clipped = np.clip(a, 2, 3)  # → array([2, 2, 3, 3])

# Reshape — change shape without changing data
row = np.array([1, 2, 3, 4, 5, 6])
grid = row.reshape(2, 3)    # shape (2, 3)

# Flatten — collapse to 1-D
flat = grid.reshape(-1)     # or grid.flatten()
# -1 means "figure out this dimension automatically"

# reshape(-1, 1) — very common in this project!
# Turns (H, W) image into (H*W, 1) column for scikit-learn
X = grid.reshape(-1, 1)     # shape (6, 1)
```

**Why reshape(-1, 1)?**
scikit-learn's `KMeans.fit_predict()` expects input in shape
`(n_samples, n_features)`.  Our image is `(rows, cols)` = one feature
per pixel, so we reshape to `(rows*cols, 1)`.

---

## P20 — Everything is an object

In Python, literally *everything* is an object — integers, strings,
functions, modules, classes themselves.  This has one practical consequence
you will see in the codebase:

```python
# A string has methods (functions belonging to it)
"hello".upper()         # → 'HELLO'

# A list has methods
[3, 1, 2].sort()        # sorts in place

# A function can be passed as an argument
def apply(fn, value):
    return fn(value)

result = apply(str.upper, "hello")   # → 'HELLO'
```

You do not need to memorise all of this.  The key insight is:
**when you see `something.method()`, ask "what type is `something`?"**
and look up what methods that type has.

---

## Quick Reference — Python constructs used in this project

| Construct | Example | Where in this project |
|-----------|---------|----------------------|
| Variable | `max_files = 5` | everywhere |
| List | `["PatientName", "PatientID"]` | `anonymizer.py` |
| Dict | `{"input": "data/raw"}` | `config.py` |
| for loop | `for tag in TAGS_TO_REMOVE:` | `anonymizer.py` |
| if / else | `if hasattr(ds, tag):` | `anonymizer.py` |
| Function | `def anonymize_dataset(ds):` | all `src/` files |
| Class | `class ScanFeatures:` | `scanner_qc.py` |
| @dataclass | `@dataclass class PipelineReport:` | `pipeline.py` |
| Import | `import os`, `from src.config import CONFIG` | all files |
| try/except | `try: … except Exception as exc:` | `pipeline.py` |
| f-string | `f"Attempt {n}/{max}"` | `pipeline.py` |
| hasattr | `if hasattr(ds, tag_name):` | `anonymizer.py` |
| delattr | `delattr(ds, tag_name)` | `anonymizer.py` |
| setattr | `setattr(ds, tag_name, value)` | `anonymizer.py` |
| logging | `logger.info("Done")` | all `src/` files |
| NumPy | `np.clip(hu, lower, upper)` | `windowing.py` |
| Type hints | `def fn(x: str) -> int:` | all `src/` files |

---

*You now know every Python concept used in this codebase.
Next: open `docs/03_CODE_WALKTHROUGH.md` for line-by-line annotation of every source file.*
