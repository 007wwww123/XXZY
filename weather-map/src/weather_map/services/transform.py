"""
services/transform.py - 数据转换和清洗服务

功能说明：
- 清洗和标准化原始数据
- 处理缺失值
- 数据类型转换
- 按省级聚合（省会代表点）
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

NUMERIC_METRIC_COLUMNS = ("temperature", "precipitation", "apparent_temperature")
META_COLUMNS = ("province_name", "province_code", "region", "capital_city", "date", "time", "weathercode")


def transform_weather_data(df: pd.DataFrame) -> pd.DataFrame:
    """转换和清洗天气数据，统一 API 与网页爬取两种来源的字段。"""
    if df.empty:
        return df.copy()

    result = df.copy()

    if "temperature" not in result.columns:
        if "apparent_temperature" in result.columns:
            result["temperature"] = pd.to_numeric(result["apparent_temperature"], errors="coerce")
        elif {"temperature_max", "temperature_min"}.issubset(result.columns):
            max_temp = pd.to_numeric(result["temperature_max"], errors="coerce")
            min_temp = pd.to_numeric(result["temperature_min"], errors="coerce")
            result["temperature"] = (max_temp + min_temp) / 2
        elif "temperature_2m" in result.columns:
            result["temperature"] = pd.to_numeric(result["temperature_2m"], errors="coerce")

    if "precipitation" not in result.columns or result["precipitation"].isna().all():
        if "precipitation_sum" in result.columns:
            result["precipitation"] = pd.to_numeric(result["precipitation_sum"], errors="coerce")
    result["precipitation"] = pd.to_numeric(result.get("precipitation"), errors="coerce")
    result["temperature"] = pd.to_numeric(result.get("temperature"), errors="coerce")

    if "apparent_temperature" in result.columns:
        result["apparent_temperature"] = pd.to_numeric(result["apparent_temperature"], errors="coerce")

    if "date" not in result.columns or result["date"].isna().all():
        if "time" in result.columns:
            result["date"] = pd.to_datetime(result["time"], errors="coerce").dt.strftime("%Y-%m-%d")
        else:
            result["date"] = datetime.now().strftime("%Y-%m-%d")
    else:
        result["date"] = result["date"].astype(str).str[:10]

    return result


def aggregate_to_province(df: pd.DataFrame) -> pd.DataFrame:
    """按省级单位聚合数据（默认每省一行，对数值字段取均值）。"""
    if df.empty:
        return df.copy()

    group_key = "province_code" if "province_code" in df.columns else "province_name"
    agg_rules: dict[str, str] = {}

    for column in NUMERIC_METRIC_COLUMNS:
        if column in df.columns:
            agg_rules[column] = "mean"

    for column in META_COLUMNS:
        if column in df.columns and column != group_key:
            agg_rules[column] = "first"

    aggregated = df.groupby(group_key, as_index=False).agg(agg_rules)
    return aggregated.sort_values(group_key).reset_index(drop=True)
