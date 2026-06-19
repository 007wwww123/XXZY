"""Tests for lightweight pyecharts map export."""

from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from weather_map.viz.choropleth import create_choropleth_map


class TestChoropleth(unittest.TestCase):
    def test_create_choropleth_map_writes_html(self):
        df = pd.DataFrame(
            {
                "province_name": ["湖北", "广东"],
                "temperature": [21.5, 28.2],
                "date": ["2026-06-10", "2026-06-10"],
            }
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "temperature_map.html"
            rendered_path = create_choropleth_map(df, "temperature", str(output_path))

            self.assertEqual(Path(rendered_path), output_path)
            self.assertTrue(output_path.exists())

            html = output_path.read_text(encoding="utf-8")
            self.assertIn("\\u5168\\u56fd\\u7701\\u7ea7\\u5e73\\u5747\\u6c14\\u6e29\\u5206\\u5e03", html)
            self.assertIn("\\u6e56\\u5317", html)
            self.assertIn("\\u5e7f\\u4e1c", html)


if __name__ == "__main__":
    unittest.main()
