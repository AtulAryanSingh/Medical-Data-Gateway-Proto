import pydicom
import matplotlib.pyplot as plt

# 1. Load the mysterious file
dataset = pydicom.dcmread("test_scan.dcm")

# 2. Print the hidden "Envelope" text (The Metadata)
print("Patient ID:", dataset.PatientID)
print("Modality:", dataset.Modality)
print("Study Date:", dataset.StudyDate)

# 3. Show the image (The Pixel Data)
plt.imshow(dataset.pixel_array, cmap=plt.cm.bone)
plt.show()