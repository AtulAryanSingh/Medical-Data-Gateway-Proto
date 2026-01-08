import pydicom
import os

# 1. Inputs and Outputs
input_folder = "2_skull_ct/DICOM"  # Make sure this matches your folder name!
output_folder = "batch_anonymized"

# 2. Create output folder
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Created target folder: {output_folder}")

# 3. Get the list of files
files = os.listdir(input_folder)
print(f"Starting batch processing of {len(files)} files...")

# 4. The Loop
for filename in files:
    # Skip hidden files
    if filename.startswith("."):
        continue
    
    # --- EVERYTHING BELOW IS NOW INDENTED (INSIDE THE LOOP) ---
    
    # Join paths
    full_path = os.path.join(input_folder, filename)

    try:
        # A. Read
        ds = pydicom.dcmread(full_path)
        
        # B. Modify
        old_name = ds.PatientName
        ds.PatientName = "BATCH_ANONYMIZED"
        ds.PatientID = "00000"
        
        # C. Save
        new_filename = f"Clean_{filename}.dcm"
        save_path = os.path.join(output_folder, new_filename)
        
        ds.save_as(save_path)
        print(f"Processed: {filename} -> {new_filename}")
        
    except Exception as e:
        # Even the error handler must be indented!
        print(f"Error Processing {filename}: {e}") 
    
    # --- END OF LOOP ---

print("Batch Job completed.")