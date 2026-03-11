"""
测试 akshare 数据源有效性
"""

import sys
sys.path.insert(0, 'src')
import akshare as ak

print("="*60)
print("AlphaLens Pro - 数据源有效性检查")
print("="*60)

# 测试1: 行业列表
print("\n1. 测试行业列表接口 (stock_board_industry_name_em)")
try:
    df = ak.stock_board_industry_name_em()
    print(f"   状态: 成功")
    print(f"   数量: {len(df)} 个行业")
    if len(df) > 0:
        print(f"   示例: {df.iloc[0]['板块名称']}")
        print(f"   列名: {list(df.columns)}")
except Exception as e:
    print(f"   状态: 失败")
    print(f"   错误: {str(e)[:100]}")

# 测试2: 行业日线
print("\n2. 测试行业日线接口 (stock_board_industry_hist_em)")
try:
    df = ak.stock_board_industry_hist_em(symbol="半导体")
    print(f"   状态: 成功")
    print(f"   数量: {len(df)} 条数据")
    if len(df) > 0:
        print(f"   列名: {list(df.columns)}")
except Exception as e:
    print(f"   状态: 失败")
    print(f"   错误: {str(e)[:100]}")

# 测试3: ETF列表
print("\n3. 测试ETF列表接口 (fund_etf_spot_em)")
try:
    df = ak.fund_etf_spot_em()
    print(f"   状态: 成功")
    print(f"   数量: {len(df)} 只ETF")
    if len(df) > 0:
        print(f"   列名: {list(df.columns)[:5]}...")
except Exception as e:
    print(f"   状态: 失败")
    print(f"   错误: {str(e)[:100]}")

# 测试4: 行业成分股
print("\n4. 测试行业成分股接口 (stock_board_industry_cons_em)")
try:
    df = ak.stock_board_industry_cons_em(symbol="半导体")
    print(f"   状态: 成功")
    print(f"   数量: {len(df)} 只股票")
    if len(df) > 0:
        print(f"   列名: {list(df.columns)[:5]}...")
except Exception as e:
    print(f"   状态: 失败")
    print(f"   错误: {str(e)[:100]}")

# 测试5: 资金流向
print("\n5. 测试资金流向接口 (stock_fund_flow_industry)")
try:
    df = ak.stock_fund_flow_industry(symbol="半导体")
    print(f"   状态: 成功")
    print(f"   数量: {len(df)} 条数据")
except Exception as e:
    print(f"   状态: 失败")
    print(f"   错误: {str(e)[:100]}")

print("\n" + "="*60)
print("检查完成")
print("="*60)
