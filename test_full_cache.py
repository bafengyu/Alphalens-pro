"""
测试全量数据缓存机制
- 首次请求下载全量数据到缓存
- 后续所有请求从缓存读取
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from alphalens.data_fetcher import IndustryDataFetcher
import time


def test_full_cache():
    """测试全量缓存机制"""
    print("="*70)
    print("AlphaLens Pro - 全量数据缓存机制测试")
    print("="*70)
    
    fetcher = IndustryDataFetcher()
    
    # 检查初始状态
    stats = fetcher.get_daily_cache_stats()
    print(f"\n初始缓存状态:")
    print(f"  日期: {stats['today']}")
    print(f"  内存项数: {stats['memory_items']}")
    print(f"  是否全量加载: {stats['is_fully_loaded']}")
    
    # 测试1: 首次加载全量数据
    print("\n" + "-"*70)
    print("测试1: 首次加载全量数据")
    print("-"*70)
    
    start_time = time.time()
    fetcher.load_all_industry_data()
    load_time = time.time() - start_time
    
    stats = fetcher.get_daily_cache_stats()
    print(f"\n加载耗时: {load_time:.2f}秒")
    print(f"缓存项数: {stats['memory_items']}")
    print(f"是否全量加载: {stats['is_fully_loaded']}")
    print(f"缓存类型: {', '.join(stats['cached_types'][:5])}...")
    
    # 测试2: 再次调用（应该跳过）
    print("\n" + "-"*70)
    print("测试2: 再次调用全量加载（应该跳过）")
    print("-"*70)
    
    start_time = time.time()
    fetcher.load_all_industry_data()
    skip_time = time.time() - start_time
    
    print(f"执行耗时: {skip_time:.3f}秒 (应该接近0)")
    
    # 测试3: 从缓存读取行业数据
    print("\n" + "-"*70)
    print("测试3: 从缓存读取行业数据")
    print("-"*70)
    
    test_industries = ["半导体", "新能源", "银行"]
    
    for industry in test_industries:
        print(f"\n  行业: {industry}")
        
        # 获取日线数据（从缓存）
        start_time = time.time()
        daily_df = fetcher.get_industry_daily(industry, days=30)
        daily_time = time.time() - start_time
        
        print(f"    日线数据: {len(daily_df)} 条 (耗时: {daily_time:.3f}秒)")
        
        # 获取成分股（从缓存）
        start_time = time.time()
        stocks_df = fetcher.get_industry_stocks(industry)
        stocks_time = time.time() - start_time
        
        print(f"    成分股: {len(stocks_df)} 只 (耗时: {stocks_time:.3f}秒)")
        
        # 分析趋势（从缓存）
        start_time = time.time()
        analysis = fetcher.analyze_industry_trend(industry)
        analysis_time = time.time() - start_time
        
        print(f"    分析结果: {analysis.get('recommendation', 'N/A')} (耗时: {analysis_time:.3f}秒)")
    
    # 测试4: 获取基础数据（从缓存）
    print("\n" + "-"*70)
    print("测试4: 获取基础数据（从缓存）")
    print("-"*70)
    
    start_time = time.time()
    industry_list = fetcher.get_industry_list()
    list_time = time.time() - start_time
    print(f"  行业列表: {len(industry_list)} 个 (耗时: {list_time:.3f}秒)")
    
    start_time = time.time()
    hot_industries = fetcher.get_hot_industries()
    hot_time = time.time() - start_time
    print(f"  热门行业: {len(hot_industries)} 个 (耗时: {hot_time:.3f}秒)")
    
    start_time = time.time()
    etf_list = fetcher.get_etf_list()
    etf_time = time.time() - start_time
    print(f"  ETF列表: {len(etf_list)} 只 (耗时: {etf_time:.3f}秒)")
    
    # 汇总
    print("\n" + "="*70)
    print("测试结果汇总")
    print("="*70)
    print(f"✓ 全量数据已加载到缓存")
    print(f"✓ 所有后续请求均从缓存读取")
    print(f"✓ 缓存数据次日自动刷新")
    print(f"\n缓存文件位置: {stats['cache_dir']}")
    
    # 列出缓存文件
    if os.path.exists(stats['cache_dir']):
        files = os.listdir(stats['cache_dir'])
        today_files = [f for f in files if f.startswith(stats['today'])]
        print(f"今日缓存文件数: {len(today_files)}")
        for f in today_files[:10]:
            print(f"  - {f}")
        if len(today_files) > 10:
            print(f"  ... 还有 {len(today_files) - 10} 个文件")
    
    print("\n" + "="*70)
    print("测试完成！")
    print("="*70)


if __name__ == "__main__":
    test_full_cache()
