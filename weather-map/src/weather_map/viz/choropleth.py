"""
viz/choropleth.py - 分层设色地图可视化

功能说明：
- 使用 pyecharts 生成省级分层设色地图
- 支持自定义配色和数据范围
- 生成交互式 HTML 地图
"""

import pandas as pd


def create_choropleth_map(df: pd.DataFrame, metric: str, output_path: str = None) -> str:
    """
    创建分层设色地图

    Args:
        df: 省级聚合数据
        metric: 要可视化的指标字段
        output_path: 输出 HTML 文件路径

    Returns:
        str: 生成的 HTML 文件路径
    """
    pass

