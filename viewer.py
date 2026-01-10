import pydicom 
import matplotlib.pyplot as plt
import os

# Lets have a look at our cleaned file
folder_path = "batch_anonymized" #We are just checking if the batch processor actually worked
filename =  "Clean_I10.dcm"

full_path = os.path.join(folder_path, filename)

#Check if file exists
if not os.path.exists(full_path):
    print(f"ERROR: could not find {full_path} ")
    print("Did you run the batch processor first?")
    exit()

# Read the DICOM file
ds = pydicom.dcmread(full_path)

#we are printing a secret ID tag, anonymized version
print(f"Patient Name: {ds.PatientName} ")
print(f"Patient ID: {ds.PatientID}")
print(f"Image size: {ds.Rows} x {ds.Columns} pixels")

# Magic: Show the image
print("Displaying image...")

#CT scans are usually just grid of numbers, pixel_arrays access them
plt.imshow(ds.pixel_array, cmap =plt.cm.bone) #Bone colormap for better visualization of ct scans

plt.title(f"CT Slice: {ds.PatientName}")
plt.axis('off')  #Hiding the x and y axis for better visualization
plt.show()             