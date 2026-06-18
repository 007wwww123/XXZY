"""
cli.py - 命令行入口

功能说明：
- 抓取天气数据
- 清洗与省级聚合
- 导出 Parquet（raw / processed）
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from .config import DEFAULT_SOURCE, NAME_MAP_JSON
from .services.export import export_processed_parquet, export_raw_parquet
from .services.fetch import fetch_all_provinces, fetch_weather_data
from .services.map_join import align_province_names
from .services.transform import aggregate_to_province, transform_weather_data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="全国省级天气数据抓取与 Parquet 存储")
    parser.add_argument(
        "--source",
        choices=("api", "web"),
        default=DEFAULT_SOURCE,
        help="数据来源：api（Open-Meteo）或 web（中国天气网）",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="数据日期，格式 YYYY-MM-DD，默认今天",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=3,
        help="API 批量抓取并发数（仅 source=api 时生效）",
    )
    return parser


def run_pipeline(source: str, date: str | None = None, max_workers: int = 3) -> dict[str, str]:
    """执行抓取 → 清洗 → 导出 raw → 聚合 → 对齐 → 导出 processed。"""
    partition_key = date or datetime.now().strftime("%Y-%m-%d")

    if source == "api":
        raw_df = fetch_all_provinces(max_workers=max_workers)
    else:
        raw_df = fetch_weather_data(source="web", date=partition_key)

    if raw_df.empty:
        raise RuntimeError("未获取到任何天气数据，请检查网络或数据源配置")

    cleaned_df = transform_weather_data(raw_df)
    cleaned_df["date"] = partition_key

    raw_path = export_raw_parquet(cleaned_df, partition_key=partition_key)

    province_df = aggregate_to_province(cleaned_df)
    aligned_df = align_province_names(province_df, str(NAME_MAP_JSON))
    processed_path = export_processed_parquet(aligned_df, partition_key=partition_key)

    return {
        "raw": raw_path,
        "processed": processed_path,
        "rows_raw": str(len(cleaned_df)),
        "rows_processed": str(len(aligned_df)),
        "date": partition_key,
        "source": source,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = run_pipeline(source=args.source, date=args.date, max_workers=args.max_workers)
    except Exception as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    print("数据存储完成：")
    print(f"  日期: {result['date']}")
    print(f"  来源: {result['source']}")
    print(f"  原始记录: {result['rows_raw']} 行 → {result['raw']}")
    print(f"  省级记录: {result['rows_processed']} 行 → {result['processed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
