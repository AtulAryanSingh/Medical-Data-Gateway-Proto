# =============================================================================
# anonymizer.py — Step 1: The Privacy / GDPR Layer
# =============================================================================
# PURPOSE: Strip every piece of Personally Identifiable Information (PII)
# from a DICOM scan *before* it leaves the mobile truck and travels over the
# network to the cloud.  This is not optional — it is a legal requirement
# under GDPR (Europe) and HIPAA (USA).
#
# CONCEPT — Data Minimisation (GDPR Article 5(1)(c)):
#   Only the data strictly necessary for the medical purpose should be
#   transmitted.  Patient names and IDs are not needed for image analysis —
#   therefore they must be removed at the source (the "edge").
#
# CONCEPT — Edge vs Cloud Processing:
#   "Edge" means processing happens on the device closest to the data source
#   (the truck's laptop / Raspberry Pi) rather than in a central server.
#   Edge processing is faster, cheaper on bandwidth, and safer for privacy.
#
# PIPELINE POSITION:  Inspector → [Anonymizer] → Batch Processor → …
# =============================================================================

# --- IMPORTS ---
import pydicom   # Read and write DICOM files.  Same as inspector.py.
import os        # Operating System interface: check if files/folders exist,
                 # build file paths, etc.
                 # "os" is part of Python's standard library — no pip needed.

# =============================================================================
# CONFIGURATION — Define what we read and what we produce
# =============================================================================
# It is good practice to put file names at the TOP of the script as named
# constants so that anyone reading the code immediately knows the inputs/outputs.

input_file  = "test_scan.dcm"       # The raw DICOM file straight from the scanner.
output_file = "anonymized_scan.dcm" # The cleaned file that is safe to transmit.

print(f"--- Processing {input_file} ---")
# f-string (formatted string literal): the f"…{variable}…" syntax embeds the
# value of `input_file` directly inside the string at runtime.
# Equivalent to:  "--- Processing " + input_file + " ---"

# =============================================================================
# STEP 1 — Safety Check: does the input file actually exist?
# =============================================================================
# CONCEPT — Defensive Programming:
#   Never assume a file exists. Always validate inputs before doing work.
#   os.path.exists() returns True/False — it does NOT open the file.
#   This prevents confusing "AttributeError" crashes later.

if not os.path.exists(input_file):
    # The `not` inverts the boolean: we enter this block when the file is MISSING.
    print("ERROR: File not found! Did you rename your file to 'test_scan.dcm'?")
    exit()   # exit() immediately terminates the Python process with status 0.
             # Use this sparingly — in production you would raise an Exception.

# =============================================================================
# STEP 2 — Load the DICOM file into memory
# =============================================================================
# pydicom.dcmread() reads the .dcm binary file and returns a FileDataset object.
# This object (ds) behaves like a Python dictionary where:
#   Key   = DICOM tag name (e.g., "PatientName")
#   Value = The actual data (e.g., "Smith^John")
# After this line, `ds` holds the entire file in RAM — both header AND pixels.

ds = pydicom.dcmread(input_file)

# =============================================================================
# STEP 3 — Inspect the "Before" state (for verification)
# =============================================================================
# Printing the ORIGINAL values lets us confirm the anonymization actually worked
# when we do the "After" comparison at the end.
# In DICOM, PatientName is stored as "FamilyName^GivenName" by convention.

print(f"ORIGINAL Patient Name: {ds.PatientName}")
print(f"ORIGINAL Patient ID:   {ds.PatientID}")

# =============================================================================
# STEP 4 — Apply the Anonymization (the core "business logic")
# =============================================================================
# CONCEPT — Mutation vs Immutability:
#   We are mutating (changing in-place) the `ds` object.  We are NOT creating
#   a new copy — we are overwriting the fields on the existing object.
#   This is a "destructive" operation on the in-memory object (the file on
#   disk is unchanged until we call ds.save_as()).

ds.PatientName = "ANONYMOUS"   # Replace real name with a placeholder string.
                               # "ANONYMOUS" is the de-facto standard marker in
                               # medical imaging research datasets.

ds.PatientID   = "00000"       # Replace real hospital ID with a neutral zero.
                               # Using "00000" is a clear visual signal that
                               # this field has been intentionally wiped.

# =============================================================================
# STEP 5 — Add the "Source" Tag (the pipeline provenance tag)
# =============================================================================
# CONCEPT — Data Provenance / Lineage:
#   When data flows through a pipeline with many steps, you always want to
#   know WHERE each file originated.  The DICOM tag "StationName" is a
#   standard field meant to record the scanning station's name.
#   We repurpose it to carry our edge-device ID so the cloud server can
#   immediately know which mobile clinic produced this scan.
#   This is critical for: fleet analytics, fault attribution, audit logging.

ds.StationName = "REMOTE_MOBILE_CLINIC_01"
print('Added Tag: StationName -> "REMOTE_MOBILE_CLINIC_01"')

# =============================================================================
# STEP 6 — Write the modified file back to disk
# =============================================================================
# ds.save_as() serialises the in-memory FileDataset object back into the
# binary DICOM format and writes it to the path you provide.
# Note: we write to `output_file` (a NEW path), so the original file is
# preserved unchanged — good practice for "non-destructive" pipelines.

ds.save_as(output_file)

print("-" * 30)          # Print a decorative horizontal line for readability.
print("SUCCESS: File anonymized and saved.")
print(f"New file created: {output_file}")

# =============================================================================
# STEP 7 — Verification: Re-read the output file and confirm the changes
# =============================================================================
# CONCEPT — Round-Trip Verification:
#   After every write operation, best practice is to READ BACK what you wrote
#   and assert it matches your expectations.  This guards against subtle bugs
#   where save_as() might silently fail or save stale data.
#
# We store the re-read dataset in a DIFFERENT variable (new_ds) to avoid
# confusion with the original `ds` object.

new_ds = pydicom.dcmread(output_file)
print(f"CHECKING NEW FILE -> Patient Name is now: {new_ds.PatientName}")
# Expected output: "ANONYMOUS"
# If you see the original name here, the save_as() failed silently.

# =============================================================================
# KEY INTERVIEW TALKING POINTS for this file:
# =============================================================================
# Q: "Why do we anonymize at the edge rather than in the cloud?"
# A: Sending PII over the network, even over HTTPS, increases exposure.
#    Anonymizing at the source (edge) means PII never leaves the truck —
#    eliminating network-borne data leakage risk entirely.
#
# Q: "What GDPR principle does this implement?"
# A: Data Minimisation (Article 5) — only transmit what is necessary.
#    Also Storage Limitation and Purpose Limitation.
#
# Q: "What is the StationName tag used for?"
# A: It is a provenance / lineage tag.  It tells every downstream system
#    (dashboard, PACS, analytics engine) which physical device produced the
#    scan, enabling fleet-level quality control and audit trails.
#
# Q: "Why save to a new file instead of overwriting the original?"
# A: Non-destructive pipelines preserve the original so you can re-run or
#    audit the process.  Overwriting originals is a data-engineering anti-pattern.
# =============================================================================