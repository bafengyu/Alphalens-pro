"""
验证预设行业名称映射（无需网络）
"""

from alphalens.data_fetcher import INDUSTRY_NAME_MAP

# 预设行业列表（来自app.py中的常用行业）
preset_industries = [
    "半导体", "新能源", "医药生物", "食品饮料", "电子元件",
    "软件服务", "互联网", "通信设备", "银行", "证券",
    "房地产", "建筑工程", "有色金属", "化工行业", "汽车整车",
    "电力行业", "军工", "传媒", "环保", "纺织服装"
]

print("="*70)
print("AlphaLens Pro - 预设行业名称映射验证")
print("="*70)

print(f"\n预设行业数量: {len(preset_industries)}")
print(f"已定义映射数量: {len(INDUSTRY_NAME_MAP)}")

print("\n" + "-"*70)
print("行业名称映射检查:")
print("-"*70)

mapped = []
not_mapped = []

for industry in preset_industries:
    if industry in INDUSTRY_NAME_MAP:
        mapped.append((industry, INDUSTRY_NAME_MAP[industry]))
        print(f"[✓] {industry:<12} -> {INDUSTRY_NAME_MAP[industry]}")
    else:
        not_mapped.append(industry)
        print(f"[○] {industry:<12} (无映射，将尝试精确匹配)")

print("\n" + "="*70)
print("验证结果:")
print("="*70)
print(f"有映射的行业: {len(mapped)}/{len(preset_industries)}")
print(f"无映射的行业: {len(not_mapped)}/{len(preset_industries)}")

if not_mapped:
    print("\n建议添加以下映射:")
    for industry in not_mapped:
        # 尝试给出建议映射
        suggestions = {
            "医药生物": "医疗服务",
            "食品饮料": "食品",
            "电子元件": "电子",
            "互联网": "互联网服务",
            "通信设备": "通信",
            "房地产": "房地产开发",
            "建筑工程": "建筑",
            "有色金属": "有色",
            "化工行业": "化工",
            "汽车整车": "汽车",
            "电力行业": "电力",
            "军工": "国防军工",
            "传媒": "文化传媒",
            "环保": "环境保护",
            "纺织服装": "纺织"
        }
        suggestion = suggestions.get(industry, "需确认")
        print(f'    "{industry}": "{suggestion}",')

print("\n" + "="*70)
print("当前所有定义的映射:")
print("="*70)
for k, v in sorted(INDUSTRY_NAME_MAP.items()):
    print(f"  {k:<15} -> {v}")
