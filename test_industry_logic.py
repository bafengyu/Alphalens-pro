"""
验证行业数据获取逻辑（使用模拟数据，无需网络）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from alphalens.data_fetcher import INDUSTRY_NAME_MAP
import pandas as pd

# 模拟行业列表数据（来自akshare的典型结构）
MOCK_INDUSTRY_LIST = pd.DataFrame({
    '板块名称': [
        '半导体', '新能源', '医药生物', '食品饮料', '电子',
        '软件开发', '互联网服务', '通信设备', '银行', '证券',
        '房地产开发', '建筑', '有色', '化工', '汽车',
        '电力', '国防军工', '文化传媒', '环境保护', '纺织',
        '计算机应用', '保险', '白酒', '钢铁', '煤炭'
    ],
    '涨跌幅': [5.2, 3.1, -1.2, 0.8, 2.5, 4.1, 3.8, 1.2, 0.5, 1.8,
              -0.5, 1.1, 2.3, -0.8, 1.5, 0.3, 2.8, 1.9, 0.7, -0.3,
              3.2, 0.4, 2.1, -1.5, 0.9]
})

# 预设行业列表
PRESET_INDUSTRIES = [
    "半导体", "新能源", "医药生物", "食品饮料", "电子元件",
    "软件服务", "互联网", "通信设备", "银行", "证券",
    "房地产", "建筑工程", "有色金属", "化工行业", "汽车整车",
    "电力行业", "军工", "传媒", "环保", "纺织服装"
]


def match_industry_name(industry_name: str, industry_list_df: pd.DataFrame) -> str:
    """
    模拟行业名称匹配逻辑（来自data_fetcher.py）
    """
    df = industry_list_df
    
    if df.empty:
        return industry_name
    
    if '板块名称' not in df.columns:
        return industry_name
    
    # 1. 精确匹配
    exact_match = df[df['板块名称'] == industry_name]
    if not exact_match.empty:
        return exact_match.iloc[0]['板块名称']
    
    # 2. 使用预定义映射
    if industry_name in INDUSTRY_NAME_MAP:
        mapped_name = INDUSTRY_NAME_MAP[industry_name]
        mapped_match = df[df['板块名称'] == mapped_name]
        if not mapped_match.empty:
            return mapped_name
    
    # 3. 模糊匹配
    fuzzy_match = df[df['板块名称'].str.contains(industry_name, na=False)]
    if not fuzzy_match.empty:
        return fuzzy_match.sort_values('板块名称').iloc[0]['板块名称']
    
    # 4. 反向匹配
    for _, row in df.iterrows():
        if row['板块名称'] and industry_name in str(row['板块名称']):
            return row['板块名称']
    
    return industry_name


def test_industry_matching():
    """测试行业名称匹配"""
    print("="*70)
    print("AlphaLens Pro - 行业数据获取逻辑验证")
    print("="*70)
    
    print(f"\n模拟行业列表包含 {len(MOCK_INDUSTRY_LIST)} 个行业")
    print(f"预设行业数量: {len(PRESET_INDUSTRIES)}")
    print("-"*70)
    
    results = {
        "success": [],
        "failed": [],
        "mapped": []
    }
    
    for i, industry in enumerate(PRESET_INDUSTRIES, 1):
        matched = match_industry_name(industry, MOCK_INDUSTRY_LIST)
        
        if matched in MOCK_INDUSTRY_LIST['板块名称'].values:
            status = "✓"
            results["success"].append(industry)
            if matched != industry:
                results["mapped"].append((industry, matched))
                map_info = f" -> {matched}"
            else:
                map_info = ""
        else:
            status = "✗"
            results["failed"].append(industry)
            map_info = " (未找到)"
        
        print(f"[{i:2d}/20] [{status}] {industry:<12}{map_info}")
    
    # 汇总
    print("\n" + "="*70)
    print("验证结果汇总")
    print("="*70)
    print(f"总行业数: {len(PRESET_INDUSTRIES)}")
    print(f"匹配成功: {len(results['success'])} ({len(results['success'])/20*100:.0f}%)")
    print(f"匹配失败: {len(results['failed'])} ({len(results['failed'])/20*100:.0f}%)")
    print(f"名称映射: {len(results['mapped'])}")
    
    if results["mapped"]:
        print("\n名称映射详情:")
        for orig, mapped in results["mapped"]:
            print(f"  {orig:<12} -> {mapped}")
    
    if results["failed"]:
        print("\n匹配失败的行业:")
        for industry in results["failed"]:
            print(f"  [✗] {industry}")
    
    return len(results["failed"]) == 0


def test_mapping_coverage():
    """测试映射覆盖率"""
    print("\n\n" + "="*70)
    print("INDUSTRY_NAME_MAP 覆盖率分析")
    print("="*70)
    
    # 检查每个预设行业是否在映射中
    covered = []
    not_covered = []
    
    for industry in PRESET_INDUSTRIES:
        if industry in INDUSTRY_NAME_MAP:
            covered.append(industry)
        else:
            not_covered.append(industry)
    
    print(f"\n有映射: {len(covered)}/20 ({len(covered)/20*100:.0f}%)")
    print(f"无映射: {len(not_covered)}/20 ({len(not_covered)/20*100:.0f}%)")
    
    if not_covered:
        print("\n警告: 以下预设行业没有映射定义:")
        for industry in not_covered:
            print(f"  - {industry}")
    else:
        print("\n✓ 所有预设行业都有映射定义")
    
    # 检查映射目标是否存在于模拟数据中
    print("\n映射目标有效性检查:")
    invalid_targets = []
    for source, target in INDUSTRY_NAME_MAP.items():
        if target not in MOCK_INDUSTRY_LIST['板块名称'].values:
            # 检查是否是自映射（如"银行"->"银行"）
            if source != target:
                invalid_targets.append((source, target))
    
    if invalid_targets:
        print("  警告: 以下映射目标不在行业列表中:")
        for source, target in invalid_targets:
            print(f"    {source} -> {target}")
    else:
        print("  ✓ 所有映射目标都有效")
    
    return len(not_covered) == 0


if __name__ == "__main__":
    success1 = test_industry_matching()
    success2 = test_mapping_coverage()
    
    print("\n" + "="*70)
    if success1 and success2:
        print("✓ 所有测试通过！预设行业都能正确获取数据。")
    else:
        print("✗ 部分测试失败，请检查映射配置。")
    print("="*70)
