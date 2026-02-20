# =============================================================================
# density_plot.py — Step 4: The Clinical AI Layer (Single-Patient View)
# =============================================================================
# PURPOSE: Take ONE anonymized CT scan and apply unsupervised machine learning
# to segment its pixels into meaningful anatomical tissue groups.
# The output is a side-by-side visualisation: original scan vs AI-coloured
# segmentation — an aid for a radiologist doing rapid triage.
#
# CONCEPT — Image Segmentation:
#   Segmentation = dividing an image into regions that share a meaningful
#   property.  Here we segment by PIXEL BRIGHTNESS (density):
#     Dark pixels  → Air (lungs, cavities)  → Cluster 0
#     Mid pixels   → Soft Tissue (muscle, organs) → Cluster 1
#     Bright pixels → Bone (skull, ribs, spine) → Cluster 2
#   This is "semantic segmentation" — assigning a class label to every pixel.
#
# CONCEPT — Unsupervised vs Supervised Machine Learning:
#   Supervised learning needs labelled training data (e.g., "this pixel = bone").
#   UNSUPERVISED learning (like K-Means) finds structure in unlabelled data.
#   We use unsupervised here because:
#     1. We don't have labelled training scans.
#     2. We only care about relative clusters (bright vs dark), not absolute
#        clinical diagnoses.  A radiologist still reads the final image.
#
# CONCEPT — K-Means Clustering:
#   K-Means is an algorithm that groups N data points into K clusters by
#   minimising the distance of each point to its cluster's centroid (average).
#   Algorithm steps:
#     1. Randomly place K centroids in the data space.
#     2. Assign each point to the nearest centroid.
#     3. Recalculate each centroid as the mean of its assigned points.
#     4. Repeat steps 2-3 until centroids stop moving (convergence).
#   Time complexity: O(n × K × iterations) — fast on small images.
#
# PIPELINE POSITION:  … → Batch Processor → Viewer → [Density Plot] → Miner
# =============================================================================

# --- IMPORTS ---
import pydicom                      # Read DICOM files.
import matplotlib.pyplot as plt     # Plotting and image display.
import os                           # File system operations.
from sklearn.cluster import KMeans  # K-Means implementation from scikit-learn.
                                    # scikit-learn ("sklearn") is the standard
                                    # Python ML library for classical algorithms.

# =============================================================================
# CONFIGURATION — Smart File Loader
# =============================================================================
# Instead of hardcoding a specific filename (fragile), we look at the folder
# and pick the FIRST file found.  This makes the script work regardless of
# what the batch processor named the file.

work_folder = "batch_anonymized"   # Folder produced by batch_processor.py.

# =============================================================================
# STEP 1 — Folder existence check
# =============================================================================
if not os.path.exists(work_folder):
    print("ERROR: Folder not found. Run batch_processor.py first!")
    exit()

# os.listdir() returns a list of filenames in the folder.
# We filter out hidden dot-files (e.g., .DS_Store on macOS).
files = [f for f in os.listdir(work_folder) if not f.startswith('.')]

if len(files) == 0:
    print("ERROR: Folder is empty. Batch Processor failed.")
    exit()

# Pick the first available file — "smart loader" pattern.
# files[0] accesses the first element of the list (Python lists are 0-indexed).
target_file = files[0]
full_path   = os.path.join(work_folder, target_file)

print(f"--> FOUND FILE: {target_file}")
print(f"--> Loading {full_path} for AI Analysis...")

# =============================================================================
# STEP 2 — Load the DICOM file and extract pixel data
# =============================================================================
# We wrap this in try/except because some DICOM files have incomplete headers
# or use unsupported compression — crashing here would be unrecoverable.
#
# force=True: tells pydicom to attempt to read even if the DICOM preamble
# or transfer syntax header is missing or non-standard.  Useful for files
# from older scanners or files that were partially anonymized.

try:
    ds          = pydicom.dcmread(full_path, force=True)
    pixel_data  = ds.pixel_array   # 2-D NumPy array of pixel intensities.
except Exception as e:
    print(f"\nCRITICAL ERROR: Could not read {target_file}.")
    print(f"Details: {e}")
    exit()

# =============================================================================
# STEP 3 — Prepare the data for K-Means (the "feature engineering" step)
# =============================================================================
# CONCEPT — Feature Engineering:
#   ML algorithms don't understand "images" — they understand arrays of numbers.
#   "Feature engineering" is the process of converting raw data into the
#   numeric format the algorithm expects.
#
# pixel_data is currently a 2-D array with shape (rows, columns).
# e.g. for a 512×512 CT slice: shape = (512, 512).
#
# K-Means from scikit-learn expects a 2-D input with shape (n_samples, n_features).
# Each row = one data point (one pixel).
# Each column = one feature (here we only have 1 feature: brightness).
#
# .reshape(-1, 1) transforms:
#   (512, 512) → (262144, 1)
# The -1 tells NumPy "calculate this dimension automatically" so we don't
# have to compute 512×512=262144 ourselves.

print("Running K-Means Clustering...")
X = pixel_data.reshape(-1, 1)   # Flatten 2-D image into a column vector.

# =============================================================================
# STEP 4 — Fit K-Means
# =============================================================================
# KMeans Parameters:
#   n_clusters=3  : We want exactly 3 groups (Air, Soft Tissue, Bone).
#                   This is a HYPERPARAMETER — a design choice made by the
#                   engineer, not learned from data.
#   random_state=42 : Seeds the random number generator so results are
#                   REPRODUCIBLE.  Without this, K-Means gives slightly
#                   different results every run (because initial centroids
#                   are placed randomly).  Using 42 is a convention.
#   n_init=10     : Run K-Means 10 times with different centroid seeds and
#                   keep the best result.  Reduces the chance of converging
#                   to a local minimum rather than the global optimum.
#
# kmeans.fit(X)   : Trains the model — runs the K-Means algorithm on X.
#                   After this call, kmeans.labels_ contains the cluster
#                   assignment (0, 1, or 2) for every pixel.
#                   kmeans.cluster_centers_ contains the 3 centroid values.

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans.fit(X)

# kmeans.labels_ is a 1-D array of length n_samples (262144 for 512×512).
# Each element is an integer in {0, 1, 2} indicating the cluster.
# We reshape it BACK to the original image shape so we can display it
# as a 2-D image where each pixel is coloured by its cluster label.
clustered_pixels = kmeans.labels_.reshape(pixel_data.shape)

# =============================================================================
# STEP 5 — Visualise: Original vs AI Segmented (side-by-side comparison)
# =============================================================================
print("Generating Image...")

# plt.figure(figsize=(10, 5)) creates a blank figure that is 10 inches wide
# and 5 inches tall.  figsize controls the physical size of the saved image.
plt.figure(figsize=(10, 5))

# --- Left Panel: Original Scan ---
# plt.subplot(rows, cols, panel_number) divides the figure into a grid.
# subplot(1, 2, 1) means: 1 row, 2 columns, and we are drawing in panel 1.
plt.subplot(1, 2, 1)
plt.imshow(pixel_data, cmap='gray')   # 'gray' colour map: dark=low, bright=high.

# ds.get("StationName", "Unknown") safely retrieves the StationName tag.
# If the tag doesn't exist in the file, it returns "Unknown" instead of crashing.
# This is the tag we SET in batch_processor.py — it tells us which clinic
# the scan came from.
try:
    station = ds.get("StationName", "Unknown")
    plt.title(f"Original Scan\n(Source: {station})")
except Exception:
    plt.title("Original Scan")

plt.axis('off')   # Hide axis ticks — standard for medical image display.

# --- Right Panel: AI-Segmented Image ---
plt.subplot(1, 2, 2)

# cmap='plasma' maps cluster labels (0, 1, 2) to a vivid purple-orange-yellow
# colour scale.  We choose 'plasma' (not 'gray') specifically so the 3 tissue
# types are visually distinct — making triage faster for a radiologist.
# Cluster 0 (dark blue) → Air
# Cluster 1 (orange)    → Soft Tissue
# Cluster 2 (yellow)    → Bone
plt.imshow(clustered_pixels, cmap='plasma')
plt.title("AI Segmentation\n(Air vs Tissue vs Bone)")
plt.axis('off')

# =============================================================================
# STEP 6 — Save the output image to disk
# =============================================================================
# plt.savefig() writes the figure to a PNG file on disk.
# This is essential for a pipeline — you always want a persistent artefact
# rather than just an ephemeral screen display.
output_file = "highlighted_scan.png"
plt.savefig(output_file)
print(f"[SUCCESS] Analysis saved to {output_file}")

# Note: plt.show() is intentionally NOT called here so the script can run
# non-interactively (e.g., inside a Docker container or cron job without
# a display).  The PNG file is the primary output.

# =============================================================================
# KEY INTERVIEW TALKING POINTS for this file:
# =============================================================================
# Q: "Explain K-Means Clustering in simple terms."
# A: K-Means groups data points into K buckets so that each point is as
#    close as possible to the centre of its bucket.  It iterates:
#    assign each point to nearest centre → recalculate centre → repeat.
#    It minimises "within-cluster sum of squared distances" (inertia).
#
# Q: "Why K=3 specifically?"
# A: We know from anatomy that a CT scan contains 3 broad tissue density
#    zones: air (~-1000 HU), soft tissue (~0–80 HU), bone (~400+ HU).
#    K=3 maps directly to this domain knowledge.  Choosing K is a
#    hyperparameter decision informed by subject matter expertise.
#
# Q: "What is random_state=42?"
# A: Setting a random seed makes results deterministic and reproducible.
#    This is critical in research and production — you need to get the
#    same result every time you run the code on the same data.
#
# Q: "What does reshape(-1, 1) do?"
# A: It converts a 2-D image array into a single column of pixels.
#    The -1 is a NumPy shorthand meaning "infer this dimension automatically."
#    It is needed because scikit-learn requires shape (n_samples, n_features).
#
# Q: "What is the difference between supervised and unsupervised learning?"
# A: Supervised learning uses labelled training data (input → known output).
#    Unsupervised learning discovers structure without labels.  K-Means is
#    unsupervised — it finds clusters based purely on data geometry.
# =============================================================================