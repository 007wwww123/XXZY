"""数据抓取服务。

功能说明：
- 根据指定数据源获取原始天气数据
- 支持 API 和网页爬取两种方式
- 提供全国省级批量抓取入口
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import pandas as pd

from ..adapters.open_meteo_api import OpenMeteoAdapter
from ..adapters.weather_web import WeatherWebAdapter
from ..config import PROVINCES_CSV, CACHE_DIR

PROVINCE_COLUMNS = (
    "province_name",
    "province_code",
    "region",
    "capital_city",
    "latitude",
    "longitude",
)

WEATHER_COLUMNS = (
    "time",
    "apparent_temperature",
    "weathercode",
    "precipitation",
)


def fetch_weather_data(source: str, **kwargs) -> pd.DataFrame:
    """获取天气数据。

    Args:
        source: 数据源 ('api' 或 'web')
        **kwargs: 其他参数

    Returns:
        pd.DataFrame: 原始天气数据
    """
    source = source.lower().strip()

    if source == "api":
        return OpenMeteoAdapter().fetch_data(**kwargs)
    elif source == "web":
        return WeatherWebAdapter().fetch_data(**kwargs)
    elif source == "web15d":
        return WeatherWebAdapter().fetch_15day_forecast(**kwargs)

    raise NotImplementedError(f"Unsupported source: {source}")


def _normalize_batch_frame(df: pd.DataFrame, row: pd.Series) -> pd.DataFrame:
    """补齐省级元数据，并只保留最终需要的天气字段。"""
    result = df.copy()

    for column in PROVINCE_COLUMNS:
        if column not in result.columns:
            result[column] = row.get(column)

    keep_columns = [column for column in (*PROVINCE_COLUMNS, *WEATHER_COLUMNS) if column in result.columns]
    return result.loc[:, keep_columns]


def fetch_all_provinces(
    provinces_csv: str | None = None,
    max_workers: int = 3,
    max_retries: int = 2,
    backoff_factor: float = 0.5,
    rate_sleep: float = 0.2,
) -> pd.DataFrame:
    """按 provinces.csv 批量抓取全国省级天气数据。

    增强点：并发、重试、简单限速与失败记录。
    参数化并发/重试/退避/限速以便在运行时调整。
    """
    csv_path = provinces_csv or str(PROVINCES_CSV)
    provinces = pd.read_csv(csv_path)

    results: list[pd.DataFrame] = []
    failures: list[dict] = []

    def worker(row: pd.Series, max_retries: int, backoff_factor: float, rate_sleep: float) -> Optional[pd.DataFrame]:
        adapter = OpenMeteoAdapter()
        for attempt in range(max_retries + 1):
            try:
                df = adapter.fetch_data(
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                    province_name=row.get("province_name"),
                    province_code=row.get("province_code"),
                    region=row.get("region"),
                    capital_city=row.get("capital_city"),
                )
                if not isinstance(df, pd.DataFrame) or df.empty:
                    raise RuntimeError("empty response")

                normalized = _normalize_batch_frame(df, row)
                # 简单限速
                time.sleep(rate_sleep)
                return normalized
            except Exception:
                if attempt < max_retries:
                    time.sleep(backoff_factor * (2 ** attempt))
                    continue
                # 最后一次失败
                return None

    # 并发执行
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(worker, row, max_retries, backoff_factor, rate_sleep): row for _, row in provinces.iterrows()}
        for fut in as_completed(futures):
            row = futures[fut]
            try:
                res = fut.result()
                if res is None:
                    failures.append({"province_name": row.get("province_name"), "province_code": row.get("province_code")})
                else:
                    results.append(res)
            except Exception:
                failures.append({"province_name": row.get("province_name"), "province_code": row.get("province_code")})

    # 记录失败到 cache 以便重跑或排查
    if failures:
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            import json
            ts = int(time.time())
            path = CACHE_DIR / f"fetch_failures_{ts}.json"
            path.write_text(json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    if results:
        return pd.concat(results, ignore_index=True)

    return pd.DataFrame()
