"""test_map_join.py - 省名对齐测试"""

import importlib.util
from pathlib import Path
import unittest

import pandas as pd


def _load_align_province_names():
    module_path = Path(__file__).resolve().parents[1] / "src" / "weather_map" / "services" / "map_join.py"
    spec = importlib.util.spec_from_file_location("map_join", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.align_province_names, module.join_with_geojson


align_province_names, join_with_geojson = _load_align_province_names()


class TestMapJoin(unittest.TestCase):
    def test_align_province_names(self):
        root = Path(__file__).resolve().parents[1]
        name_map_path = root / "data" / "geo" / "name_map.json"

        df = pd.DataFrame(
            {
                "province_name": ["湖北省", " 湖南省", "北京", "中国南海十段线"],
                "temperature": [1, 2, 3, 4],
            }
        )

        result = align_province_names(df, str(name_map_path))

        self.assertEqual(result["province_name"].tolist(), ["湖北", "湖南", "北京", "十段线"])
        self.assertEqual(result["province_name_raw"].tolist(), ["湖北省", " 湖南省", "北京", "中国南海十段线"])
        self.assertEqual(result["temperature"].tolist(), [1, 2, 3, 4])

    def test_join_with_geojson_uses_cached_geojson(self):
        root = Path(__file__).resolve().parents[1]
        geojson_path = root / "data" / "geo" / "china_province.geojson"

        df = pd.DataFrame({"province_name": ["北京市"], "temperature": [21]})
        result = join_with_geojson(df, str(geojson_path))

        self.assertEqual(result.loc[0, "geo_fullname"], "北京市")
        self.assertEqual(result.loc[0, "geo_code"], "110000")
        self.assertIsInstance(result.loc[0, "geometry"], dict)


if __name__ == "__main__":
    unittest.main()


