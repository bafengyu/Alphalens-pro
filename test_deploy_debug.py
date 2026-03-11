"""
调试部署后的数据获取问题
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from alphalens.data_fetcher import IndustryDataFetcher
from alphalens.analyzer import IndustryAnalyzer

print("="*70)
print("AlphaLens Pro - 部署调试")
print("="*70)

# 测试1: 直接获取数据
print("\n测试1: 直接获取数据（不使用缓存）")
fetcher = IndustryDataFetcher()

try:
    industries = fetcher.get_industry_list(use_daily_cache=False)
    print(f"  行业列表: {len(industries)} 个")
    if len(industries) > 0:
        print(f"  前3个行业: {industries['板块名称'].head(3).tolist()}")
except Exception as e:
    print(f"  ERROR: {e}")

# 测试2: 使用缓存获取
print("\n测试2: 使用缓存获取")
try:
    industries = fetcher.get_industry_list(use_daily_cache=True)
    print(f"  行业列表: {len(industries)} 个")
except Exception as e:
    print(f"  ERROR: {e}")

# 测试3: 分析器
print("\n测试3: 分析器")
analyzer = IndustryAnalyzer()

try:
    result = analyzer.analyze("半导体", use_llm=False, use_cache=True)
    print(f"  分析结果:")
    print(f"    数据来源: {result.get('data_source', 'unknown')}")
    print(f"    日线数据: {len(result.get('daily_data', []))} 条")
    print(f"    成分股数: {result.get('industry_analysis', {}).get('stocks_count', 0)}")
    print(f"    错误信息: {result.get('error', '无')}")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()

# 测试4: 检查缓存状态
print("\n测试4: 缓存状态")
stats = fetcher.get_daily_cache_stats()
print(f"  日期: {stats['today']}")
print(f"  内存项数: {stats['memory_items']}")
print(f"  是否全量加载: {stats['is_fully_loaded']}")
print(f"  缓存类型: {stats['cached_types']}")

print("\n" + "="*70)
print("调试完成")
print("="*70)
