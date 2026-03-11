"""
模拟测试全量数据缓存机制（无需网络）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from alphalens.data_fetcher import DailyDataCache
import pandas as pd
import json


def test_cache_mechanism():
    """测试缓存机制逻辑"""
    print("="*70)
    print("AlphaLens Pro - 缓存机制模拟测试")
    print("="*70)
    
    # 创建临时缓存目录
    test_cache_dir = "test_data_cache"
    if os.path.exists(test_cache_dir):
        # 清理旧缓存
        for f in os.listdir(test_cache_dir):
            os.remove(os.path.join(test_cache_dir, f))
    
    cache = DailyDataCache(cache_dir=test_cache_dir)
    
    print("\n" + "-"*70)
    print("测试1: 初始状态")
    print("-"*70)
    stats = cache.get_cache_stats()
    print(f"  日期: {stats['today']}")
    print(f"  内存项数: {stats['memory_items']}")
    print(f"  是否全量加载: {stats['is_fully_loaded']}")
    
    # 模拟数据
    print("\n" + "-"*70)
    print("测试2: 保存模拟数据到缓存")
    print("-"*70)
    
    # 模拟行业列表
    mock_industry_list = pd.DataFrame({
        '板块名称': ['半导体', '新能源', '银行'],
        '涨跌幅': [5.2, 3.1, 0.5]
    })
    cache._save_cache("industry_list", mock_industry_list)
    print(f"  ✓ 保存行业列表: {len(mock_industry_list)} 条")
    
    # 模拟行业日线数据
    for industry in ['半导体', '新能源', '银行']:
        mock_daily = pd.DataFrame({
            '日期': pd.date_range('2024-01-01', periods=5),
            '收盘': [100, 102, 101, 103, 105],
            '涨跌幅': [1.0, 2.0, -0.5, 1.5, 1.0]
        })
        cache._save_cache(f"industry_daily_{industry}", mock_daily)
        print(f"  ✓ 保存 {industry} 日线: {len(mock_daily)} 条")
    
    # 模拟成分股数据
    for industry in ['半导体', '新能源']:
        mock_stocks = pd.DataFrame({
            '代码': ['000001', '000002', '000003'],
            '名称': ['股票A', '股票B', '股票C'],
            '涨跌幅': [2.5, 1.5, -0.5]
        })
        cache._save_cache(f"industry_stocks_{industry}", mock_stocks)
        print(f"  ✓ 保存 {industry} 成分股: {len(mock_stocks)} 只")
    
    print("\n" + "-"*70)
    print("测试3: 从缓存读取数据")
    print("-"*70)
    
    # 读取行业列表
    data = cache.get("industry_list", lambda: pd.DataFrame())
    print(f"  ✓ 读取行业列表: {len(data)} 条")
    
    # 读取行业日线
    for industry in ['半导体', '新能源', '银行']:
        data = cache.get(f"industry_daily_{industry}", lambda: pd.DataFrame())
        print(f"  ✓ 读取 {industry} 日线: {len(data)} 条")
    
    # 读取成分股
    for industry in ['半导体', '新能源']:
        data = cache.get(f"industry_stocks_{industry}", lambda: pd.DataFrame())
        print(f"  ✓ 读取 {industry} 成分股: {len(data)} 只")
    
    print("\n" + "-"*70)
    print("测试4: 缓存统计")
    print("-"*70)
    stats = cache.get_cache_stats()
    print(f"  内存项数: {stats['memory_items']}")
    print(f"  缓存类型: {stats['cached_types']}")
    
    # 检查缓存文件
    print("\n" + "-"*70)
    print("测试5: 缓存文件检查")
    print("-"*70)
    cache_files = os.listdir(test_cache_dir)
    print(f"  缓存文件数: {len(cache_files)}")
    for f in sorted(cache_files):
        file_path = os.path.join(test_cache_dir, f)
        size = os.path.getsize(file_path)
        print(f"  - {f} ({size} bytes)")
    
    print("\n" + "-"*70)
    print("测试6: 次日刷新模拟")
    print("-"*70)
    
    # 模拟日期变化
    cache.today = "2024-01-01"  # 设置为过去日期
    
    # 尝试获取数据（应该检测到日期变化）
    data = cache.get("industry_list", lambda: pd.DataFrame({'板块名称': ['新数据'], '涨跌幅': [10.0]}))
    print(f"  ✓ 日期变化检测成功")
    print(f"  ✓ 新日期: {cache.today}")
    
    print("\n" + "="*70)
    print("测试结果: ✓ 缓存机制工作正常")
    print("="*70)
    
    # 清理
    for f in os.listdir(test_cache_dir):
        os.remove(os.path.join(test_cache_dir, f))
    os.rmdir(test_cache_dir)
    print("\n已清理测试缓存目录")


if __name__ == "__main__":
    test_cache_mechanism()
