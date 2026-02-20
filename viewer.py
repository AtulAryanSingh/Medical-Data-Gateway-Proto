# =============================================================================
# viewer.py — Step 3: Single-Scan Verification (Quality Assurance Check)
# =============================================================================
# PURPOSE: After the batch processor runs, we want to verify that a specific
# processed file looks correct — both its metadata AND its image.
# This script is a QA (Quality Assurance) checkpoint in the pipeline.
#
# CONCEPT — QA Checkpoint in a Pipeline:
#   In any data pipeline, you insert verification steps between stages to
#   confirm the previous stage produced the expected output before you
#   continue.  A pipeline without QA checkpoints is like an assembly line
#   with no inspection stations — defects propagate undetected.
#
# CONCEPT — Single-file vs Batch:
#   This script loads ONE specific file by name.  This is intentional —
#   for QA you want to inspect individual records, not the entire batch.
#   The batch-level view comes later in miner.py.
#
# PIPELINE POSITION:  … → Batch Processor → [Viewer (QA)] → Density Plot → Miner
# =============================================================================

# --- IMPORTS ---
import pydicom              # Read DICOM files (same as every other script).
import matplotlib.pyplot as plt   # Display images in a graphical window.
import os                   # Check file existence with os.path.exists().

# =============================================================================
# CONFIGURATION
# =============================================================================
# We hard-code the folder and filename to inspect a specific processed scan.
# In production you would accept these as command-line arguments (via argparse)
# so you can inspect any file without editing the script.

folder_path = "batch_anonymized"   # The folder batch_processor.py created.
filename    = "Clean_I10.dcm"      # The specific file we want to inspect.
                                   # "Clean_" prefix confirms it went through
                                   # the batch processor (see batch_processor.py).

# os.path.join() safely combines folder + filename into a full path.
# e.g. "batch_anonymized" + "Clean_I10.dcm" → "batch_anonymized/Clean_I10.dcm"
full_path = os.path.join(folder_path, filename)

# =============================================================================
# STEP 1 — Safety Check
# =============================================================================
# PATTERN — Guard Clause / Early Return:
#   Check preconditions at the TOP of a function or script and exit early
#   if they are not met.  This avoids deeply nested if-statements and makes
#   the "happy path" (normal execution) easy to read.

if not os.path.exists(full_path):
    print(f"ERROR: could not find {full_path}")
    print("Did you run the batch processor first?")
    exit()   # Terminate immediately — no point continuing without the file.

# =============================================================================
# STEP 2 — Load the DICOM file
# =============================================================================
# Same as in inspector.py and anonymizer.py.  This returns a FileDataset
# object with both metadata attributes and the pixel array.

ds = pydicom.dcmread(full_path)

# =============================================================================
# STEP 3 — Verify the metadata (confirm anonymization worked)
# =============================================================================
# These print statements let us visually confirm that:
#   PatientName → should be "ANONYMOUS"  (not the real name)
#   PatientID   → should be "00000"      (not the real ID)
#
# This is the "Verify" step of Read-Modify-Verify lifecycle.

print(f"Patient Name: {ds.PatientName}")     # Expected: ANONYMOUS
print(f"Patient ID:   {ds.PatientID}")       # Expected: 00000

# Rows and Columns are standard DICOM metadata tags that tell us the
# image dimensions (height × width in pixels).
# For a CT skull scan: typically 512 × 512 pixels.
print(f"Image size: {ds.Rows} x {ds.Columns} pixels")

# =============================================================================
# STEP 4 — Display the pixel data as a greyscale image
# =============================================================================
# CONCEPT — pixel_array (repeated for reinforcement):
#   ds.pixel_array returns a 2-D NumPy array of integers.
#   Each integer is the brightness of one pixel.
#   plt.imshow() renders that array as a colour image using a colour map.
#
# cmap=plt.cm.bone:
#   The "bone" colour map is specifically designed for skeletal imaging.
#   It maps low pixel values → dark (representing air or soft tissue)
#   and high pixel values → bright white (representing dense bone).
#   Using the correct colour map makes anatomical structures immediately
#   recognisable to a clinician — this matters for rapid triage.

print("Displaying image...")

plt.imshow(ds.pixel_array, cmap=plt.cm.bone)

# plt.title() adds a label at the top of the figure.
# ds.PatientName is now "ANONYMOUS" — this is intentional: we are proving
# that the image has been anonymized while still being clinically usable.
plt.title(f"CT Slice: {ds.PatientName}")

# plt.axis('off') hides the X and Y axis tick marks and labels.
# For medical images, the axes carry no clinical meaning and just add
# visual noise — removing them is standard practice in medical imaging UIs.
plt.axis('off')

# plt.show() opens the matplotlib interactive window.
# Execution pauses here until the user closes the window.
plt.show()

# =============================================================================
# KEY INTERVIEW TALKING POINTS for this file:
# =============================================================================
# Q: "What is a QA checkpoint in a data pipeline?"
# A: A verification step between pipeline stages that confirms the previous
#    stage produced valid output.  Catches errors early, before they propagate
#    and become expensive to fix downstream.
#
# Q: "What is a guard clause / early return pattern?"
# A: Checking preconditions at the top of a block and exiting immediately
#    if they fail.  Keeps code flat and readable by avoiding deep nesting.
#
# Q: "What does ds.Rows and ds.Columns tell you?"
# A: The image dimensions in pixels (height × width).  Standard DICOM tags
#    (0028,0010) and (0028,0011).  A 512×512 CT slice is very common.
#
# Q: "Why use cmap='bone' for CT images?"
# A: It mimics the visual appearance of traditional film X-rays that
#    radiologists are trained on, making dense structures (bone) appear
#    white and air appear black — clinically intuitive and reduces
#    interpretation errors.
# =============================================================================