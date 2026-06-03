"""Tests for geographic data caching."""

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from weather_map.utils import geo_cache


class TestGeoCache(unittest.TestCase):
    def test_get_cached_geo_file_reuses_existing_cache(self):
        cache_path = geo_cache.get_cached_geo_file("name_map.json", refresh=True)
        self.assertTrue(cache_path.exists())
        self.assertEqual(cache_path.parent.name, "geo")
        self.assertEqual(cache_path.parent.parent.name, "cache")

        original_source = geo_cache.GEO_CACHE_SOURCES["name_map.json"]
        geo_cache.GEO_CACHE_SOURCES["name_map.json"] = ROOT / "missing-name-map.json"
        try:
            reused_path = geo_cache.get_cached_geo_file("name_map.json")
        finally:
            geo_cache.GEO_CACHE_SOURCES["name_map.json"] = original_source

        self.assertEqual(reused_path, cache_path)

    def test_load_cached_provinces(self):
        provinces = geo_cache.load_cached_provinces(refresh=True)
        self.assertIn("province_name", provinces.columns)
        self.assertIn("capital_city", provinces.columns)
        self.assertIn("latitude", provinces.columns)
        self.assertIn("longitude", provinces.columns)


if __name__ == "__main__":
    unittest.main()
