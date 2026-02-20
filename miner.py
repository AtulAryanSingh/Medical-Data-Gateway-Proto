# =============================================================================
# miner.py — Step 5: The Business Intelligence / Fleet Analytics Layer
# =============================================================================
# PURPOSE: Zoom out from individual patients and look at the ENTIRE FLEET.
# Instead of asking "Is this scan normal?", we ask "Are any of our SCANNERS
# producing systematically different images than the rest?"
# This is Quality Control (QC) at the machine level — detecting broken hardware.
#
# CONCEPT — Population Analytics vs Individual Analytics:
#   density_plot.py works at the PIXEL level on ONE scan  (micro view).
#   miner.py works at the SCAN level across ALL patients  (macro view).
#   This is the same distinction as:
#     Individual health record  vs  Public health statistics.
#     One stock's price history  vs  Market-wide sector analysis.
#
# CONCEPT — Feature Extraction (Data Mining):
#   "Data Mining" means finding hidden patterns in large datasets.
#   We cannot feed 262,144 pixel values per scan into an analytics model —
#   it would be impossibly slow and the signal would be buried in noise.
#   Instead we EXTRACT summary statistics (features) that describe each
#   scan in just 3 numbers:
#     1. Average Density  -> How bright is the scan overall?
#     2. Contrast (StdDev) -> How sharp/varied is the image?
#     3. Peak Bone Density -> How dense is the densest structure?
#   Reducing dimensions like this is called DIMENSIONALITY REDUCTION.
#
# CONCEPT — Anomaly Detection via Clustering:
#   We cluster scans by their 3 features.  Scans from working scanners
#   will cluster together (Cluster A).  Scans from a faulty scanner —
#   one with a calibration drift, dusty detector, or broken X-ray tube —
#   will have systematically different brightness/contrast and form a
#   separate cluster (Cluster B = outliers).
#   This is an automated QC system: no human needs to manually review
#   every scan to spot a broken machine.
#
# CONCEPT — Separation of Concerns (Functions):
#   This script is split into two functions:
#     extract_scan_features()    -> Data ingestion + feature engineering
#     run_clustering_analysis()  -> ML + visualisation
#   Keeping each "concern" in its own function makes the code testable,
#   reusable, and easy to maintain.
#
# PIPELINE POSITION:  ... -> Density Plot -> [Miner] (final analytics stage)
# =============================================================================

# --- IMPORTS ---
import os                           # File system operations.
import pydicom                      # Read DICOM files.
import numpy as np                  # NumPy: numerical computing library.
                                    # np.mean(), np.std(), np.max(), np.array()
                                    # NumPy arrays are the backbone of all
                                    # scientific Python (ML, stats, simulation).
import matplotlib.pyplot as plt     # Plotting scatter charts.
from sklearn.cluster import KMeans  # K-Means clustering algorithm.

# =============================================================================
# CONFIGURATION
# =============================================================================
# The folder produced by batch_processor.py — same as density_plot.py.
input_folder = "batch_anonymized"

# =============================================================================
# FUNCTION 1: extract_scan_features()
# =============================================================================
# "Feature extraction" is arguably the most important step in any ML pipeline.
# Garbage features -> garbage model -> garbage business decisions.
# Good features -> meaningful clusters -> actionable QC insights.

def extract_scan_features(folder):
    """
    Loop through all DICOM files in `folder` and extract three numerical
    features from each scan's pixel data.

    Features extracted per scan:
        avg_density  (float) : Mean pixel intensity — overall brightness.
        contrast     (float) : Standard deviation of pixel intensity — sharpness.
        peak_bone    (float) : Maximum pixel value — densest anatomical structure.

    Args:
        folder (str): Path to the folder of processed DICOM files.

    Returns:
        tuple: (np.ndarray of shape (N, 3), list of N filenames)
               Returns ([], []) if the folder is missing or empty.

    CONCEPT — Docstrings:
        The text between the triple-quotes is a "docstring" — Python's
        built-in documentation standard.  Tools like Sphinx, pytest, and
        IDEs automatically read docstrings to generate docs and hover-tips.
        Always write docstrings for public functions in production code.
    """
    # Two parallel lists — built together, they form a "dataset table":
    # data_points[i] = [avg_density, contrast, peak_bone] for the i-th file.
    # filenames[i]   = the filename of the i-th file.
    data_points = []
    filenames   = []

    # --- Safety Check ---
    if not os.path.exists(folder):
        print(f"ERROR: Folder '{folder}' not found. Run batch_processor.py first!")
        return [], []

    print("--- 1. MINING DATASET GENERATION ---")

    # os.listdir() + filter — same pattern as batch_processor.py.
    files = [f for f in os.listdir(folder) if not f.startswith('.')]

    if len(files) == 0:
        print("ERROR: No files in folder. Run the batch processor!")
        return [], []

    # --- MAIN EXTRACTION LOOP ---
    for f in files:
        full_path = os.path.join(folder, f)
        try:
            # force=True handles edge-case DICOM files with truncated headers.
            ds         = pydicom.dcmread(full_path, force=True)
            pixel_data = ds.pixel_array   # 2-D NumPy array of pixel values.

            # =================================================================
            # FEATURE 1 — Average Density
            # =================================================================
            # np.mean(array) computes the arithmetic mean of all elements.
            # For a 512x512 CT image with values in [-1000, +3000]:
            #   A high mean -> lots of bright pixels -> dense anatomy (e.g., skull)
            #   A low mean  -> lots of dark pixels  -> lots of air/soft tissue
            #
            # UNIT: Hounsfield Units (HU) for CT, raw ADC counts for X-ray.
            # CLINICAL MEANING: Scanner-level baseline brightness.
            #   If one scanner consistently produces darker images (lower mean)
            #   it may have an X-ray tube that is losing power — a fault signal.
            avg_density = np.mean(pixel_data)

            # =================================================================
            # FEATURE 2 — Contrast (Standard Deviation)
            # =================================================================
            # np.std(array) computes the standard deviation:
            #   std = sqrt(mean((x - mean)^2))
            # Standard deviation measures how spread out the pixel values are.
            #   High std -> wide range of brightnesses -> sharp, well-contrasted image
            #   Low std  -> all pixels similar brightness -> flat, foggy/washed-out image
            #
            # CLINICAL MEANING: Image quality indicator.
            #   A scanner with a deteriorating X-ray detector produces low-contrast
            #   (uniform grey) images — dangerous because subtle lesions become invisible.
            contrast = np.std(pixel_data)

            # =================================================================
            # FEATURE 3 — Peak Bone Density
            # =================================================================
            # np.max(array) returns the single highest value in the array.
            # For CT: this is the brightest pixel, usually cortical bone.
            #   Normal peak: ~1000-3000 HU (dense bone).
            #   Abnormally low peak: scanner may be under-exposed or miscalibrated.
            peak_bone = np.max(pixel_data)

            # Append this scan's features as a list to our data_points collection.
            # After the loop, data_points looks like:
            #   [[avg1, std1, max1], [avg2, std2, max2], ...]
            data_points.append([avg_density, contrast, peak_bone])
            filenames.append(f)

            # :.1f in the f-string means "format as float with 1 decimal place".
            print(f"   [MINED] {f} -> Density: {avg_density:.1f} | Contrast: {contrast:.1f}")

        except Exception as e:
            # Skip unreadable files gracefully — same fault-tolerance pattern
            # as batch_processor.py.
            print(f"   [SKIP] Could not read {f}: {e}")

    # Convert the Python list-of-lists into a NumPy 2-D array.
    # np.array([[1,2,3],[4,5,6]]) -> shape (2, 3) array.
    # We need a NumPy array (not a plain list) because:
    #   1. scikit-learn expects NumPy arrays.
    #   2. NumPy supports column slicing: data[:, 0] (all rows, column 0).
    return np.array(data_points), filenames


# =============================================================================
# FUNCTION 2: run_clustering_analysis()
# =============================================================================
# Takes the feature matrix produced by extract_scan_features() and applies
# K-Means to find scanner-level clusters.  Then visualises the result.

def run_clustering_analysis(data, filenames):
    """
    Apply K-Means (K=2) to the feature matrix and generate a scatter plot
    that visually separates standard scans from outlier scans.

    Args:
        data      (np.ndarray): Shape (N, 3) feature matrix.
        filenames (list):       List of N filenames (for point labels on chart).

    CONCEPT — Scatter Plot for Cluster Visualisation:
        A scatter plot places each scan as a dot in 2-D space.
        X-axis = Average Density   (Feature 1)
        Y-axis = Contrast          (Feature 2)
        Each dot is coloured by its cluster label (blue=normal, red=outlier).
        Outlier clusters that appear SEPARATE from the main group signal
        a scanner calibration problem to the fleet manager.
    """
    # Need at least 2 data points to form 2 clusters.
    if len(data) < 2:
        print("\n[!] Not enough data to cluster. (Need > 1 file)")
        return

    print("\n--- 2. EXECUTING K-MEANS ALGORITHM ---")

    # --- FEATURE SELECTION: Use only the first 2 features for 2-D plotting ---
    # data[:, 0:2] uses NumPy array slicing:
    #   [:,  ]  = all rows (all scans)
    #   [, 0:2] = columns 0 and 1 (avg_density, contrast)
    # We drop peak_bone (column 2) because a 2-D plot is easier to explain.
    # In production you would use all 3 features and apply PCA to reduce to 2-D.
    #
    # CONCEPT — PCA (Principal Component Analysis):
    #   A dimensionality reduction technique that projects high-dimensional data
    #   onto the 2-3 directions of greatest variance.  Useful for visualising
    #   clusters in data with more than 3 features.
    X = data[:, 0:2]

    # K-Means with K=2:
    #   Cluster 0 = Standard scans  (normal scanner behaviour)
    #   Cluster 1 = Outlier scans   (possible scanner fault / anomaly)
    # n_clusters=2 is our HYPOTHESIS: there are at most 2 distinct scanner states.
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    # fit_predict() is shorthand for .fit(X) followed by .predict(X) — it
    # trains the model AND returns cluster labels for the training data in one call.

    print(f"   [SUCCESS] Classified {len(data)} patients into 2 groups.")

    # --- VISUALISATION ---
    print("\n--- 3. VISUALISING POPULATION TRENDS ---")
    plt.figure(figsize=(10, 6))

    # --- Plot Cluster 0 (Blue = Standard Scans) ---
    # X[labels == 0, 0] : Select rows where label=0, take column 0 (avg_density).
    # X[labels == 0, 1] : Select rows where label=0, take column 1 (contrast).
    # Boolean indexing: `labels == 0` creates a True/False mask, which NumPy
    # uses to select only the matching rows.  This is a fundamental NumPy pattern.
    plt.scatter(
        X[labels == 0, 0],      # X-coordinates: average density of cluster-0 scans.
        X[labels == 0, 1],      # Y-coordinates: contrast of cluster-0 scans.
        s=100,                  # s = marker size in points squared.
        c='blue',               # c = colour.
        label='Cluster A (Standard Scans)'
    )

    # --- Plot Cluster 1 (Red = Outlier / Suspicious Scans) ---
    plt.scatter(
        X[labels == 1, 0],
        X[labels == 1, 1],
        s=100,
        c='red',
        label='Cluster B (Outliers/Mobile Units)'
    )

    # --- Label Each Data Point with its Filename ---
    # enumerate(filenames) gives (0, name0), (1, name1), ...
    # plt.annotate() adds a text label near the (x, y) coordinate of each point.
    # We label every point so the fleet manager can immediately see WHICH
    # specific file (and therefore which patient scan) is an outlier.
    for i, txt in enumerate(filenames):
        plt.annotate(
            txt,                            # The text to display.
            (X[i, 0], X[i, 1]),            # Anchor point (x, y) for the annotation.
            fontsize=9,                     # Small font — many labels, limited space.
            alpha=0.8,                      # 80% opacity — slightly transparent.
            xytext=(5, 5),                  # Offset the text 5 pixels right and up.
            textcoords='offset points'      # Unit for xytext: pixels from anchor.
        )

    # --- Chart Decoration ---
    plt.title("MedSendX Data Mining: Patient Population Analysis")
    plt.xlabel("Average Tissue Density (Brightness)")
    plt.ylabel("Scan Contrast (Image Quality)")

    # plt.legend() draws a colour-coded key (Cluster A / Cluster B).
    # It reads the label= arguments from each scatter() call automatically.
    plt.legend()

    # Grid lines make it easier to read off coordinates visually.
    # linestyle='--' = dashed lines.  alpha=0.6 = 60% transparent (subtle).
    plt.grid(True, linestyle='--', alpha=0.6)

    print("   [DISPLAY] Opening Analysis Plot...")

    # Save the figure to disk BEFORE plt.show() — plt.show() clears the figure.
    plt.savefig("mining_report.png")
    print("   [SAVED] Plot saved to 'mining_report.png'")

    # plt.show() opens an interactive window.  Comment this out for
    # headless/server deployments (Docker, CI, cron jobs).
    plt.show()


# =============================================================================
# ENTRY POINT — `if __name__ == "__main__":`
# =============================================================================
# CONCEPT — Python Module System:
#   Every Python file is a "module".  When you RUN a file directly
#   (python miner.py), Python sets the special variable __name__ to "__main__".
#   When another script IMPORTS this file (import miner), __name__ is "miner".
#
#   The guard `if __name__ == "__main__":` means: "Only execute this block
#   when the file is run directly, NOT when it is imported as a library."
#   This allows us to:
#     1. Run the full pipeline by executing: python miner.py
#     2. Import and reuse extract_scan_features() in other scripts or tests
#        WITHOUT automatically running the whole pipeline.
#   This pattern is STANDARD in every professional Python project.

if __name__ == "__main__":
    # Step 1: Build the feature dataset from the DICOM folder.
    features, names = extract_scan_features(input_folder)

    # Step 2: Cluster and visualise only if we got valid data back.
    # `len(features) > 0` guards against the empty-folder error case.
    if len(features) > 0:
        run_clustering_analysis(features, names)

# =============================================================================
# KEY INTERVIEW TALKING POINTS for this file:
# =============================================================================
# Q: "What is Feature Extraction and why is it important?"
# A: Transforming raw data (images) into compact numerical representations
#    (features) that capture the essential signal.  Good features make ML
#    models more accurate, faster, and interpretable.  "Garbage in, garbage out."
#
# Q: "Why use mean, std, and max as features for medical images?"
# A: These three statistics capture: overall brightness (mean), image quality
#    (std/contrast), and the brightest anatomical structure (max).  They are
#    fast to compute, interpretable by clinicians, and sensitive to scanner faults.
#
# Q: "What business problem does this solve?"
# A: Automated Quality Control.  A faulty X-ray scanner produces systematically
#    different images (wrong brightness/contrast).  K-Means clusters flagging
#    one mobile unit's scans as "outliers" signals a maintenance team to inspect
#    that specific unit — BEFORE misdiagnoses occur from degraded image quality.
#
# Q: "What is the `if __name__ == '__main__':` pattern?"
# A: It separates the "library" (reusable functions) from the "script" (runner code).
#    Functions above the guard can be imported and unit-tested independently.
#    Code inside the guard only runs when the file is executed directly.
#
# Q: "What is NumPy boolean indexing?"
# A: Using a True/False array as a subscript to select elements.
#    X[labels == 0] selects all rows of X where the corresponding label is 0.
#    It is much faster than a Python for-loop because NumPy operations are
#    implemented in C and run at native speed.
# =============================================================================
