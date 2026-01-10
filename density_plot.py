import pydicom
import matplotlib.pyplot as plt
import os

# Loading a file from the batch aninymized folder
filename = "batch_anonymized/Clean_I10.dcm"
ds = pydicom.dcmread(filename)

#Extracting the raw pixels
pixels = ds.pixel_array

#Flattening the data for density plot
flat_pixels = pixels.flatten() 

#Creating the histogram
print(f"Analyzing {len(flat_pixels)} pixels...")
print("Plotting tissue densitites")

plt.figure(figsize = (10,6))
plt.hist(flat_pixels, bins = 100, color = 'c')

#Labeling the plot
plt.title(f"Radiodensity Histogram {ds.PatientName}")
plt.xlabel("Pixel Instensity (Housefiled units approx)")
plt.ylabel("Number of pixels (Frequency count)")
plt.grid(True, alpha = 0.3)

plt.show()