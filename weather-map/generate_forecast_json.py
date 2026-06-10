"""
生成15天预报数据文件（包含港澳台地区）
"""

import sys
import os
import json
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from weather_map.adapters.weather_web import WeatherWebAdapter
from weather_map.services.fetch import fetch_weather_data


def generate_15day_forecast_json():
    """生成15天预报JSON文件"""
    print("=" * 60)
    print("开始生成15天预报数据（包含港澳台地区）...")
    print("=" * 60)
    
    # 使用web15d数据源获取15天预报
    adapter = WeatherWebAdapter()
    df = adapter.fetch_15day_forecast()
    
    if df.empty:
        print("❌ 数据获取失败，DataFrame为空")
        return False
    
    print(f"\n✅ 成功获取 {len(df)} 条记录")
    print(f"   包含省份: {df['province_name'].unique().tolist()}")
    
    # 转换为前端需要的JSON格式
    data_dict = {}
    province_names = df['province_name'].unique()
    
    for province in province_names:
        province_df = df[df['province_name'] == province]
        city_name = province_df['city_name'].iloc[0] if len(province_df) > 0 else province
        
        for _, row in province_df.iterrows():
            date_str = row['date']
            if date_str not in data_dict:
                data_dict[date_str] = {}
            
            data_dict[date_str][province] = {
                'city': city_name,
                'temp_max': int(row['temp_max']) if pd.notna(row['temp_max']) else None,
                'temp_min': int(row['temp_min']) if pd.notna(row['temp_min']) else None,
                'precip': float(row['precip']) if pd.notna(row['precip']) else 0.0
            }
    
    # 构建最终JSON结构
    result = {
        'provider': 'weather.com.cn',
        'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_cities': len(province_names),
        'total_records': len(df),
        'data': data_dict
    }
    
    # 保存到web目录
    output_path = os.path.join(os.path.dirname(__file__), 'web', 'weather_15day_forecast.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ JSON文件已保存: {output_path}")
    print(f"   总天数: {len(data_dict)}")
    print(f"   总省份: {len(province_names)}")
    
    # 检查港澳台数据
    hkmt_provinces = ['台湾省', '香港特别行政区', '澳门特别行政区']
    for province in hkmt_provinces:
        if province in province_names:
            print(f"   ✅ {province} 数据已包含")
        else:
            print(f"   ❌ {province} 数据缺失")
    
    return True


if __name__ == '__main__':
    import pandas as pd
    success = generate_15day_forecast_json()
    if success:
        print("\n" + "=" * 60)
        print("数据生成完成！")
        print("=" * 60)
    else:
        print("\n数据生成失败，请检查网络连接和爬虫逻辑")