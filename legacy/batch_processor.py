import pydicom
import os
import time
import random

# 1. Inputs and Outputs
input_folder = "2_skull_ct/DICOM" 
output_folder = "batch_anonymized"

# 2. Create output folder
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 3. Get the list of files
files = [f for f in os.listdir(input_folder) if not f.startswith('.')]
print(f"Starting batch processing of {len(files)} files...")
print("-" * 50)

# --- THE DRAMA FUNCTION (Fake Upload) ---
def mock_upload(filename):
    print(f"   [UPLOAD] Sending {filename} to MedCloud...")
    time.sleep(0.3) 
    
    if random.random() < 0.3:
        print(f"   [!] CONNECTION DROP: 4G Signal Unstable.")
        time.sleep(0.5)
        print(f"   [RETRY] Exponential Backoff... Retrying in 1s...")
        time.sleep(1.0)
        print(f"   [SUCCESS] Reconnected via HTTPS. Upload Complete.")
    else:
        print(f"   [SUCCESS] Upload Complete.")

# 4. The Loop
for index, filename in enumerate(files):
    # STOPPER: Only do 5 files for the demo
    if index >= 5:
        print("\n[DEMO LIMIT] Processed 5 files. Stopping batch job.")
        break

    # --- THIS WAS THE MISSING LINE CAUSING THE ERROR ---
    full_path = os.path.join(input_folder, filename)
    # ---------------------------------------------------
    
    try:
        # A. Read
        ds = pydicom.dcmread(full_path)
        
        # B. Modify 
        ds.PatientName = "ANONYMOUS"
        ds.PatientID = "00000"
        # The Critical Tag
        ds.StationName = "REMOTE_MOBILE_CLINIC_01" 
        
        # C. Save
        new_filename = f"Clean_{filename}"
        save_path = os.path.join(output_folder, new_filename)
        ds.save_as(save_path)
        
        print(f"[EDGE PROCESS] Anonymized: {filename}")
        
        # D. Run the Fake Upload
        mock_upload(new_filename)
        print("-" * 50)

    except Exception as e:
        print(f"Error Processing {filename}: {e}")

print("Batch Job completed.")