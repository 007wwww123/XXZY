"""
services/export.py - 数据导出服务

功能说明：
- 将处理后的数据导出为 Parquet 格式
- 支持原始数据和处理后数据的不同输出
- 按日期分区命名文件
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from ..config import PROCESSED_PARQUET_DIR, RAW_PARQUET_DIR
from ..utils.paths import ensure_dir


def _resolve_partition_key(partition_key: str | None, df: pd.DataFrame) -> str:
    """从参数或 DataFrame 中解析分区日期。"""
    if partition_key:
        return str(partition_key)[:10]

    if "date" in df.columns:
        first_date = df["date"].dropna().astype(str).str[:10]
        if not first_date.empty:
            return first_date.iloc[0]

    if "time" in df.columns:
        parsed = pd.to_datetime(df["time"], errors="coerce").dropna()
        if not parsed.empty:
            return parsed.iloc[0].strftime("%Y-%m-%d")

    return datetime.now().strftime("%Y-%m-%d")


def _build_output_path(base_dir, partition_key: str, suffix: str) -> str:
    ensure_dir(base_dir)
    filename = f"weather_{partition_key}_{suffix}.parquet"
    return str(base_dir / filename)


def export_raw_parquet(df: pd.DataFrame, partition_key: str | None = None) -> str:
    """导出原始结构化数据为 Parquet。"""
    if df.empty:
        raise ValueError("无法导出空的原始数据集")

    key = _resolve_partition_key(partition_key, df)
    output_path = _build_output_path(RAW_PARQUET_DIR, key, "raw")
    df.to_parquet(output_path, index=False, engine="pyarrow")
    return output_path


def export_processed_parquet(df: pd.DataFrame, partition_key: str | None = None) -> str:
    """导出处理后的省级数据为 Parquet。"""
    if df.empty:
        raise ValueError("无法导出空的处理后数据集")

    key = _resolve_partition_key(partition_key, df)
    output_path = _build_output_path(PROCESSED_PARQUET_DIR, key, "processed")
    df.to_parquet(output_path, index=False, engine="pyarrow")
    return output_path


def read_raw_parquet(partition_key: str) -> pd.DataFrame:
    """读取指定日期的原始 Parquet 文件。"""
    path = _build_output_path(RAW_PARQUET_DIR, partition_key[:10], "raw")
    return pd.read_parquet(path, engine="pyarrow")


def read_processed_parquet(partition_key: str) -> pd.DataFrame:
    """读取指定日期的处理后 Parquet 文件。"""
    path = _build_output_path(PROCESSED_PARQUET_DIR, partition_key[:10], "processed")
    return pd.read_parquet(path, engine="pyarrow")
