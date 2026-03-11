"""
测试每日数据缓存功能
验证：当天首次请求获取数据，后续使用缓存
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from alphalens.data_fetcher import IndustryDataFetcher, DailyDataCache
from datetime import datetime


def test_daily_cache():
    """测试每日缓存功能"""
    print("="*60)
    print("AlphaLens Pro - 每日数据缓存测试")
    print("="*60)
    
    # 创建数据获取器（使用临时缓存目录）
    fetcher = IndustryDataFetcher(cache_dir="test_data_cache")
    
    print("\n【测试1】首次获取行业列表（应从API获取）")
    print("-"*60)
    df1 = fetcher.get_industry_list()
    print(f"获取到 {len(df1)} 个行业")
    
    print("\n【测试2】再次获取行业列表（应从缓存获取）")
    print("-"*60)
    df2 = fetcher.get_industry_list()
    print(f"获取到 {len(df2)} 个行业")
    
    print("\n【测试3】获取热门行业（首次）")
    print("-"*60)
    hot1 = fetcher.get_hot_industries()
    print(f"热门行业数量: {len(hot1)}")
    if not hot1.empty:
        print(f"Top 3: {', '.join(hot1.head(3)['板块名称'].tolist())}")
    
    print("\n【测试4】再次获取热门行业（应从缓存获取）")
    print("-"*60)
    hot2 = fetcher.get_hot_industries()
    print(f"热门行业数量: {len(hot2)}")
    
    print("\n【测试5】获取ETF列表（首次）")
    print("-"*60)
    etf1 = fetcher.get_etf_list()
    print(f"ETF数量: {len(etf1)}")
    
    print("\n【测试6】缓存统计信息")
    print("-"*60)
    stats = fetcher.get_daily_cache_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n【测试7】强制刷新缓存")
    print("-"*60)
    fetcher.refresh_daily_cache("hot_industries")
    
    print("\n【测试8】清空缓存")
    print("-"*60)
    fetcher.clear_daily_cache()
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    
    # 清理测试缓存文件
    import shutil
    if os.path.exists("test_data_cache"):
        shutil.rmtree("test_data_cache")
        print("\n已清理测试缓存文件")


def test_cache_mechanism():
    """详细测试缓存机制"""
    print("\n\n" + "="*60)
    print("缓存机制详细测试")
    print("="*60)
    
    cache = DailyDataCache(cache_dir="test_cache_mechanism")
    
    # 模拟数据获取函数
    call_count = 0
    def mock_fetch():
        nonlocal call_count
        call_count += 1
        print(f"  [模拟API调用] 第 {call_count} 次")
        return {"data": f"test_data_{datetime.now()}", "timestamp": datetime.now().isoformat()}
    
    print("\n1. 首次获取数据（应调用API）:")
    result1 = cache.get("test_data", mock_fetch)
    print(f"   结果: {result1['data'][:30]}...")
    
    print("\n2. 第二次获取（应从缓存读取）:")
    result2 = cache.get("test_data", mock_fetch)
    print(f"   结果: {result2['data'][:30]}...")
    
    print("\n3. 强制刷新（应重新调用API）:")
    result3 = cache.get("test_data", mock_fetch, force_refresh=True)
    print(f"   结果: {result3['data'][:30]}...")
    
    print(f"\n4. 总结：API实际被调用了 {call_count} 次（期望3次）")
    
    # 清理
    import shutil
    if os.path.exists("test_cache_mechanism"):
        shutil.rmtree("test_cache_mechanism")


if __name__ == "__main__":
    test_daily_cache()
    test_cache_mechanism()
