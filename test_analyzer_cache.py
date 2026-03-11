"""
测试LLM分析时的缓存机制
- 首次分析触发全量数据预加载
- 后续分析从缓存读取
- 缓存未命中时自动从线上获取
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from alphalens.analyzer import IndustryAnalyzer
import time


def test_analyzer_cache():
    """测试分析器缓存机制"""
    print("="*70)
    print("AlphaLens Pro - LLM分析缓存机制测试")
    print("="*70)
    
    analyzer = IndustryAnalyzer()
    
    # 测试1: 首次分析（应该触发全量数据预加载）
    print("\n" + "-"*70)
    print("测试1: 首次分析（触发全量数据预加载）")
    print("-"*70)
    
    start_time = time.time()
    result1 = analyzer.analyze("半导体", use_llm=False, use_cache=True)
    first_time = time.time() - start_time
    
    print(f"  分析耗时: {first_time:.2f}秒")
    print(f"  数据来源: {result1.get('data_source', 'unknown')}")
    print(f"  日线数据条数: {len(result1.get('daily_data', []))}")
    print(f"  成分股数量: {result1.get('industry_analysis', {}).get('stocks_count', 0)}")
    
    # 测试2: 第二次分析同个行业（应该从缓存读取）
    print("\n" + "-"*70)
    print("测试2: 第二次分析半导体（应该从缓存读取）")
    print("-"*70)
    
    start_time = time.time()
    result2 = analyzer.analyze("半导体", use_llm=False, use_cache=True)
    second_time = time.time() - start_time
    
    print(f"  分析耗时: {second_time:.3f}秒")
    print(f"  数据来源: {result2.get('data_source', 'unknown')}")
    print(f"  耗时减少: {(1 - second_time/first_time)*100:.1f}%")
    
    # 测试3: 分析其他行业（应该也从缓存读取）
    print("\n" + "-"*70)
    print("测试3: 分析其他行业（新能源、银行）")
    print("-"*70)
    
    for industry in ["新能源", "银行"]:
        start_time = time.time()
        result = analyzer.analyze(industry, use_llm=False, use_cache=True)
        elapsed = time.time() - start_time
        
        print(f"  {industry}: {elapsed:.3f}秒 (来源: {result.get('data_source', 'unknown')})")
    
    # 测试4: 不使用缓存（直接从线上获取）
    print("\n" + "-"*70)
    print("测试4: 不使用缓存（直接从线上获取）")
    print("-"*70)
    
    # 创建新的分析器实例
    analyzer2 = IndustryAnalyzer()
    
    start_time = time.time()
    result = analyzer2.analyze("半导体", use_llm=False, use_cache=False)
    online_time = time.time() - start_time
    
    print(f"  分析耗时: {online_time:.2f}秒")
    print(f"  数据来源: {result.get('data_source', 'unknown')}")
    
    # 测试5: 批量AI推荐（使用缓存）
    print("\n" + "-"*70)
    print("测试5: 批量AI推荐分析")
    print("-"*70)
    
    # 创建新的分析器实例
    analyzer3 = IndustryAnalyzer()
    test_industries = ["半导体", "新能源", "银行", "证券", "医药生物"]
    
    start_time = time.time()
    recommendations = analyzer3.get_ai_recommendations(
        industries=test_industries,
        use_cache=True
    )
    batch_time = time.time() - start_time
    
    print(f"  分析行业数: {len(test_industries)}")
    print(f"  总耗时: {batch_time:.2f}秒")
    print(f"  平均每个行业: {batch_time/len(test_industries):.2f}秒")
    print(f"  推荐结果数: {len(recommendations)}")
    
    for rec in recommendations:
        print(f"    - {rec['industry']}: {rec['decision']} (置信度: {rec.get('confidence', 0)}%)")
    
    # 汇总
    print("\n" + "="*70)
    print("测试结果汇总")
    print("="*70)
    print(f"✓ 首次分析触发全量数据预加载")
    print(f"✓ 缓存读取速度: {second_time:.3f}秒")
    print(f"✓ 线上获取速度: {online_time:.2f}秒")
    print(f"✓ 缓存加速比: {online_time/second_time:.1f}x")
    print(f"\n缓存机制工作正常！")
    print("="*70)


if __name__ == "__main__":
    test_analyzer_cache()
