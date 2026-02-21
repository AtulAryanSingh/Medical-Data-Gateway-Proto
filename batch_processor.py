import pydicom
import os
import time
import random
import argparse


def mock_upload(filename, max_retries=4):
    print(f"   [UPLOAD] Sending {filename} to MedCloud...")
    for attempt in range(max_retries):
        time.sleep(0.3)
        if random.random() < 0.3:
            wait = 2 ** attempt  # Real exponential backoff: 1s, 2s, 4s, 8s
            print(f"   [!] CONNECTION DROP: 4G Signal Unstable. (Attempt {attempt + 1}/{max_retries})")
            print(f"   [RETRY] Exponential Backoff... Retrying in {wait}s...")
            time.sleep(wait)
        else:
            print(f"   [SUCCESS] Upload Complete after {attempt + 1} attempt(s).")
            return True
    print(f"   [FAILED] Upload failed after {max_retries} attempts. File queued for later retry.")
    return False


def main():
    parser = argparse.ArgumentParser(description="Batch anonymize and upload DICOM files.")
    parser.add_argument("--input", default="2_skull_ct/DICOM", help="Input folder containing raw DICOM files")
    parser.add_argument("--output", default="batch_anonymized", help="Output folder for anonymized files")
    parser.add_argument("--limit", type=int, default=5, help="Max files to process (demo limit)")
    args = parser.parse_args()
    input_folder = args.input
    output_folder = args.output

    # Create output folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get the list of files
    files = [f for f in os.listdir(input_folder) if not f.startswith('.')]
    print(f"Starting batch processing of {len(files)} files...")
    print("-" * 50)

    # The Loop
    for index, filename in enumerate(files):
        # STOPPER: Only do files up to the demo limit
        if index >= args.limit:
            print(f"\n[DEMO LIMIT] Processed {args.limit} files. Stopping batch job.")
            break

        full_path = os.path.join(input_folder, filename)

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


if __name__ == "__main__":
    main()