import pydicom
import matplotlib.pyplot as plt
import os
import argparse


def main():
    parser = argparse.ArgumentParser(description="View an anonymized DICOM scan.")
    parser.add_argument("--file", default="Clean_I10.dcm", help="Filename inside batch_anonymized/ to view")
    parser.add_argument("--folder", default="batch_anonymized", help="Folder containing anonymized DICOM files")
    args = parser.parse_args()

    folder_path = args.folder
    filename = args.file

    full_path = os.path.join(folder_path, filename)

    # Check if file exists
    if not os.path.exists(full_path):
        print(f"ERROR: could not find {full_path} ")
        print("Did you run the batch processor first?")
        exit()

    # Read the DICOM file
    ds = pydicom.dcmread(full_path)

    # we are printing a secret ID tag, anonymized version
    print(f"Patient Name: {ds.PatientName} ")
    print(f"Patient ID: {ds.PatientID}")
    print(f"Image size: {ds.Rows} x {ds.Columns} pixels")

    # Magic: Show the image
    print("Displaying image...")

    # CT scans are usually just grid of numbers, pixel_arrays access them
    plt.imshow(ds.pixel_array, cmap=plt.cm.bone)  # Bone colormap for better visualization of ct scans

    plt.title(f"CT Slice: {ds.PatientName}")
    plt.axis('off')  # Hiding the x and y axis for better visualization
    plt.show()


if __name__ == "__main__":
    main()             