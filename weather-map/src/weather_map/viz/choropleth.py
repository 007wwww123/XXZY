"""Generate lightweight province-level choropleth HTML maps."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import HTML_OUTPUT_DIR
from ..utils.paths import ensure_dir


METRIC_LABELS = {
    "temperature": "平均气温",
    "precipitation": "降水量",
    "apparent_temperature": "体感温度",
}

METRIC_UNITS = {
    "temperature": "℃",
    "precipitation": "mm",
    "apparent_temperature": "℃",
}


def _find_name_column(df: pd.DataFrame) -> str:
    for column in ("province_name", "province", "name"):
        if column in df.columns:
            return column
    raise KeyError("DataFrame must contain one of: province_name, province, name")


def _resolve_output_path(df: pd.DataFrame, metric: str, output_path: str | None) -> Path:
    if output_path:
        return Path(output_path)

    date_part = "latest"
    if "date" in df.columns:
        dates = df["date"].dropna().astype(str).str[:10]
        if not dates.empty:
            date_part = dates.iloc[0]

    return HTML_OUTPUT_DIR / f"weather_{date_part}_{metric}.html"


def _build_data_pairs(df: pd.DataFrame, name_column: str, metric: str) -> list[tuple[str, float]]:
    values = pd.to_numeric(df[metric], errors="coerce")
    pairs: list[tuple[str, float]] = []

    for province_name, value in zip(df[name_column], values):
        if pd.isna(province_name) or pd.isna(value):
            continue
        pairs.append((str(province_name).strip(), round(float(value), 2)))

    return pairs


def create_choropleth_map(df: pd.DataFrame, metric: str, output_path: str | None = None) -> str:
    """Create an interactive pyecharts China choropleth map.

    Args:
        df: Province-level weather data. It must include province_name/province/name and metric.
        metric: Numeric metric column to visualize, such as temperature or precipitation.
        output_path: Optional target HTML path. Defaults to outputs/html/weather_DATE_METRIC.html.

    Returns:
        The generated HTML file path.
    """
    if df.empty:
        raise ValueError("Cannot create a choropleth map from an empty DataFrame")
    if metric not in df.columns:
        raise KeyError(f"Metric column not found: {metric}")

    from pyecharts import options as opts
    from pyecharts.charts import Map

    name_column = _find_name_column(df)
    data_pairs = _build_data_pairs(df, name_column, metric)
    if not data_pairs:
        raise ValueError(f"Metric column has no numeric values: {metric}")

    output = _resolve_output_path(df, metric, output_path)
    ensure_dir(output.parent)

    values = [value for _, value in data_pairs]
    metric_label = METRIC_LABELS.get(metric, metric)
    metric_unit = METRIC_UNITS.get(metric, "")

    chart = (
        Map(init_opts=opts.InitOpts(width="1200px", height="760px"))
        .add(
            series_name=metric_label,
            data_pair=data_pairs,
            maptype="china",
            is_map_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"全国省级{metric_label}分布",
                subtitle="基于省级聚合数据生成",
            ),
            tooltip_opts=opts.TooltipOpts(formatter=f"{{b}}<br/>{metric_label}: {{c}} {metric_unit}"),
            visualmap_opts=opts.VisualMapOpts(
                min_=min(values),
                max_=max(values),
                is_calculable=True,
                range_text=["高", "低"],
            ),
        )
    )

    chart.render(str(output))
    return str(output)
