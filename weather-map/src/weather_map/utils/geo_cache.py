"""Caching helpers for bundled geographic data files."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pandas as pd

from ..config import NAME_MAP_JSON, PROVINCE_GEOJSON, PROVINCES_CSV
from .paths import get_geo_cache_path


GEO_CACHE_SOURCES = {
    "china_province.geojson": PROVINCE_GEOJSON,
    "name_map.json": NAME_MAP_JSON,
    "provinces.csv": PROVINCES_CSV,
}


def get_cached_geo_file(filename: str, refresh: bool = False) -> Path:
    """Return a cached geographic file path, creating it from the canonical file if needed."""
    if filename not in GEO_CACHE_SOURCES:
        allowed = ", ".join(sorted(GEO_CACHE_SOURCES))
        raise ValueError(f"Unsupported geographic cache file: {filename}. Allowed: {allowed}")

    source_path = GEO_CACHE_SOURCES[filename]
    cache_path = get_geo_cache_path(filename)

    if refresh or not cache_path.exists():
        if not source_path.exists():
            raise FileNotFoundError(f"Geographic source file not found: {source_path}")
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, cache_path)

    return cache_path


def load_cached_geojson(filename: str = "china_province.geojson", refresh: bool = False) -> dict[str, Any]:
    """Load a cached GeoJSON file."""
    cache_path = get_cached_geo_file(filename, refresh=refresh)
    return json.loads(cache_path.read_text(encoding="utf-8"))


def load_cached_name_map(refresh: bool = False) -> dict[str, str]:
    """Load the cached province name map."""
    cache_path = get_cached_geo_file("name_map.json", refresh=refresh)
    return json.loads(cache_path.read_text(encoding="utf-8"))


def load_cached_provinces(refresh: bool = False) -> pd.DataFrame:
    """Load cached province lookup data, including capital coordinates."""
    cache_path = get_cached_geo_file("provinces.csv", refresh=refresh)
    return pd.read_csv(cache_path)
