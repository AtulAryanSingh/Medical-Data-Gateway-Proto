# =============================================================================
# batch_processor.py — Step 2: The Resilience / Ingestion Layer
# =============================================================================
# PURPOSE: Process an entire FOLDER of DICOM files one-by-one, applying
# anonymization to each, then simulate uploading each file to the cloud.
# The key engineering challenge here is RESILIENCE: mobile clinics operate
# on unstable 4G/LTE connections, so the upload logic must gracefully handle
# network drops without losing any scan.
#
# CONCEPT — Batch Processing:
#   Instead of processing one file at a time (like anonymizer.py), a batch
#   processor runs a loop over a collection.  This is the foundation of every
#   data pipeline — ETL (Extract, Transform, Load) systems do exactly this:
#     Extract  = read from source folder
#     Transform = anonymize + tag
#     Load     = upload to cloud
#
# CONCEPT — Exponential Backoff:
#   When a network request fails, a naive retry immediately hits the server
#   again — but the server is probably still overloaded.  Exponential Backoff
#   waits progressively longer between retries (1s, 2s, 4s, 8s …).
#   This is used by AWS, Google Cloud, and virtually every production API.
#   Here we simulate it with fixed sleep times for simplicity.
#
# CONCEPT — Mock / Simulation:
#   We cannot actually connect to the internet in this prototype, so we
#   MOCK the upload with a fake function.  Mocking is a fundamental
#   software engineering technique used in testing ("unit tests" mock
#   external dependencies so you can test your logic in isolation).
#
# PIPELINE POSITION:  Inspector → Anonymizer → [Batch Processor] → Density Plot
# =============================================================================

# --- IMPORTS ---
import pydicom   # Read/write DICOM files.
import os        # File system: check folders, list files, join paths.
import time      # time.sleep(seconds) — pause execution for N seconds.
                 # Used to simulate network latency and retry delays.
import random    # Generate pseudo-random numbers.
                 # random.random() returns a float in [0.0, 1.0).
                 # We use it to randomly simulate a 30% network failure rate.

# =============================================================================
# CONFIGURATION — Define input and output locations
# =============================================================================
# input_folder: Where the raw DICOM files live.
#   "2_skull_ct/DICOM" is the folder structure typical of DICOM exports —
#   each study gets its own numbered folder.
#
# output_folder: Where we save the anonymized/processed files.
#   Using a separate folder keeps originals untouched (non-destructive pipeline).

input_folder  = "2_skull_ct/DICOM"
output_folder = "batch_anonymized"

# =============================================================================
# STEP 1 — Create the output folder if it doesn't already exist
# =============================================================================
# CONCEPT — Idempotency:
#   A good pipeline can be run multiple times without causing errors.
#   Checking `not os.path.exists(output_folder)` before calling makedirs()
#   makes this step IDEMPOTENT — running it twice is safe.
#   os.makedirs() creates the folder AND any missing parent directories.

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# =============================================================================
# STEP 2 — Build a list of files to process
# =============================================================================
# os.listdir(path) returns a Python list of all filenames in the folder.
# PITFALL: On macOS, hidden files like ".DS_Store" appear in the listing.
# The filter `not f.startswith('.')` skips all dot-files — a common idiom
# in data engineering scripts that need to be OS-agnostic.
#
# List Comprehension syntax: [expression  for item in iterable  if condition]
# This single line replaces a 4-line for-loop + if-statement.  It is Pythonic.

files = [f for f in os.listdir(input_folder) if not f.startswith('.')]

print(f"Starting batch processing of {len(files)} files...")
# len(files) gives the total count of items in the list.
print("-" * 50)   # Print 50 dashes — a visual separator in terminal output.

# =============================================================================
# STEP 3 — Define the mock upload function (Resilience Layer)
# =============================================================================
# CONCEPT — Functions:
#   A function is a reusable block of code that runs ONLY when called.
#   Defining the function here (above the loop) means the loop can call it
#   for every file without copy-pasting the same code 5 times.
#   DRY Principle: Don't Repeat Yourself.
#
# CONCEPT — Simulating Randomness (Monte Carlo / Chaos Engineering):
#   random.random() < 0.3 is True 30% of the time — modelling a 30% packet
#   loss rate, which is realistic for rural 4G coverage.  Using randomness
#   to test resilience is the foundation of "Chaos Engineering" (Netflix
#   famously built "Chaos Monkey" to randomly kill their own servers in
#   production to verify resilience).

def mock_upload(filename):
    """
    Simulates uploading a single file to the cloud.
    Introduces a 30% random connection drop to test exponential backoff.

    Args:
        filename (str): The name of the file being "uploaded".
    """
    # Announce the upload attempt.
    print(f"   [UPLOAD] Sending {filename} to MedCloud...")

    # time.sleep(0.3) pauses for 0.3 seconds — simulates the latency of
    # an HTTP PUT request travelling over a 4G connection to an S3 bucket.
    time.sleep(0.3)

    # --- SIMULATE NETWORK INSTABILITY ---
    # random.random() generates a random float e.g. 0.73, 0.12, 0.91 …
    # Comparing it to 0.3 gives us a 30% chance of "failure" per upload.
    if random.random() < 0.3:
        # This block runs 30% of the time (simulated connection drop).
        print(f"   [!] CONNECTION DROP: 4G Signal Unstable.")

        # Wait 0.5s — simulating TCP timeout detection.
        time.sleep(0.5)

        # In real exponential backoff the wait doubles each retry.
        # Here we simplify to a single 1-second retry for demo clarity.
        print(f"   [RETRY] Exponential Backoff... Retrying in 1s...")
        time.sleep(1.0)

        # Simulate successful reconnection.  In production you would actually
        # repeat the HTTP request here inside a while-loop with a max_retries cap.
        print(f"   [SUCCESS] Reconnected via HTTPS. Upload Complete.")
    else:
        # This block runs 70% of the time (normal successful upload).
        print(f"   [SUCCESS] Upload Complete.")

# =============================================================================
# STEP 4 — The main processing loop
# =============================================================================
# CONCEPT — enumerate():
#   enumerate(iterable) wraps a list so that each iteration gives you BOTH
#   the position (index, starting at 0) AND the value.
#   Without enumerate you would have to manage a separate counter variable.
#   Pattern:  for index, value in enumerate(my_list):

for index, filename in enumerate(files):

    # --- DEMO SAFETY NET ---
    # We cap at 5 files so the demo finishes quickly and doesn't time out.
    # In production you remove this guard and process the entire folder.
    if index >= 5:
        print("\n[DEMO LIMIT] Processed 5 files. Stopping batch job.")
        break   # `break` immediately exits the for-loop.

    # --- BUILD THE FULL FILE PATH ---
    # CONCEPT — os.path.join():
    #   Never concatenate paths with "+" or "/" manually — different operating
    #   systems use different separators ("\\" on Windows, "/" on Linux/macOS).
    #   os.path.join() handles this automatically — your code is portable.
    #   Example: os.path.join("2_skull_ct/DICOM", "I10.dcm") → "2_skull_ct/DICOM/I10.dcm"
    full_path = os.path.join(input_folder, filename)

    # --- TRY/EXCEPT: Error Handling ---
    # CONCEPT — Exception Handling:
    #   In a batch pipeline, one corrupted file should NOT crash the entire job.
    #   The try/except pattern says:
    #     "Attempt the risky code in `try`.
    #      If ANY error occurs, jump to `except` and handle it gracefully."
    #   `Exception as e` captures the error object; e gives us the description.
    try:
        # A. EXTRACT — Read the DICOM file from disk.
        ds = pydicom.dcmread(full_path)

        # B. TRANSFORM — Apply anonymization (same logic as anonymizer.py).
        ds.PatientName = "ANONYMOUS"
        ds.PatientID   = "00000"
        ds.StationName = "REMOTE_MOBILE_CLINIC_01"   # Provenance tag (see anonymizer.py).

        # C. LOAD — Save the transformed file to the output folder.
        # Prefix "Clean_" makes it easy to distinguish processed files from originals.
        new_filename = f"Clean_{filename}"
        save_path    = os.path.join(output_folder, new_filename)
        ds.save_as(save_path)

        print(f"[EDGE PROCESS] Anonymized: {filename}")

        # D. UPLOAD — Trigger the (simulated) network upload.
        mock_upload(new_filename)
        print("-" * 50)

    except Exception as e:
        # If reading or saving fails (e.g., corrupted file, missing pixel data),
        # we print the error and CONTINUE to the next file rather than crashing.
        # `continue` skips the rest of this iteration and moves to the next `filename`.
        print(f"Error Processing {filename}: {e}")

# =============================================================================
# STEP 5 — Final status message
# =============================================================================
print("Batch Job completed.")

# =============================================================================
# KEY INTERVIEW TALKING POINTS for this file:
# =============================================================================
# Q: "What is the ETL pattern?"
# A: Extract-Transform-Load.  Extract = read raw files.  Transform = clean/anonymize.
#    Load = write to destination (disk, S3, PACS).  Every data pipeline is ETL.
#
# Q: "What is Exponential Backoff and why is it important?"
# A: A retry strategy where the wait time doubles after each failure
#    (1s, 2s, 4s, 8s …).  It prevents "retry storms" that overwhelm a
#    recovering server.  AWS, GCP, and Azure all recommend it in their SDKs.
#
# Q: "Why use try/except in a loop?"
# A: Fault isolation.  In batch jobs, one bad record must not stop the rest.
#    This is called "fault tolerance" — a core reliability principle.
#
# Q: "What is a List Comprehension?"
# A: A concise, Pythonic way to build a list from an iterable with an optional
#    filter.  [f for f in os.listdir(...) if not f.startswith('.')]
#    is equivalent to a for-loop with an if-statement inside.
#
# Q: "What does os.path.join() do and why is it important?"
# A: It builds file paths correctly regardless of the operating system,
#    using "/" on Linux/macOS and "\\" on Windows.  Using "+" to join paths
#    is a portability bug waiting to happen.
# =============================================================================