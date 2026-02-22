import os
import pydicom
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# --- CONFIGURATION ---
# This must match the folder created by batch_processor.py
input_folder = "batch_anonymized"

def extract_scan_features(folder):
    """
    Loops through all patients to build the 'University Dataset'.
    Instead of just looking at one image, we compare ALL of them.
    """
    data_points = []
    filenames = []
    
    # Safety Check
    if not os.path.exists(folder):
        print(f"ERROR: Folder '{folder}' not found. Run batch_processor.py first!")
        return [], []

    print(f"--- 1. MINING DATASET GENERATION ---")
    
    # Get all DICOM files
    files = [f for f in os.listdir(folder) if not f.startswith('.')]
    
    if len(files) == 0:
        print("ERROR: No files in folder. Run the batch processor!")
        return [], []

    for f in files:
        full_path = os.path.join(folder, f)
        try:
            # force=True helps read files even if headers are incomplete
            ds = pydicom.dcmread(full_path, force=True)
            pixel_data = ds.pixel_array
            
            # --- THE MINING LOGIC (Extracting "Meta-Features") ---
            # We turn the image into Numbers (Features)
            
            # Feature 1: Average Density (How "bright" is the scan?)
            avg_density = np.mean(pixel_data)
            
            # Feature 2: Contrast (Standard Deviation)
            # High # = Sharp scan (Good). Low # = Blurry/Foggy scan (Bad).
            contrast = np.std(pixel_data)
            
            # Feature 3: Peak Bone Density (Max Value)
            peak_bone = np.max(pixel_data)
            
            # Add to our "Excel Sheet"
            data_points.append([avg_density, contrast, peak_bone])
            filenames.append(f)
            
            print(f"   [MINED] {f} -> Density: {avg_density:.1f} | Contrast: {contrast:.1f}")
            
        except Exception as e:
            print(f"   [SKIP] Could not read {f}: {e}")

    return np.array(data_points), filenames

def run_clustering_analysis(data, filenames):
    """
    The 'Data Mining' part: Finding patterns across the patient population.
    """
    # Safety Check: Need at least 2 files to "cluster" them
    if len(data) < 2:
        print("\n[!] Not enough data to cluster. (Need > 1 file)")
        return

    print("\n--- 2. EXECUTING K-MEANS ALGORITHM ---")
    
    # We use Density (Col 0) and Contrast (Col 1) to group patients
    X = data[:, 0:2] 
    
    # K-Means groups patients into 2 "Clusters" 
    # (e.g., Cluster 0 = Normal Scans, Cluster 1 = Outliers)
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    
    print(f"   [SUCCESS] Classified {len(data)} patients into 2 groups.")

    # --- VISUALIZATION ---
    print("\n--- 3. VISUALIZING POPULATION TRENDS ---")
    plt.figure(figsize=(10, 6))
    
    # Plot Group A (Blue)
    plt.scatter(X[labels == 0, 0], X[labels == 0, 1], 
                s=100, c='blue', label='Cluster A (Standard Scans)')
    
    # Plot Group B (Red)
    plt.scatter(X[labels == 1, 0], X[labels == 1, 1], 
                s=100, c='red', label='Cluster B (Outliers/Mobile Units)')

    # Label specific points so we know which file is which
    for i, txt in enumerate(filenames):
        # Only label every other file to keep it clean
        plt.annotate(txt, (X[i, 0], X[i, 1]), fontsize=9, alpha=0.8, xytext=(5, 5), textcoords='offset points')

    plt.title("MedSendX Data Mining: Patient Population Analysis")
    plt.xlabel("Average Tissue Density (Brightness)")
    plt.ylabel("Scan Contrast (Image Quality)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    print("   [DISPLAY] Opening Analysis Plot...")
    
    # Save it too, just in case
    plt.savefig("mining_report.png")
    print("   [SAVED] Plot saved to 'mining_report.png'")
    
    plt.show()

# --- MAIN RUNNER ---
if __name__ == "__main__":
    # 1. Build the dataset from the images
    features, names = extract_scan_features(input_folder)
    
    # 2. Analyze the dataset
    if len(features) > 0:
        run_clustering_analysis(features, names)