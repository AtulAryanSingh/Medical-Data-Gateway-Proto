import pydicom
import matplotlib.pyplot as plt
import os
from sklearn.cluster import KMeans


def main():
    # --- SMART LOADER: Finds ANY file in the folder ---
    work_folder = "batch_anonymized"

    if not os.path.exists(work_folder):
        print("ERROR: Folder not found. Run batch_processor.py first!")
        exit()

    # Get ALL files (ignore hidden .DS_Store files)
    files = [f for f in os.listdir(work_folder) if not f.startswith('.')]

    if len(files) == 0:
        print("ERROR: Folder is empty. Batch Processor failed.")
        exit()

    # Pick the first file found, whatever it is named
    target_file = files[0]
    full_path = os.path.join(work_folder, target_file)

    print(f"--> FOUND FILE: {target_file}")
    print(f"--> Loading {full_path} for AI Analysis...")
    # --------------------------------------------------

    # 1. Load Data
    try:
        ds = pydicom.dcmread(full_path, force=True)  # force=True handles missing headers
        pixel_data = ds.pixel_array
    except Exception as e:
        print(f"\nCRITICAL ERROR: Could not read {target_file}.")
        print(f"Details: {e}")
        exit()

    # 2. AI Clustering
    print("Running K-Means Clustering...")
    X = pixel_data.reshape(-1, 1)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(X)
    clustered_pixels = kmeans.labels_.reshape(pixel_data.shape)

    # 3. Visualization
    print("Generating Image...")
    plt.figure(figsize=(10, 5))

    # Left: Original
    plt.subplot(1, 2, 1)
    plt.imshow(pixel_data, cmap='gray')
    try:
        station = ds.get("StationName", "Unknown")
        plt.title(f"Original Scan\n(Source: {station})")
    except:
        plt.title("Original Scan")
    plt.axis('off')

    # Right: AI Segmented
    plt.subplot(1, 2, 2)
    plt.imshow(clustered_pixels, cmap='plasma')
    plt.title("AI Segmentation\n(Air vs Tissue vs Bone)")
    plt.axis('off')

    # Save
    output_file = "highlighted_scan.png"
    plt.savefig(output_file)
    print(f"[SUCCESS] Analysis saved to {output_file}")


if __name__ == "__main__":
    main()