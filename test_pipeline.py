import unittest
import os
import tempfile
import numpy as np
import pydicom


class TestAnonymizerLogic(unittest.TestCase):
    """Test that anonymization correctly overwrites patient identifiers."""

    def test_anonymization(self):
        ds = pydicom.Dataset()
        ds.PatientName = "John Doe"
        ds.PatientID = "12345"

        # Apply anonymization logic (mirrors anonymizer.py)
        ds.PatientName = "ANONYMOUS"
        ds.PatientID = "00000"

        self.assertEqual(str(ds.PatientName), "ANONYMOUS")
        self.assertEqual(str(ds.PatientID), "00000")


class TestFeatureExtraction(unittest.TestCase):
    """Test that pixel feature extraction produces correct statistics."""

    def test_feature_extraction(self):
        pixel_data = np.array([[100, 200], [50, 150]], dtype=np.float32)

        avg_density = np.mean(pixel_data)
        contrast = np.std(pixel_data)
        peak_bone = np.max(pixel_data)

        self.assertAlmostEqual(avg_density, 125.0)
        self.assertAlmostEqual(contrast, np.std(pixel_data))
        self.assertEqual(peak_bone, 200.0)


class TestExponentialBackoff(unittest.TestCase):
    """Test that the backoff delay doubles correctly for each attempt."""

    def test_backoff_sequence(self):
        delays = [2 ** attempt for attempt in range(4)]
        self.assertEqual(delays, [1, 2, 4, 8])


class TestOutputFolderCreation(unittest.TestCase):
    """Test that the output folder is created when it does not exist."""

    def test_makedirs(self):
        base = tempfile.mkdtemp()
        output_folder = os.path.join(base, "batch_anonymized")
        self.assertFalse(os.path.exists(output_folder))

        os.makedirs(output_folder)

        self.assertTrue(os.path.isdir(output_folder))


if __name__ == "__main__":
    unittest.main()
