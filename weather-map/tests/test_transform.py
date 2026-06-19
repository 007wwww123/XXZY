"""
test_transform.py - 数据转换服务测试
"""

import unittest

import pandas as pd

from weather_map.services.transform import aggregate_to_province, transform_weather_data


class TestTransform(unittest.TestCase):
    def test_transform_api_data(self):
        df = pd.DataFrame(
            {
                "province_name": ["湖北省"],
                "apparent_temperature": ["18.5"],
                "precipitation": ["0.2"],
                "time": ["2026-06-10T12:00"],
            }
        )
        result = transform_weather_data(df)

        self.assertAlmostEqual(result.loc[0, "temperature"], 18.5)
        self.assertAlmostEqual(result.loc[0, "precipitation"], 0.2)
        self.assertEqual(result.loc[0, "date"], "2026-06-10")

    def test_transform_web_data(self):
        df = pd.DataFrame(
            {
                "province_name": ["广东省"],
                "temperature_max": [30],
                "temperature_min": [22],
                "precipitation_sum": [5.5],
                "date": ["2026-06-10"],
            }
        )
        result = transform_weather_data(df)

        self.assertAlmostEqual(result.loc[0, "temperature"], 26.0)
        self.assertAlmostEqual(result.loc[0, "precipitation"], 5.5)

    def test_aggregate_to_province(self):
        df = pd.DataFrame(
            {
                "province_code": ["420000", "420000", "440000"],
                "province_name": ["湖北省", "湖北省", "广东省"],
                "temperature": [20.0, 22.0, 28.0],
                "precipitation": [1.0, 3.0, 0.0],
                "date": ["2026-06-10", "2026-06-10", "2026-06-10"],
            }
        )
        result = aggregate_to_province(df)

        self.assertEqual(len(result), 2)
        self.assertAlmostEqual(result.loc[result["province_code"] == "420000", "temperature"].iloc[0], 21.0)
        self.assertAlmostEqual(result.loc[result["province_code"] == "420000", "precipitation"].iloc[0], 2.0)


if __name__ == "__main__":
    unittest.main()
