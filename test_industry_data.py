"""
验证所有预设行业都能获取到行情数据
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from alphalens.data_fetcher import IndustryDataFetcher, INDUSTRY_NAME_MAP
import pandas as pd


def test_all_preset_industries():
    """测试所有预设行业数据获取"""
    
    # 预设行业列表（来自app.py中的常用行业）
    preset_industries = [
        "半导体", "新能源", "医药生物", "食品饮料", "电子元件",
        "软件服务", "互联网", "通信设备", "银行", "证券",
        "房地产", "建筑工程", "有色金属", "化工行业", "汽车整车",
        "电力行业", "军工", "传媒", "环保", "纺织服装"
    ]
    
    print("="*70)
    print("AlphaLens Pro - 预设行业数据验证")
    print("="*70)
    
    fetcher = IndustryDataFetcher()
    
    results = {
        "success": [],
        "failed": [],
        "mapped": []
    }
    
    print(f"\n待验证行业数量: {len(preset_industries)}")
    print("-"*70)
    
    for i, industry in enumerate(preset_industries, 1):
        print(f"\n[{i}/{len(preset_industries)}] 测试行业: {industry}")
        
        try:
            # 1. 测试行业名称匹配
            matched_name = fetcher._match_industry_name(industry)
            if matched_name != industry:
                print(f"  [映射] {industry} -> {matched_name}")
                results["mapped"].append((industry, matched_name))
            
            # 2. 测试获取行业日线数据
            daily_df = fetcher.get_industry_daily(matched_name, days=5)
            
            if daily_df is not None and not daily_df.empty:
                data_count = len(daily_df)
                latest_close = daily_df.iloc[-1].get('收盘', 'N/A') if '收盘' in daily_df.columns else 'N/A'
                
                print(f"  [✓] 数据获取成功: {data_count} 条")
                print(f"      最新收盘价: {latest_close}")
                results["success"].append(industry)
            else:
                print(f"  [✗] 数据为空")
                results["failed"].append((industry, "数据为空"))
                
        except Exception as e:
            print(f"  [✗] 获取失败: {str(e)[:50]}")
            results["failed"].append((industry, str(e)))
    
    # 打印汇总
    print("\n" + "="*70)
    print("验证结果汇总")
    print("="*70)
    
    total = len(preset_industries)
    success_count = len(results["success"])
    failed_count = len(results["failed"])
    mapped_count = len(results["mapped"])
    
    print(f"\n总行业数: {total}")
    print(f"成功: {success_count} ({success_count/total*100:.1f}%)")
    print(f"失败: {failed_count} ({failed_count/total*100:.1f}%)")
    print(f"名称映射: {mapped_count}")
    
    if results["mapped"]:
        print("\n名称映射详情:")
        for original, mapped in results["mapped"]:
            print(f"  {original} -> {mapped}")
    
    if results["failed"]:
        print("\n失败详情:")
        for industry, error in results["failed"]:
            print(f"  [✗] {industry}: {error}")
    
    # 测试热门行业获取
    print("\n" + "="*70)
    print("热门行业数据验证")
    print("="*70)
    
    try:
        hot_industries = fetcher.get_hot_industries(use_daily_cache=False)
        if not hot_industries.empty:
            print(f"\n获取到 {len(hot_industries)} 个热门行业:")
            for idx, row in hot_industries.head(5).iterrows():
                name = row.get('板块名称', 'N/A')
                change = row.get('涨跌幅', 'N/A')
                print(f"  {name}: {change}%")
        else:
            print("[✗] 热门行业数据为空")
    except Exception as e:
        print(f"[✗] 获取热门行业失败: {e}")
    
    # 测试ETF列表获取
    print("\n" + "="*70)
    print("ETF列表数据验证")
    print("="*70)
    
    try:
        etf_list = fetcher.get_etf_list(use_daily_cache=False)
        if not etf_list.empty:
            print(f"\n获取到 {len(etf_list)} 只ETF")
            # 显示前5只
            for idx, row in etf_list.head(5).iterrows():
                name = row.get('名称', 'N/A')
                code = row.get('代码', 'N/A')
                print(f"  {code}: {name}")
        else:
            print("[✗] ETF列表为空")
    except Exception as e:
        print(f"[✗] 获取ETF列表失败: {e}")
    
    print("\n" + "="*70)
    print("验证完成!")
    print("="*70)
    
    return results


def test_industry_analysis():
    """测试行业分析功能"""
    print("\n\n" + "="*70)
    print("行业趋势分析验证")
    print("="*70)
    
    fetcher = IndustryDataFetcher()
    test_industries = ["半导体", "新能源", "银行"]
    
    for industry in test_industries:
        print(f"\n分析行业: {industry}")
        try:
            analysis = fetcher.analyze_industry_trend(industry)
            print(f"  成分股数: {analysis.get('stocks_count', 0)}")
            print(f"  平均涨跌: {analysis.get('avg_change', 0):.2f}%")
            print(f"  上涨家数: {analysis.get('up_count', 0)}")
            print(f"  下跌家数: {analysis.get('down_count', 0)}")
            print(f"  综合建议: {analysis.get('recommendation', 'N/A')}")
        except Exception as e:
            print(f"  [✗] 分析失败: {e}")


if __name__ == "__main__":
    results = test_all_preset_industries()
    test_industry_analysis()
