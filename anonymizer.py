import pydicom
import os


def main():
    # 1. Setup: Define our input and output
    input_file = "test_scan.dcm"
    output_file = "anonymized_scan.dcm"

    print(f"--- Processing {input_file} ---")

    # 2. Safety Check: Ensure the file exists
    if not os.path.exists(input_file):
        print("ERROR: File not found! Did you rename your file to 'test_scan.dcm'?")
        exit()

    # 3. Load the DICOM file
    ds = pydicom.dcmread(input_file)

    # 4. Show "Before" status
    print(f"ORIGINAL Patient Name: {ds.PatientName}")
    print(f"ORIGINAL Patient ID: {ds.PatientID}")

    # 5. The "Business Logic" (Anonymization)
    ds.PatientName = "ANONYMOUS"
    ds.PatientID = "00000"

    # Simulating the 'edge' environment
    # This tag(StationName) tells the server that where this file has came from
    ds.StationName = "REMOTE_MOBILE_CLINIC_01"
    print('Added Tag: StationName -> "REMOTE_MOBILE_CLINIC_01"')

    # 6. Save the new file(The "MIG" Action)
    ds.save_as(output_file)

    print("-" * 30)
    print("SUCCESS: File anonymized and saved.")
    print(f"New file created: {output_file}")

    # 7. Verification: Read the file to prove it worked
    new_ds = pydicom.dcmread(output_file)
    print(f"CHECKING NEW FILE -> Patient Name is now: {new_ds.PatientName}")


if __name__ == "__main__":
    main()    