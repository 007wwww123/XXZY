"""
utils/paths.py - 统一路径管理

功能说明：
- 统一路径管理，避免硬编码
- 自动创建必要目录
- 提供缓存和输出路径快捷访问
"""

from pathlib import Path
from typing import Optional

from ..config import (
    CACHE_DIR,
    DATA_DIR,
    GEO_CACHE_DIR,
    GEO_DIR,
    HTML_OUTPUT_DIR,
    LOOKUP_DIR,
    OUTPUTS_DIR,
    PROCESSED_PARQUET_DIR,
    PROJECT_ROOT,
    RAW_PARQUET_DIR,
)


def ensure_dir(path: Path) -> Path:
    """
    确保目录存在

    Args:
        path: 目录路径

    Returns:
        Path: 目录路径
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_project_root() -> Path:
    """
    获取项目根目录

    Returns:
        Path: 项目根目录
    """
    return PROJECT_ROOT


def get_data_dir() -> Path:
    """获取数据目录"""
    return DATA_DIR


def get_cache_dir(subdir: Optional[str] = None) -> Path:
    """
    获取缓存目录

    Args:
        subdir: 子目录名 ('api_responses' 或 'html_pages')

    Returns:
        Path: 缓存目录路径
    """
    if subdir:
        return ensure_dir(CACHE_DIR / subdir)
    return CACHE_DIR


def get_cache_path(filename: str, subdir: Optional[str] = None) -> Path:
    """
    获取缓存文件路径

    Args:
        filename: 文件名
        subdir: 子目录名

    Returns:
        Path: 缓存文件完整路径
    """
    cache_dir = get_cache_dir(subdir)
    return cache_dir / filename


def get_geo_cache_dir() -> Path:
    """Get the geographic data cache directory."""
    return ensure_dir(GEO_CACHE_DIR)


def get_geo_cache_path(filename: str) -> Path:
    """Get a cached geographic data file path."""
    return get_geo_cache_dir() / filename


def get_parquet_dir(processed: bool = False) -> Path:
    """
    获取 Parquet 数据目录

    Args:
        processed: 是否为处理后的数据

    Returns:
        Path: Parquet 目录路径
    """
    if processed:
        return ensure_dir(PROCESSED_PARQUET_DIR)
    return ensure_dir(RAW_PARQUET_DIR)


def get_parquet_path(filename: str, processed: bool = False) -> Path:
    """
    获取 Parquet 文件路径

    Args:
        filename: 文件名
        processed: 是否为处理后的数据

    Returns:
        Path: Parquet 文件完整路径
    """
    parquet_dir = get_parquet_dir(processed)
    return parquet_dir / filename


def get_output_dir(subdir: Optional[str] = None) -> Path:
    """
    获取输出目录

    Args:
        subdir: 子目录名 ('html' 或 'logs')

    Returns:
        Path: 输出目录路径
    """
    if subdir:
        return ensure_dir(OUTPUTS_DIR / subdir)
    return OUTPUTS_DIR


def get_output_path(filename: str, subdir: Optional[str] = None) -> Path:
    """
    获取输出文件路径

    Args:
        filename: 文件名
        subdir: 子目录名

    Returns:
        Path: 输出文件完整路径
    """
    output_dir = get_output_dir(subdir)
    return output_dir / filename


def get_geo_path(filename: str) -> Path:
    """
    获取地理数据文件路径

    Args:
        filename: 文件名

    Returns:
        Path: 地理数据文件路径
    """
    return GEO_DIR / filename


def get_lookup_path(filename: str) -> Path:
    """
    获取查找表文件路径

    Args:
        filename: 文件名

    Returns:
        Path: 查找表文件路径
    """
    return LOOKUP_DIR / filename
