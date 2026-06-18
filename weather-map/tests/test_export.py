"""Tests for Parquet export helpers."""

from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from weather_map.services import export as export_module


class TestExport(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.raw_dir = Path(self.temp_dir.name) / "raw"
        self.processed_dir = Path(self.temp_dir.name) / "processed"
        self.original_raw = export_module.RAW_PARQUET_DIR
        self.original_processed = export_module.PROCESSED_PARQUET_DIR
        export_module.RAW_PARQUET_DIR = self.raw_dir
        export_module.PROCESSED_PARQUET_DIR = self.processed_dir

    def tearDown(self):
        export_module.RAW_PARQUET_DIR = self.original_raw
        export_module.PROCESSED_PARQUET_DIR = self.original_processed
        self.temp_dir.cleanup()

    def test_export_raw_and_processed_parquet(self):
        raw_df = pd.DataFrame(
            {
                "province_name": ["湖北省"],
                "temperature": [21.0],
                "precipitation": [1.5],
                "date": ["2026-06-10"],
            }
        )
        processed_df = raw_df.copy()
        processed_df["province_name"] = ["湖北"]

        raw_path = export_module.export_raw_parquet(raw_df, partition_key="2026-06-10")
        processed_path = export_module.export_processed_parquet(processed_df, partition_key="2026-06-10")

        self.assertTrue(Path(raw_path).exists())
        self.assertTrue(Path(processed_path).exists())

        loaded_raw = export_module.read_raw_parquet("2026-06-10")
        loaded_processed = export_module.read_processed_parquet("2026-06-10")

        self.assertEqual(len(loaded_raw), 1)
        self.assertEqual(loaded_processed.loc[0, "province_name"], "湖北")


if __name__ == "__main__":
    unittest.main()
