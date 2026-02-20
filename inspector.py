# =============================================================================
# inspector.py — Step 0: "What even IS a DICOM file?"
# =============================================================================
# PURPOSE: This is your very first "hello world" for medical imaging.
# Before building any pipeline, you need to know what the raw material
# looks like.  A DICOM file is NOT just an image — it is an image PLUS
# a structured metadata "envelope" (like a labelled envelope in a hospital
# records room).  This script tears open that envelope and shows you both
# the label (metadata) and the letter inside (pixel data).
#
# CONCEPT — What is DICOM?
#   DICOM = Digital Imaging and Communications in Medicine.
#   It is the global standard for storing and transmitting medical images
#   (X-rays, CT scans, MRIs, etc.).  Every .dcm file contains:
#     1. A HEADER (key-value tags like PatientID, Modality, StudyDate)
#     2. PIXEL DATA (the actual image as a grid of numbers)
#   Think of it as a Python dictionary stapled to a photograph.
# =============================================================================

# --- IMPORT SECTION ---
# An "import" tells Python: "go find this pre-built toolbox and bring it here."
# You do not write these libraries yourself — they are maintained by experts
# and installed via `pip install pydicom matplotlib`.

import pydicom           # Toolbox for reading/writing DICOM (.dcm) files.
                         # Without this, Python has no idea what a .dcm file is.

import matplotlib.pyplot as plt  # Toolbox for drawing charts and images.
                                 # "pyplot" is the sub-module that gives us an
                                 # interface similar to MATLAB (plt.imshow, plt.show).

# =============================================================================
# STEP 1 — Load the DICOM file from disk into memory
# =============================================================================
# pydicom.dcmread() reads ALL the bytes in the .dcm file and builds a
# Python object (here called `dataset`) that behaves like a dictionary.
# After this line `dataset` holds BOTH the metadata AND the pixel array.
#
# ANALOGY: Imagine scanning a paper hospital record into your computer.
# dcmread() does exactly that — it "scans" the .dcm file into an
# in-memory Python object you can query with dot-notation.
dataset = pydicom.dcmread("test_scan.dcm")

# =============================================================================
# STEP 2 — Print the metadata tags (the "envelope" / header information)
# =============================================================================
# Each piece of metadata is accessed like an attribute (dataset.TagName).
# Internally pydicom maps standard DICOM tag numbers to human-readable names.
# e.g.  (0010,0020) in DICOM spec  →  dataset.PatientID in Python.

# PatientID: A unique identifier assigned to the patient in the hospital system.
# In a real system this is a sensitive PII (Personally Identifiable Information)
# field — our anonymizer.py will later replace this with "00000".
print("Patient ID:", dataset.PatientID)

# Modality: The type of imaging equipment used.
# Common values: "CT" (Computed Tomography), "MR" (MRI), "DX" (Digital X-ray).
# Knowing the modality tells you what kind of image you are dealing with
# and what clinical information it contains.
print("Modality:", dataset.Modality)

# StudyDate: When the scan was acquired (format YYYYMMDD, e.g. "20231105").
# This is crucial for audit trails and for ordering studies chronologically.
print("Study Date:", dataset.StudyDate)

# =============================================================================
# STEP 3 — Display the image (the "pixel data" inside the envelope)
# =============================================================================
# CONCEPT — pixel_array:
#   dataset.pixel_array converts the raw compressed bytes stored in the DICOM
#   file into a NumPy 2-D array (a grid) of integers where each integer
#   represents the brightness of one pixel.
#   For a CT scan, these numbers are Hounsfield Units (HU):
#     -1000 HU = Air (black)
#        0 HU = Water
#     +400 HU = Bone (white)
#   For a chest X-ray they are raw 12-bit or 16-bit intensity values.
#
# plt.imshow(): Takes the 2-D NumPy array and maps each number to a colour
#   using a "colour map" (cmap).
#
# cmap=plt.cm.bone: The "bone" colour map renders low values as dark blue/black
#   and high values as white — mimicking how a traditional film X-ray looks
#   on a light-box.  This makes anatomical structures (ribs, vertebrae) visually
#   intuitive for a clinician or radiologist.
plt.imshow(dataset.pixel_array, cmap=plt.cm.bone)

# plt.show() opens an interactive window displaying the rendered image.
# In a script (non-Jupyter) environment this blocks until you close the window.
plt.show()

# =============================================================================
# KEY INTERVIEW TALKING POINTS for this file:
# =============================================================================
# Q: "What is a DICOM file?"
# A: A standardised medical-imaging container format that bundles structured
#    metadata (patient, study, equipment tags) with compressed pixel data.
#
# Q: "Why do we use pydicom?"
# A: pydicom is the de-facto Python library for DICOM.  It handles the complex
#    binary parsing, tag mapping, and decompression so we don't have to.
#
# Q: "What does pixel_array return?"
# A: A NumPy ndarray — typically 2-D for a single slice, 3-D for a volume.
#    NumPy arrays are the lingua franca of scientific Python; virtually every
#    AI/ML library (scikit-learn, TensorFlow, PyTorch) expects NumPy arrays.
# =============================================================================